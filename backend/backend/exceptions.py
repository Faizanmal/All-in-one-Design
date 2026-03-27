"""
Custom Exception Handlers
"""
import uuid
import logging
from rest_framework.response import Response
from rest_framework import status
from drf_standardized_errors.handler import exception_handler as standardized_handler

logger = logging.getLogger('api')


def custom_exception_handler(exc, context):
    """
    RFC-7807 Problem Details API standard handler.
    Wraps drf-standardized-errors to also inject trace IDs and log payloads.
    """
    request = context.get('request')
    trace_id = str(uuid.uuid4())
    
    # Let drf-standardized-errors format it to RFC-7807
    response = standardized_handler(exc, context)
    
    if request:
        logger.error(f'API Exception [Trace ID: {trace_id}]', extra={
            'trace_id': trace_id,
            'exception': str(exc),
            'exception_type': type(exc).__name__,
            'path': request.path,
            'method': request.method,
            'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
        }, exc_info=True)
    
    # If the response was formatted, add our trace_id so the frontend can display it
    if response and isinstance(response.data, dict):
        response.data['trace_id'] = trace_id
    elif response is None:
        # Failsafe if drf-standardized-errors somehow fails
        return Response(
            {
                'type': 'about:blank',
                'title': 'Internal Server Error',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'detail': str(exc) if hasattr(exc, 'detail') else 'An unexpected error occurred',
                'instance': request.path if request else 'unknown',
                'trace_id': trace_id
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
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
