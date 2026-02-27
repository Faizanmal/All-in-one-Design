from django.urls import path
from django.http import HttpResponse
from . import views

def cors_options(request):
    """Handle CORS preflight requests"""
    response = HttpResponse(status=200)
    response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
    response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD'
    response['Access-Control-Allow-Headers'] = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'Content-Type, Authorization')
    response['Access-Control-Allow-Credentials'] = 'true'
    response['Access-Control-Max-Age'] = '86400'
    return response

urlpatterns = [
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('users/me/', views.get_current_user, name='current-user'),
    
    # Password management
    path('password/reset/', views.request_password_reset, name='password-reset-request'),
    path('password/reset/confirm/', views.confirm_password_reset, name='password-reset-confirm'),
    path('password/change/', views.change_password, name='password-change'),
    
    # Email verification
    path('email/verify/', views.verify_email, name='email-verify'),
    path('email/resend-verification/', views.resend_verification_email, name='email-resend-verify'),
    
    # User preferences
    path('preferences/', views.user_preferences, name='user-preferences'),
    
    # Onboarding
    path('onboarding/complete/', views.complete_onboarding, name='complete-onboarding'),
    
    # Security
    path('security/login-history/', views.get_login_history, name='login-history'),
    path('security/audit-logs/', views.get_audit_logs, name='audit-logs'),
]
