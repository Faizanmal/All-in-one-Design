"""
OAuth Token Refresh Service
Handles OAuth token refresh for external service connections
"""
import logging
import requests
from datetime import timedelta
from typing import Optional, Dict, Any
from django.conf import settings
from django.utils import timezone
from celery import shared_task

logger = logging.getLogger(__name__)


class OAuthProvider:
    """OAuth provider configurations"""
    
    FIGMA = 'figma'
    GOOGLE_DRIVE = 'google_drive'
    DROPBOX = 'dropbox'
    ADOBE_XD = 'adobe_xd'
    GITHUB = 'github'


OAUTH_CONFIGS = {
    OAuthProvider.FIGMA: {
        'token_url': 'https://www.figma.com/api/oauth/refresh',
        'client_id_setting': 'FIGMA_CLIENT_ID',
        'client_secret_setting': 'FIGMA_CLIENT_SECRET',
        'grant_type': 'refresh_token',
    },
    OAuthProvider.GOOGLE_DRIVE: {
        'token_url': 'https://oauth2.googleapis.com/token',
        'client_id_setting': 'GOOGLE_CLIENT_ID',
        'client_secret_setting': 'GOOGLE_CLIENT_SECRET',
        'grant_type': 'refresh_token',
    },
    OAuthProvider.DROPBOX: {
        'token_url': 'https://api.dropboxapi.com/oauth2/token',
        'client_id_setting': 'DROPBOX_CLIENT_ID',
        'client_secret_setting': 'DROPBOX_CLIENT_SECRET',
        'grant_type': 'refresh_token',
    },
    OAuthProvider.ADOBE_XD: {
        'token_url': 'https://ims-na1.adobelogin.com/ims/token/v3',
        'client_id_setting': 'ADOBE_CLIENT_ID',
        'client_secret_setting': 'ADOBE_CLIENT_SECRET',
        'grant_type': 'refresh_token',
    },
    OAuthProvider.GITHUB: {
        'token_url': 'https://github.com/login/oauth/access_token',
        'client_id_setting': 'GITHUB_CLIENT_ID',
        'client_secret_setting': 'GITHUB_CLIENT_SECRET',
        'grant_type': 'refresh_token',
    },
}


