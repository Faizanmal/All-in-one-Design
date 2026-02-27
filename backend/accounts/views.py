from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger('accounts')


@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user and return an authentication token.
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = Response(status=200)
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'Content-Type, Authorization')
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'
        return response
    
    logger.info("Registration request received")
    
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Validate required fields
    if not username or not email or not password:
        logger.warning("Registration failed: missing required fields")
        return Response(
            {'error': 'Username, email, and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if username already exists
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Username already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if email already exists
    if User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate password
    try:
        validate_password(password, user=None)
    except ValidationError as e:
        error_list = list(e.messages)
        logger.warning(f"Password validation failed: {error_list}")
        # Return all password validation errors for better user experience
        return Response(
            {
                'error': 'Password does not meet requirements',
                'password_errors': error_list,
                'requirements': [
                    'At least 8 characters long',
                    'Cannot be too similar to personal information',
                    'Cannot be a commonly used password',
                    'Cannot be entirely numeric'
                ]
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create user
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Create authentication token
        token, created = Token.objects.get_or_create(user=user)
        
        logger.info(f"User registered successfully: {user.id}")
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response(
            {'error': 'Registration failed. Please try again.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user and return authentication token.
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = Response(status=200)
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'Content-Type, Authorization')
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'
        return response
    
    from django.contrib.auth import authenticate
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    })


@api_view(['GET', 'OPTIONS'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    Get current authenticated user's information.
    """
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        response = Response(status=200)
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'Content-Type, Authorization')
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'
        return response

    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'name': f"{user.first_name} {user.last_name}".strip() or user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    })
