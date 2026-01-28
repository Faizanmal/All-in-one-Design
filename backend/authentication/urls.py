"""
URL configuration for authentication app
Multi-provider OAuth support: Google, GitHub, Firebase
"""
from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    # Google OAuth
    path('oauth/google/', views.google_oauth_start, name='google-oauth-start'),
    path('oauth/google/callback/', views.google_oauth_callback, name='google-oauth-callback'),
    
    # GitHub OAuth
    path('oauth/github/', views.github_oauth_start, name='github-oauth-start'),
    path('oauth/github/callback/', views.github_oauth_callback, name='github-oauth-callback'),
    
    # Firebase Auth
    path('oauth/firebase/verify/', views.firebase_auth_verify, name='firebase-auth-verify'),
    
    # OAuth Connection Management
    path('oauth/connections/', views.list_oauth_connections, name='list-oauth-connections'),
    path('oauth/disconnect/<str:provider>/', views.disconnect_oauth, name='disconnect-oauth'),
    
    # Security
    path('security/profile/', views.get_security_profile, name='security-profile'),
    path('security/login-history/', views.get_login_history, name='login-history'),
]
