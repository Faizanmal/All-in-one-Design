"""
OAuth Authentication Views for Multi-Provider Support
Supports Google OAuth, GitHub OAuth, and Firebase Authentication
"""
import logging
import requests
from urllib.parse import urlencode
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    OAuthConnection, OAuthState, OAuthProvider,
    LoginAttempt, UserSecurityProfile, SecurityAuditLog
)

User = get_user_model()
logger = logging.getLogger('security')


class AuthRateThrottle(AnonRateThrottle):
    """Custom rate throttle for authentication endpoints"""
    rate = '5/minute'


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def create_tokens_for_user(user):
    """Create JWT tokens for a user"""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


def log_login_attempt(email, ip_address, user_agent, success, failure_reason=None, provider=None):
    """Log a login attempt for security monitoring"""
    LoginAttempt.objects.create(
        email=email,
        ip_address=ip_address,
        user_agent=user_agent,
        success=success,
        failure_reason=failure_reason,
        provider=provider,
    )


# ===================== GOOGLE OAUTH =====================

@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def google_oauth_start(request):
    """
    Initiate Google OAuth flow
    Returns the Google authorization URL
    """
    try:
        # Prefer an explicitly configured redirect URI (useful for Docker / prod); fall back to request host
        redirect_uri = getattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', '') or request.build_absolute_uri('/api/v1/auth/oauth/google/callback/')
        
        # Create OAuth state for CSRF protection
        oauth_state = OAuthState.create_state(
            provider=OAuthProvider.GOOGLE,
            redirect_uri=redirect_uri,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        # Build Google authorization URL
        params = {
            'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': oauth_state.state,
            'nonce': oauth_state.nonce,
            'access_type': 'offline',
            'prompt': 'consent',
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        
        return Response({
            'authorization_url': auth_url,
            'state': oauth_state.state,
        })
        
    except Exception as e:
        logger.error(f"Google OAuth start error: {str(e)}")
        return Response(
            {'error': 'Failed to initiate Google OAuth'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def google_oauth_callback(request):
    """
    Handle Google OAuth callback
    Exchange authorization code for tokens and create/login user
    """
    code = request.GET.get('code') or request.data.get('code')
    state = request.GET.get('state') or request.data.get('state')
    error = request.GET.get('error')
    
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # If Google redirected the browser to the API callback but the configured redirect URI
    # is the frontend SPA, forward the browser to the SPA callback (preserve query string).
    configured_redirect = getattr(settings, 'GOOGLE_OAUTH_REDIRECT_URI', '') or ''
    backend_callback = request.build_absolute_uri('/api/v1/auth/oauth/google/callback/')
    if request.method == 'GET' and configured_redirect and configured_redirect != backend_callback:
        qs = request.META.get('QUERY_STRING', '')
        target = configured_redirect + (f'?{qs}' if qs else '')
        return redirect(target)
    
    if error:
        logger.warning(f"Google OAuth error: {error}")
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    
    if not code or not state:
        return Response(
            {'error': 'Missing code or state parameter'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Validate state
        try:
            oauth_state = OAuthState.objects.get(
                state=state,
                provider=OAuthProvider.GOOGLE,
                used=False
            )
        except OAuthState.DoesNotExist:
            logger.warning(f"Invalid OAuth state from IP: {ip_address}")
            return Response(
                {'error': 'Invalid or expired state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if oauth_state.is_expired():
            oauth_state.delete()
            return Response(
                {'error': 'OAuth state expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        oauth_state.mark_used()
        
        # Exchange code for tokens
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': settings.GOOGLE_OAUTH_CLIENT_ID,
                'client_secret': settings.GOOGLE_OAUTH_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': oauth_state.redirect_uri,
            },
            timeout=10
        )
        
        if not token_response.ok:
            logger.error(f"Google token exchange failed: {token_response.text}")
            return Response(
                {'error': 'Failed to exchange authorization code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        # Get user info from Google
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if not user_info_response.ok:
            logger.error(f"Google user info failed: {user_info_response.text}")
            return Response(
                {'error': 'Failed to get user information'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_info = user_info_response.json()
        google_id = user_info.get('id')
        email = user_info.get('email')
        name = user_info.get('name', '')
        
        if not google_id or not email:
            return Response(
                {'error': 'Missing required user information from Google'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': name.split()[0] if name else '',
                'last_name': ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
            }
        )
        
        # Create or update OAuth connection
        oauth_connection, _ = OAuthConnection.objects.update_or_create(
            provider=OAuthProvider.GOOGLE,
            provider_user_id=google_id,
            defaults={
                'user': user,
                'provider_email': email,
                'provider_username': name,
                'profile_data': user_info,
                'last_used_at': timezone.now(),
            }
        )
        
        # Create security profile if not exists
        UserSecurityProfile.objects.get_or_create(user=user)
        
        # Log successful login
        log_login_attempt(email, ip_address, user_agent, True, provider='google')
        SecurityAuditLog.log_event(
            event_type='oauth_login',
            event_category='authentication',
            event_status='success',
            description='Successful Google OAuth login',
            user=user,
            request=request,
        )
        
        # Generate JWT tokens
        tokens = create_tokens_for_user(user)
        
        return Response({
            'tokens': tokens,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'is_new': created,
            }
        })
        
    except Exception as e:
        logger.exception(f"Google OAuth callback error: {str(e)}")
        return Response(
            {'error': 'Authentication failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===================== GITHUB OAUTH =====================

@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def github_oauth_start(request):
    """
    Initiate GitHub OAuth flow
    Returns the GitHub authorization URL
    """
    try:
        # Prefer an explicitly configured redirect URI (useful for Docker / prod); fall back to request host
        redirect_uri = getattr(settings, 'GITHUB_OAUTH_REDIRECT_URI', '') or request.build_absolute_uri('/api/v1/auth/oauth/github/callback/')
        
        # Create OAuth state for CSRF protection
        oauth_state = OAuthState.create_state(
            provider=OAuthProvider.GITHUB,
            redirect_uri=redirect_uri,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )
        
        # Build GitHub authorization URL
        params = {
            'client_id': settings.GITHUB_OAUTH_CLIENT_ID,
            'redirect_uri': redirect_uri,
            'scope': 'user:email read:user',
            'state': oauth_state.state,
        }
        
        auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
        
        return Response({
            'authorization_url': auth_url,
            'state': oauth_state.state,
        })
        
    except Exception as e:
        logger.error(f"GitHub OAuth start error: {str(e)}")
        return Response(
            {'error': 'Failed to initiate GitHub OAuth'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def github_oauth_callback(request):
    """
    Handle GitHub OAuth callback
    Exchange authorization code for tokens and create/login user
    """
    code = request.GET.get('code') or request.data.get('code')
    state = request.GET.get('state') or request.data.get('state')
    error = request.GET.get('error')
    
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')

    # If GitHub redirected the browser to the API callback but the configured redirect URI
    # is the frontend SPA, forward the browser to the SPA callback (preserve query string).
    configured_redirect = getattr(settings, 'GITHUB_OAUTH_REDIRECT_URI', '') or ''
    backend_callback = request.build_absolute_uri('/api/v1/auth/oauth/github/callback/')
    if request.method == 'GET' and configured_redirect and configured_redirect != backend_callback:
        qs = request.META.get('QUERY_STRING', '')
        target = configured_redirect + (f'?{qs}' if qs else '')
        return redirect(target)
    
    if error:
        logger.warning(f"GitHub OAuth error: {error}")
        return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)
    
    if not code or not state:
        return Response(
            {'error': 'Missing code or state parameter'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Validate state
        try:
            oauth_state = OAuthState.objects.get(
                state=state,
                provider=OAuthProvider.GITHUB,
                used=False
            )
        except OAuthState.DoesNotExist:
            logger.warning(f"Invalid OAuth state from IP: {ip_address}")
            return Response(
                {'error': 'Invalid or expired state'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if oauth_state.is_expired():
            oauth_state.delete()
            return Response(
                {'error': 'OAuth state expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        oauth_state.mark_used()
        
        # Exchange code for tokens
        token_response = requests.post(
            'https://github.com/login/oauth/access_token',
            data={
                'client_id': settings.GITHUB_OAUTH_CLIENT_ID,
                'client_secret': settings.GITHUB_OAUTH_CLIENT_SECRET,
                'code': code,
                'redirect_uri': oauth_state.redirect_uri,
            },
            headers={'Accept': 'application/json'},
            timeout=10
        )
        
        if not token_response.ok:
            logger.error(f"GitHub token exchange failed: {token_response.text}")
            return Response(
                {'error': 'Failed to exchange authorization code'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        
        if not access_token:
            return Response(
                {'error': 'No access token received'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user info from GitHub
        user_info_response = requests.get(
            'https://api.github.com/user',
            headers={
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json'
            },
            timeout=10
        )
        
        if not user_info_response.ok:
            logger.error(f"GitHub user info failed: {user_info_response.text}")
            return Response(
                {'error': 'Failed to get user information'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user_info = user_info_response.json()
        github_id = str(user_info.get('id'))
        username = user_info.get('login')
        name = user_info.get('name', username)
        
        # Get primary email from GitHub
        emails_response = requests.get(
            'https://api.github.com/user/emails',
            headers={
                'Authorization': f'token {access_token}',
                'Accept': 'application/vnd.github.v3+json'
            },
            timeout=10
        )
        
        email = None
        if emails_response.ok:
            emails = emails_response.json()
            for e in emails:
                if e.get('primary') and e.get('verified'):
                    email = e.get('email')
                    break
        
        if not email:
            email = user_info.get('email') or f"{username}@github.local"
        
        if not github_id:
            return Response(
                {'error': 'Missing required user information from GitHub'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'first_name': name.split()[0] if name else '',
                'last_name': ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
            }
        )
        
        # Create or update OAuth connection
        oauth_connection, _ = OAuthConnection.objects.update_or_create(
            provider=OAuthProvider.GITHUB,
            provider_user_id=github_id,
            defaults={
                'user': user,
                'provider_email': email,
                'provider_username': username,
                'profile_data': user_info,
                'last_used_at': timezone.now(),
            }
        )
        
        # Create security profile if not exists
        UserSecurityProfile.objects.get_or_create(user=user)
        
        # Log successful login
        log_login_attempt(email, ip_address, user_agent, True, provider='github')
        SecurityAuditLog.log_event(
            event_type='oauth_login',
            event_category='authentication',
            event_status='success',
            description='Successful GitHub OAuth login',
            user=user,
            request=request,
        )
        
        # Generate JWT tokens
        tokens = create_tokens_for_user(user)
        
        return Response({
            'tokens': tokens,
            'user': {
                'id': user.id,
                'email': user.email,
                'username': username,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'is_new': created,
            }
        })
        
    except Exception as e:
        logger.exception(f"GitHub OAuth callback error: {str(e)}")
        return Response(
            {'error': 'Authentication failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===================== FIREBASE AUTH =====================

@api_view(['POST'])
@permission_classes([AllowAny])
@throttle_classes([AuthRateThrottle])
def firebase_auth_verify(request):
    """
    Verify Firebase ID token and create/login user
    """
    id_token = request.data.get('id_token')
    
    if not id_token:
        return Response(
            {'error': 'Missing ID token'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    try:
        # Verify the Firebase ID token
        # Using Google's public keys for verification
        verify_response = requests.get(
            f'https://www.googleapis.com/identitytoolkit/v3/relyingparty/getAccountInfo?key={settings.FIREBASE_API_KEY}',
            json={'idToken': id_token},
            timeout=10
        )
        
        if not verify_response.ok:
            # Try alternative Firebase Admin SDK approach
            # This is a simplified verification - in production, use firebase-admin SDK
            logger.warning("Firebase token verification failed")
            return Response(
                {'error': 'Invalid Firebase token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        firebase_data = verify_response.json()
        users = firebase_data.get('users', [])
        
        if not users:
            return Response(
                {'error': 'No user found for token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        firebase_user = users[0]
        firebase_uid = firebase_user.get('localId')
        email = firebase_user.get('email')
        display_name = firebase_user.get('displayName', '')
        email_verified = firebase_user.get('emailVerified', False)
        
        if not firebase_uid or not email:
            return Response(
                {'error': 'Missing required user information'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'first_name': display_name.split()[0] if display_name else '',
                'last_name': ' '.join(display_name.split()[1:]) if display_name and len(display_name.split()) > 1 else '',
            }
        )
        
        # Create or update OAuth connection
        OAuthConnection.objects.update_or_create(
            provider=OAuthProvider.FIREBASE,
            provider_user_id=firebase_uid,
            defaults={
                'user': user,
                'provider_email': email,
                'provider_username': display_name,
                'profile_data': firebase_user,
                'last_used_at': timezone.now(),
            }
        )
        
        # Create security profile if not exists
        UserSecurityProfile.objects.get_or_create(user=user)
        
        # Log successful login
        log_login_attempt(email, ip_address, user_agent, True, provider='firebase')
        SecurityAuditLog.log_event(
            event_type='firebase_login',
            event_category='authentication',
            event_status='success',
            description='Successful Firebase authentication',
            user=user,
            request=request,
        )
        
        # Generate JWT tokens
        tokens = create_tokens_for_user(user)
        
        return Response({
            'tokens': tokens,
            'user': {
                'id': user.id,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip(),
                'email_verified': email_verified,
                'is_new': created,
            }
        })
        
    except Exception as e:
        logger.exception(f"Firebase auth error: {str(e)}")
        log_login_attempt(
            request.data.get('email', 'unknown'),
            ip_address, user_agent, False,
            failure_reason=str(e),
            provider='firebase'
        )
        return Response(
            {'error': 'Authentication failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# ===================== OAUTH CONNECTION MANAGEMENT =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_oauth_connections(request):
    """
    List all OAuth connections for the current user
    """
    connections = OAuthConnection.objects.filter(user=request.user)
    data = [{
        'id': str(conn.id),
        'provider': conn.provider,
        'provider_email': conn.provider_email,
        'provider_username': conn.provider_username,
        'is_primary': conn.is_primary,
        'created_at': conn.created_at.isoformat(),
        'last_used_at': conn.last_used_at.isoformat() if conn.last_used_at else None,
    } for conn in connections]
    
    return Response({'connections': data})


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def disconnect_oauth(request, provider):
    """
    Disconnect an OAuth provider from the user's account
    """
    try:
        connection = OAuthConnection.objects.get(
            user=request.user,
            provider=provider
        )
        
        # Check if user has a password set before allowing disconnect
        if not request.user.has_usable_password():
            # Count remaining connections
            remaining = OAuthConnection.objects.filter(user=request.user).exclude(id=connection.id).count()
            if remaining == 0:
                return Response(
                    {'error': 'Cannot disconnect the only authentication method. Please set a password first.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        SecurityAuditLog.log_event(
            event_type='oauth_disconnect',
            event_category='security_change',
            event_status='success',
            description=f'Disconnected {provider} OAuth',
            user=request.user,
            request=request,
        )
        
        connection.delete()
        
        return Response({'message': f'{provider} disconnected successfully'})
        
    except OAuthConnection.DoesNotExist:
        return Response(
            {'error': 'OAuth connection not found'},
            status=status.HTTP_404_NOT_FOUND
        )


# ===================== SECURITY ENDPOINTS =====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_security_profile(request):
    """
    Get security profile for the current user
    """
    profile, _ = UserSecurityProfile.objects.get_or_create(user=request.user)
    
    return Response({
        'two_factor_enabled': profile.two_factor_enabled,
        'two_factor_method': profile.two_factor_method,
        'password_changed_at': profile.password_changed_at.isoformat() if profile.password_changed_at else None,
        'last_login_ip': profile.last_login_ip,
        'last_login_at': profile.last_login_at.isoformat() if profile.last_login_at else None,
        'is_locked': profile.is_locked,
        'active_sessions_count': profile.active_sessions_count,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_login_history(request):
    """
    Get login history for the current user
    """
    attempts = LoginAttempt.objects.filter(
        email=request.user.email
    ).order_by('-timestamp')[:50]
    
    data = [{
        'timestamp': attempt.timestamp.isoformat(),
        'ip_address': attempt.ip_address,
        'success': attempt.success,
        'provider': attempt.provider,
        'failure_reason': attempt.failure_reason,
        'country': attempt.country,
        'city': attempt.city,
    } for attempt in attempts]
    
    return Response({'login_history': data})
