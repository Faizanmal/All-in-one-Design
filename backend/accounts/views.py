from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    UserProfile, UserPreferences, EmailVerificationToken,
    PasswordResetToken, LoginAttempt, AuditLog
)
from .serializers import (
    UserProfileSerializer, UserPreferencesSerializer,
    RegisterSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, ChangePasswordSerializer,
    EmailVerificationSerializer, AuditLogSerializer, LoginAttemptSerializer,
)
import logging

logger = logging.getLogger('accounts')


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


def get_tokens_for_user(user):
    """Generate JWT tokens for user"""
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@api_view(['POST', 'OPTIONS'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user and return JWT tokens + send verification email.
    """
    if request.method == 'OPTIONS':
        response = Response(status=200)
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'Content-Type, Authorization')
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'
        return response
    
    logger.info("Registration request received")
    serializer = RegisterSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        data = serializer.validated_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
        )
        
        # Profile and preferences are auto-created via signal
        # Send verification email
        verification_token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timezone.timedelta(hours=24),
        )
        
        try:
            frontend_url = settings.CSRF_TRUSTED_ORIGINS[0] if settings.CSRF_TRUSTED_ORIGINS else 'http://localhost:3000'
            verification_url = f"{frontend_url}/verify-email?token={verification_token.token}"
            send_mail(
                subject='Verify your email - AI Design Tool',
                message=f'Welcome to AI Design Tool!\n\nPlease verify your email by clicking this link:\n{verification_url}\n\nThis link expires in 24 hours.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception as e:
            logger.warning(f"Failed to send verification email: {e}")
        
        # Generate JWT tokens
        tokens = get_tokens_for_user(user)
        
        # Log registration
        AuditLog.log(user, 'register', 'user', user.id, request=request)
        
        # Record login attempt
        LoginAttempt.objects.create(
            user=user,
            username_attempted=user.username,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            success=True,
            provider='email',
        )
        
        logger.info(f"User registered successfully: {user.id}")
        return Response({
            'tokens': tokens,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            },
            'message': 'Registration successful. Please check your email to verify your account.',
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
    Login user and return JWT tokens.
    """
    if request.method == 'OPTIONS':
        response = Response(status=200)
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'Content-Type, Authorization')
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'
        return response
    
    from django.contrib.auth import authenticate
    
    # Support both username and email login
    username_or_email = request.data.get('username') or request.data.get('email', '')
    password = request.data.get('password')
    
    if not username_or_email or not password:
        return Response(
            {'error': 'Username/email and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Try authenticating with username first, then email
    user = authenticate(username=username_or_email, password=password)
    if user is None and '@' in username_or_email:
        try:
            user_obj = User.objects.get(email=username_or_email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass
    
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    if user is None:
        # Record failed attempt
        LoginAttempt.objects.create(
            username_attempted=username_or_email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason='invalid_credentials',
            provider='email',
        )
        
        # Check for brute force (5+ failed attempts in 15 minutes)
        recent_failures = LoginAttempt.objects.filter(
            ip_address=ip_address,
            success=False,
            timestamp__gte=timezone.now() - timezone.timedelta(minutes=15),
        ).count()
        
        if recent_failures >= 5:
            return Response(
                {'error': 'Too many failed login attempts. Please wait 15 minutes before trying again.',
                 'retry_after': 900},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )
        
        return Response(
            {'error': 'Invalid credentials. Please check your username/email and password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Record successful login
    LoginAttempt.objects.create(
        user=user,
        username_attempted=username_or_email,
        ip_address=ip_address,
        user_agent=user_agent,
        success=True,
        provider='email',
    )
    
    # Update last active
    try:
        profile = user.profile
        profile.last_active_at = timezone.now()
        profile.save(update_fields=['last_active_at'])
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=user, last_active_at=timezone.now())
    
    # Generate JWT tokens
    tokens = get_tokens_for_user(user)
    
    # Audit log
    AuditLog.log(user, 'login', request=request)
    
    return Response({
        'tokens': tokens,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'emailVerified': getattr(user, 'profile', None) and user.profile.is_email_verified,
        },
    })


@api_view(['GET', 'PATCH', 'OPTIONS'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """
    GET: Get current authenticated user's information (including profile).
    PATCH: Update user profile.
    """
    if request.method == 'OPTIONS':
        response = Response(status=200)
        response['Access-Control-Allow-Origin'] = request.META.get('HTTP_ORIGIN', '*')
        response['Access-Control-Allow-Methods'] = 'GET, PATCH, OPTIONS'
        response['Access-Control-Allow-Headers'] = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS', 'Content-Type, Authorization')
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Max-Age'] = '86400'
        return response

    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'PATCH':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            AuditLog.log(user, 'profile_update', 'user', user.id, request=request)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # GET
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'name': profile.full_name,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'avatar_url': profile.avatar_url,
        'bio': profile.bio,
        'job_title': profile.job_title,
        'company': profile.company,
        'website': profile.website,
        'location': profile.location,
        'is_email_verified': profile.is_email_verified,
        'is_onboarded': profile.is_onboarded,
        'is_staff': user.is_staff,
        'is_superuser': user.is_superuser,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
        'total_designs_created': profile.total_designs_created,
        'total_ai_requests': profile.total_ai_requests,
        'storage_used_mb': profile.storage_used_mb,
    })


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_preferences(request):
    """GET/PATCH user preferences"""
    prefs, _ = UserPreferences.objects.get_or_create(user=request.user)
    
    if request.method == 'PATCH':
        serializer = UserPreferencesSerializer(prefs, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            AuditLog.log(request.user, 'settings_change', 'preferences', request.user.id, request=request)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserPreferencesSerializer(prefs)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Request a password reset email.
    POST: {"email": "user@example.com"}
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    
    # Always return success to prevent email enumeration
    try:
        user = User.objects.get(email=email)
        
        # Invalidate previous tokens
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new token
        reset_token = PasswordResetToken(
            user=user,
            ip_address=get_client_ip(request),
            expires_at=timezone.now() + timezone.timedelta(hours=1),
        )
        reset_token.save()
        
        # Send email
        frontend_url = settings.CSRF_TRUSTED_ORIGINS[0] if settings.CSRF_TRUSTED_ORIGINS else 'http://localhost:3000'
        reset_url = f"{frontend_url}/reset-password?token={reset_token.token}"
        send_mail(
            subject='Password Reset - AI Design Tool',
            message=f'You requested a password reset.\n\nClick this link to reset your password:\n{reset_url}\n\nThis link expires in 1 hour.\n\nIf you did not request this, please ignore this email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )
        
        AuditLog.log(user, 'password_reset', 'user', user.id, request=request)
    except User.DoesNotExist:
        pass  # Don't reveal if email exists
    
    return Response({
        'message': 'If an account with that email exists, a password reset link has been sent.'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_password_reset(request):
    """
    Confirm password reset with token.
    POST: {"token": "...", "new_password": "..."}
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        reset_token = PasswordResetToken.objects.get(
            token=serializer.validated_data['token'],
            is_used=False,
        )
    except PasswordResetToken.DoesNotExist:
        return Response(
            {'error': 'Invalid or expired reset token.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if reset_token.is_expired:
        return Response(
            {'error': 'This reset link has expired. Please request a new one.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = reset_token.user
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    reset_token.is_used = True
    reset_token.save()
    
    AuditLog.log(user, 'password_change', 'user', user.id, request=request)
    
    return Response({'message': 'Password has been reset successfully.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change password for authenticated user.
    POST: {"current_password": "...", "new_password": "..."}
    """
    serializer = ChangePasswordSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    if not user.check_password(serializer.validated_data['current_password']):
        return Response(
            {'error': 'Current password is incorrect.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user.set_password(serializer.validated_data['new_password'])
    user.save()
    
    AuditLog.log(user, 'password_change', 'user', user.id, request=request)
    
    # Generate new tokens since password changed
    tokens = get_tokens_for_user(user)
    
    return Response({
        'message': 'Password changed successfully.',
        'tokens': tokens,
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email(request):
    """
    Verify email address with token.
    POST: {"token": "uuid"}
    """
    serializer = EmailVerificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        verification = EmailVerificationToken.objects.get(
            token=serializer.validated_data['token'],
            is_used=False,
        )
    except EmailVerificationToken.DoesNotExist:
        return Response(
            {'error': 'Invalid or already used verification token.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if verification.is_expired:
        return Response(
            {'error': 'Verification link has expired. Please request a new one.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify the email
    user = verification.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.is_email_verified = True
    profile.save()
    
    verification.is_used = True
    verification.save()
    
    AuditLog.log(user, 'email_verify', 'user', user.id, request=request)
    
    return Response({'message': 'Email verified successfully.'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def resend_verification_email(request):
    """Resend email verification link"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    if profile.is_email_verified:
        return Response({'message': 'Email is already verified.'})
    
    # Invalidate old tokens
    EmailVerificationToken.objects.filter(user=user, is_used=False).update(is_used=True)
    
    # Create new token
    verification_token = EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timezone.timedelta(hours=24),
    )
    
    frontend_url = settings.CSRF_TRUSTED_ORIGINS[0] if settings.CSRF_TRUSTED_ORIGINS else 'http://localhost:3000'
    verification_url = f"{frontend_url}/verify-email?token={verification_token.token}"
    
    send_mail(
        subject='Verify your email - AI Design Tool',
        message=f'Please verify your email by clicking this link:\n{verification_url}\n\nThis link expires in 24 hours.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )
    
    return Response({'message': 'Verification email sent.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_login_history(request):
    """Get user's login history (last 50 attempts)"""
    attempts = LoginAttempt.objects.filter(user=request.user)[:50]
    serializer = LoginAttemptSerializer(attempts, many=True)
    return Response({'login_history': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_audit_logs(request):
    """Get user's audit log (last 100 entries)"""
    logs = AuditLog.objects.filter(user=request.user)[:100]
    serializer = AuditLogSerializer(logs, many=True)
    return Response({'audit_logs': serializer.data})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_onboarding(request):
    """Mark user onboarding as complete and save preferences"""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    profile.is_onboarded = True
    
    # Optionally update display name
    if request.data.get('display_name'):
        profile.display_name = request.data['display_name']
    if request.data.get('job_title'):
        profile.job_title = request.data['job_title']
    if request.data.get('company'):
        profile.company = request.data['company']
    
    profile.save()
    
    # Update preferences if provided
    if request.data.get('preferences'):
        prefs, _ = UserPreferences.objects.get_or_create(user=request.user)
        pref_data = request.data['preferences']
        for key, value in pref_data.items():
            if hasattr(prefs, key):
                setattr(prefs, key, value)
        prefs.save()
    
    return Response({'message': 'Onboarding completed successfully.'})
