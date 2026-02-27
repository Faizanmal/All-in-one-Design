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
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('users/me/', views.get_current_user, name='current-user'),
]
