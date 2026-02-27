"""
Comprehensive Input Validation and Sanitization Utilities
Implements OWASP-compliant security measures
"""
import re
import html
import unicodedata
from typing import Any, Dict, List
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, URLValidator
from rest_framework import serializers


# ===================== EMAIL VALIDATION =====================

class SecureEmailValidator(EmailValidator):
    """Enhanced email validator with additional security checks"""
    
    # Disposable email domains to block
    DISPOSABLE_DOMAINS = {
        'tempmail.com', 'throwaway.email', '10minutemail.com',
        'guerrillamail.com', 'mailinator.com', 'yopmail.com',
        'temp-mail.org', 'fakeinbox.com', 'trashmail.com',
    }
    
    def __call__(self, value):
        super().__call__(value)
        
        # Additional checks
        value = value.lower().strip()
        
        # Check for disposable domains
        domain = value.split('@')[-1]
        if domain in self.DISPOSABLE_DOMAINS:
            raise ValidationError(
                'Disposable email addresses are not allowed',
                code='disposable_email'
            )
        
        # Check for suspicious patterns
        local_part = value.split('@')[0]
        if self._is_suspicious_local_part(local_part):
            raise ValidationError(
                'Invalid email format',
                code='suspicious_email'
            )
    
    def _is_suspicious_local_part(self, local_part):
        """Check for suspicious local part patterns"""
        # Too many consecutive dots or special chars
        if re.search(r'\.{2,}', local_part):
            return True
        # Starts or ends with special char
        if local_part[0] in '._-' or local_part[-1] in '._-':
            return True
        return False


# ===================== PASSWORD VALIDATION =====================

class PasswordStrengthValidator:
    """
    Comprehensive password strength validator
    Implements NIST guidelines and security best practices
    """
    
    # Common password patterns to reject
    COMMON_PATTERNS = [
        r'123456', r'password', r'qwerty', r'abc123',
        r'letmein', r'welcome', r'admin', r'login',
    ]
    
    # Keyboard patterns
    KEYBOARD_PATTERNS = [
        'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
        '1234567890', '0987654321',
    ]
    
    def __init__(
        self,
        min_length: int = 12,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digit: bool = True,
        require_special: bool = True,
        max_length: int = 128,
    ):
        self.min_length = min_length
        self.max_length = max_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digit = require_digit
        self.require_special = require_special
    
    def validate(self, password: str, user=None) -> List[str]:
        """
        Validate password strength
        Returns list of validation errors
        """
        errors = []
        
        if not password:
            return ['Password is required']
        
        # Length checks
        if len(password) < self.min_length:
            errors.append(f'Password must be at least {self.min_length} characters')
        
        if len(password) > self.max_length:
            errors.append(f'Password cannot exceed {self.max_length} characters')
        
        # Character class requirements
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append('Password must contain at least one uppercase letter')
        
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append('Password must contain at least one lowercase letter')
        
        if self.require_digit and not re.search(r'\d', password):
            errors.append('Password must contain at least one digit')
        
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append('Password must contain at least one special character')
        
        # Check for common patterns
        password_lower = password.lower()
        for pattern in self.COMMON_PATTERNS:
            if pattern in password_lower:
                errors.append('Password contains a common pattern')
                break
        
        # Check for keyboard patterns
        for pattern in self.KEYBOARD_PATTERNS:
            if pattern in password_lower or pattern[::-1] in password_lower:
                errors.append('Password contains a keyboard pattern')
                break
        
        # Check for user-related info
        if user:
            user_info = [
                getattr(user, 'username', ''),
                getattr(user, 'email', '').split('@')[0],
                getattr(user, 'first_name', ''),
                getattr(user, 'last_name', ''),
            ]
            for info in user_info:
                if info and len(info) > 2 and info.lower() in password_lower:
                    errors.append('Password cannot contain personal information')
                    break
        
        # Check for repeated characters
        if re.search(r'(.)\1{3,}', password):
            errors.append('Password cannot contain more than 3 repeated characters')
        
        return errors
    
    def get_password_strength(self, password: str) -> Dict[str, Any]:
        """
        Calculate password strength score
        Returns score (0-100) and feedback
        """
        score = 0
        feedback = []
        
        if not password:
            return {'score': 0, 'strength': 'none', 'feedback': ['Enter a password']}
        
        # Length score (up to 30 points)
        length_score = min(len(password) * 2, 30)
        score += length_score
        
        # Character variety (up to 40 points)
        variety_score = 0
        if re.search(r'[a-z]', password):
            variety_score += 10
        if re.search(r'[A-Z]', password):
            variety_score += 10
        if re.search(r'\d', password):
            variety_score += 10
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            variety_score += 10
        score += variety_score
        
        # Bonus for no common patterns (up to 20 points)
        pattern_penalty = 0
        password_lower = password.lower()
        for pattern in self.COMMON_PATTERNS + self.KEYBOARD_PATTERNS:
            if pattern in password_lower:
                pattern_penalty += 10
        score += max(0, 20 - pattern_penalty)
        
        # Entropy bonus (up to 10 points)
        unique_chars = len(set(password))
        entropy_score = min(unique_chars, 10)
        score += entropy_score
        
        # Determine strength category
        if score < 30:
            strength = 'weak'
            feedback.append('Consider using a longer password with more variety')
        elif score < 50:
            strength = 'fair'
            feedback.append('Add more character types for better security')
        elif score < 70:
            strength = 'good'
            feedback.append('Password is reasonably strong')
        elif score < 90:
            strength = 'strong'
            feedback.append('Password is strong')
        else:
            strength = 'excellent'
            feedback.append('Password is excellent')
        
        return {
            'score': min(score, 100),
            'strength': strength,
            'feedback': feedback,
        }


