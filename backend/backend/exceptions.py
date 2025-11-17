"""
Custom Exception Handlers
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger('api')


def custom_exception_handler(exc, context):
    """
    Custom exception handler for DRF that adds additional logging
    and standardized error responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception
    request = context.get('request')
    if request:
        logger.error('API Exception', extra={
            'exception': str(exc),
            'exception_type': type(exc).__name__,
            'path': request.path,
            'method': request.method,
            'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
        }, exc_info=True)
    
    # If response is None, it's an unhandled exception
    if response is None:
        return Response(
            {
                'error': 'Internal server error',
                'detail': str(exc) if hasattr(exc, 'detail') else 'An unexpected error occurred',
                'type': type(exc).__name__,
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Add custom fields to error response
    if hasattr(exc, 'status_code'):
        response.data['status_code'] = exc.status_code
    
    if hasattr(exc, 'default_code'):
        response.data['error_code'] = exc.default_code
    
    return response


class QuotaExceededException(Exception):
    """Raised when user exceeds their subscription quota"""
    def __init__(self, quota_type, message="Quota exceeded"):
        self.quota_type = quota_type
        self.message = message
        super().__init__(self.message)


class SubscriptionRequiredException(Exception):
    """Raised when feature requires active subscription"""
    def __init__(self, feature, message="Active subscription required"):
        self.feature = feature
        self.message = message
        super().__init__(self.message)