class OAuthTokenRefreshService:
    """Service for refreshing OAuth tokens"""
    
    def __init__(self):
        self.timeout = 30
    
    def refresh_token(self, connection) -> Dict[str, Any]:
        """
        Refresh OAuth token for an external service connection
        
        Args:
            connection: ExternalServiceConnection model instance
            
        Returns:
            Dict with success status and new token info or error
        """
        provider = connection.service
        
        if provider not in OAUTH_CONFIGS:
            return {
                'success': False,
                'error': f'Unsupported OAuth provider: {provider}'
            }
        
        config = OAUTH_CONFIGS[provider]
        
        # Get client credentials from settings
        client_id = getattr(settings, config['client_id_setting'], None)
        client_secret = getattr(settings, config['client_secret_setting'], None)
        
        if not client_id or not client_secret:
            logger.error(f"Missing OAuth credentials for {provider}")
            return {
                'success': False,
                'error': f'OAuth credentials not configured for {provider}'
            }
        
        if not connection.refresh_token:
            return {
                'success': False,
                'error': 'No refresh token available'
            }
        
        try:
            # Build refresh request
            data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'refresh_token': connection.refresh_token,
                'grant_type': config['grant_type'],
            }
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Accept': 'application/json',
            }
            
            # Special handling for GitHub
            if provider == OAuthProvider.GITHUB:
                headers['Accept'] = 'application/json'
            
            # Make token refresh request
            response = requests.post(
                config['token_url'],
                data=data,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                token_data = response.json()
                
                # Update connection with new tokens
                connection.access_token = token_data.get('access_token', connection.access_token)
                
                # Update refresh token if a new one is provided
                new_refresh_token = token_data.get('refresh_token')
                if new_refresh_token:
                    connection.refresh_token = new_refresh_token
                
                # Calculate token expiry
                expires_in = token_data.get('expires_in')
                if expires_in:
                    connection.token_expires_at = timezone.now() + timedelta(seconds=int(expires_in))
                
                connection.last_synced = timezone.now()
                connection.save()
                
                logger.info(f"Successfully refreshed OAuth token for {provider} (user: {connection.user_id})")
                
                return {
                    'success': True,
                    'access_token': connection.access_token,
                    'expires_at': connection.token_expires_at.isoformat() if connection.token_expires_at else None,
                }
            
            else:
                error_data = response.json() if response.content else {}
                error_msg = error_data.get('error_description') or error_data.get('error') or 'Token refresh failed'
                
                logger.warning(f"OAuth token refresh failed for {provider}: {error_msg}")
                
                # If refresh token is invalid, mark connection as inactive
                if response.status_code in [400, 401]:
                    connection.is_active = False
                    connection.save()
                
                return {
                    'success': False,
                    'error': error_msg,
                    'status_code': response.status_code
                }
                
        except requests.RequestException as e:
            logger.error(f"OAuth token refresh request failed for {provider}: {str(e)}")
            return {
                'success': False,
                'error': f'Request failed: {str(e)}'
            }
        except Exception as e:
            logger.error(f"Unexpected error during OAuth token refresh for {provider}: {str(e)}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def is_token_expired(self, connection) -> bool:
        """Check if a connection's token is expired or about to expire"""
        if not connection.token_expires_at:
            # Assume expired if no expiry is set
            return True
        
        # Consider token expired if it expires within 5 minutes
        buffer = timedelta(minutes=5)
        return connection.token_expires_at <= timezone.now() + buffer
    
    def get_valid_token(self, connection) -> Optional[str]:
        """
        Get a valid access token, refreshing if necessary
        
        Args:
            connection: ExternalServiceConnection model instance
            
        Returns:
            Valid access token or None if unable to get one
        """
        if not connection.is_active:
            return None
        
        if self.is_token_expired(connection):
            result = self.refresh_token(connection)
            if not result['success']:
                return None
        
        return connection.access_token


# Singleton instance
oauth_service = OAuthTokenRefreshService()


# Celery tasks
@shared_task(bind=True, max_retries=3)
def refresh_oauth_token_task(self, connection_id: int):
    """Celery task to refresh OAuth token"""
    from integrations.models import ExternalServiceConnection
    
    try:
        connection = ExternalServiceConnection.objects.get(id=connection_id)
        result = oauth_service.refresh_token(connection)
        
        if not result['success']:
            logger.warning(f"OAuth refresh failed for connection {connection_id}: {result.get('error')}")
            # Retry for transient failures
            if result.get('status_code', 0) >= 500:
                self.retry(countdown=300)  # Retry in 5 minutes
        
        return result
        
    except ExternalServiceConnection.DoesNotExist:
        logger.error(f"Connection {connection_id} not found for OAuth refresh")
        return {'success': False, 'error': 'Connection not found'}


@shared_task
def refresh_expiring_tokens():
    """
    Periodic task to refresh tokens that are about to expire
    Run this task every hour via Celery Beat
    """
    from integrations.models import ExternalServiceConnection
    
    # Find tokens expiring in the next hour
    expiry_threshold = timezone.now() + timedelta(hours=1)
    
    connections = ExternalServiceConnection.objects.filter(
        is_active=True,
        token_expires_at__lte=expiry_threshold,
        refresh_token__isnull=False
    ).exclude(refresh_token='')
    
    refreshed_count = 0
    failed_count = 0
    
    for connection in connections:
        result = oauth_service.refresh_token(connection)
        if result['success']:
            refreshed_count += 1
        else:
            failed_count += 1
    
    logger.info(f"Token refresh job: {refreshed_count} succeeded, {failed_count} failed")
    return {
        'refreshed': refreshed_count,
        'failed': failed_count,
        'total': connections.count()
    }


@shared_task
def validate_connection_tokens():
    """
    Periodic task to validate all active connections
    Run this task daily via Celery Beat
    """
    from integrations.models import ExternalServiceConnection
    
    connections = ExternalServiceConnection.objects.filter(is_active=True)
    
    validated = 0
    deactivated = 0
    
    for connection in connections:
        try:
            # Try to use the token to validate it
            valid = validate_token(connection)
            if valid:
                validated += 1
            else:
                connection.is_active = False
                connection.save()
                deactivated += 1
        except Exception as e:
            logger.error(f"Error validating connection {connection.id}: {e}")
    
    logger.info(f"Token validation: {validated} valid, {deactivated} deactivated")
    return {
        'validated': validated,
        'deactivated': deactivated
    }


def validate_token(connection) -> bool:
    """Validate an OAuth token by making a test API call"""
    provider = connection.service
    
    validation_endpoints = {
        OAuthProvider.FIGMA: 'https://api.figma.com/v1/me',
        OAuthProvider.GOOGLE_DRIVE: 'https://www.googleapis.com/drive/v3/about?fields=user',
        OAuthProvider.DROPBOX: 'https://api.dropboxapi.com/2/users/get_current_account',
        OAuthProvider.GITHUB: 'https://api.github.com/user',
    }
    
    if provider not in validation_endpoints:
        return True  # Assume valid for unknown providers
    
    try:
        headers = {
            'Authorization': f'Bearer {connection.access_token}'
        }
        
        # Dropbox uses a different auth header format
        if provider == OAuthProvider.DROPBOX:
            response = requests.post(
                validation_endpoints[provider],
                headers=headers,
                timeout=10
            )
        else:
            response = requests.get(
                validation_endpoints[provider],
                headers=headers,
                timeout=10
            )
        
        return response.status_code == 200
        
    except requests.RequestException:
        return False