# ===================== INPUT SANITIZATION =====================

class InputSanitizer:
    """
    Comprehensive input sanitization for XSS and injection prevention
    """
    
    # HTML entities to escape
    HTML_ESCAPE_MAP = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#x27;',
        '/': '&#x2F;',
        '`': '&#x60;',
        '=': '&#x3D;',
    }
    
    # SQL injection patterns
    SQL_PATTERNS = [
        r"(\%27)|(\')|(\-\-)|(\%23)|(#)",
        r"((\%3D)|(=))[^\n]*((\%27)|(\')|(\-\-)|(\%3B)|(;))",
        r"((\%27)|(\'))union",
        r"exec(\s|\+)+(s|x)p\w+",
        r"insert\s+into",
        r"select\s+.*\s+from",
        r"delete\s+from",
        r"drop\s+table",
        r"update\s+.*\s+set",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript\s*:",
        r"on\w+\s*=\s*['\"]",
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<link[^>]*>",
        r"<meta[^>]*>",
        r"expression\s*\(",
        r"vbscript\s*:",
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = None) -> str:
        """
        Sanitize a string input
        - HTML escape special characters
        - Remove null bytes
        - Normalize unicode
        - Trim whitespace
        """
        if not value:
            return ''
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Normalize unicode
        value = unicodedata.normalize('NFKC', value)
        
        # HTML escape
        value = html.escape(value, quote=True)
        
        # Trim whitespace
        value = value.strip()
        
        # Apply max length
        if max_length and len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @classmethod
    def sanitize_html(cls, value: str) -> str:
        """
        Sanitize HTML content - strips all tags
        Use a library like bleach for allowing safe tags
        """
        if not value:
            return ''
        
        # Remove all HTML tags
        value = re.sub(r'<[^>]+>', '', value)
        
        # Remove script-related patterns
        for pattern in cls.XSS_PATTERNS:
            value = re.sub(pattern, '', value, flags=re.IGNORECASE)
        
        return cls.sanitize_string(value)
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and injection
        """
        if not filename:
            return ''
        
        # Remove path components
        filename = filename.replace('\\', '/').split('/')[-1]
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Limit length
        name, ext = (filename.rsplit('.', 1) + [''])[:2]
        name = name[:200]
        ext = ext[:10]
        
        return f"{name}.{ext}" if ext else name
    
    @classmethod
    def sanitize_json(cls, data: Any) -> Any:
        """
        Recursively sanitize JSON data
        """
        if isinstance(data, str):
            return cls.sanitize_string(data)
        elif isinstance(data, dict):
            return {k: cls.sanitize_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.sanitize_json(item) for item in data]
        else:
            return data
    
    @classmethod
    def check_sql_injection(cls, value: str) -> bool:
        """
        Check if value contains SQL injection patterns
        Returns True if suspicious
        """
        if not value:
            return False
        
        value_lower = value.lower()
        for pattern in cls.SQL_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        return False
    
    @classmethod
    def check_xss(cls, value: str) -> bool:
        """
        Check if value contains XSS patterns
        Returns True if suspicious
        """
        if not value:
            return False
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                return True
        return False


# ===================== URL VALIDATION =====================

class SecureURLValidator(URLValidator):
    """Enhanced URL validator with security checks"""
    
    # Blocked schemes
    BLOCKED_SCHEMES = ['javascript', 'data', 'vbscript', 'file']
    
    # Blocked hosts (internal networks)
    BLOCKED_HOSTS = [
        'localhost', '127.0.0.1', '0.0.0.0',
        '10.', '172.16.', '172.17.', '172.18.', '172.19.',
        '172.20.', '172.21.', '172.22.', '172.23.', '172.24.',
        '172.25.', '172.26.', '172.27.', '172.28.', '172.29.',
        '172.30.', '172.31.', '192.168.', '169.254.',
    ]
    
    def __call__(self, value):
        # First, standard validation
        super().__call__(value)
        
        value_lower = value.lower()
        
        # Check for blocked schemes
        for scheme in self.BLOCKED_SCHEMES:
            if value_lower.startswith(f'{scheme}:'):
                raise ValidationError(
                    f'URL scheme "{scheme}" is not allowed',
                    code='blocked_scheme'
                )
        
        # Extract and check host
        try:
            from urllib.parse import urlparse
            parsed = urlparse(value)
            host = parsed.netloc.lower()
            
            # Remove port
            host = host.split(':')[0]
            
            for blocked in self.BLOCKED_HOSTS:
                if host == blocked or host.startswith(blocked):
                    raise ValidationError(
                        'URLs pointing to internal networks are not allowed',
                        code='internal_url'
                    )
        except Exception:
            pass


# ===================== SERIALIZER FIELDS =====================

class SanitizedCharField(serializers.CharField):
    """CharField with automatic sanitization"""
    
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return InputSanitizer.sanitize_string(value, max_length=self.max_length)


class SanitizedEmailField(serializers.EmailField):
    """EmailField with enhanced validation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validators.append(SecureEmailValidator())
    
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        return value.lower().strip()


class SecureURLField(serializers.URLField):
    """URLField with security validation"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validators = [SecureURLValidator()]


class SecurePasswordField(serializers.CharField):
    """Password field with strength validation"""
    
    def __init__(self, **kwargs):
        kwargs.setdefault('write_only', True)
        kwargs.setdefault('min_length', 12)
        kwargs.setdefault('max_length', 128)
        kwargs.setdefault('style', {'input_type': 'password'})
        super().__init__(**kwargs)
        self.password_validator = PasswordStrengthValidator()
    
    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        
        # Validate password strength
        errors = self.password_validator.validate(value)
        if errors:
            raise serializers.ValidationError(errors)
        
        return value


# ===================== VALIDATION HELPERS =====================

def validate_uuid(value: str) -> bool:
    """Validate UUID format"""
    import uuid
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


def validate_json_structure(data: dict, schema: dict) -> List[str]:
    """
    Validate JSON structure against a simple schema
    Schema format: {'field': 'type', 'nested': {'subfield': 'type'}}
    """
    errors = []
    
    for field, expected_type in schema.items():
        if field not in data:
            errors.append(f"Missing required field: {field}")
            continue
        
        value = data[field]
        
        if isinstance(expected_type, dict):
            if not isinstance(value, dict):
                errors.append(f"Field '{field}' must be an object")
            else:
                nested_errors = validate_json_structure(value, expected_type)
                errors.extend([f"{field}.{e}" for e in nested_errors])
        elif expected_type == 'string':
            if not isinstance(value, str):
                errors.append(f"Field '{field}' must be a string")
        elif expected_type == 'number':
            if not isinstance(value, (int, float)):
                errors.append(f"Field '{field}' must be a number")
        elif expected_type == 'boolean':
            if not isinstance(value, bool):
                errors.append(f"Field '{field}' must be a boolean")
        elif expected_type == 'array':
            if not isinstance(value, list):
                errors.append(f"Field '{field}' must be an array")
        elif expected_type == 'email':
            try:
                SecureEmailValidator()(value)
            except ValidationError:
                errors.append(f"Field '{field}' must be a valid email")
        elif expected_type == 'url':
            try:
                SecureURLValidator()(value)
            except ValidationError:
                errors.append(f"Field '{field}' must be a valid URL")
        elif expected_type == 'uuid':
            if not validate_uuid(value):
                errors.append(f"Field '{field}' must be a valid UUID")
    
    return errors
