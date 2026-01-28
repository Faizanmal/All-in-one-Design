"""
Data Encryption Utilities
AES-256 encryption for sensitive data at rest
Implements industry-standard encryption with key rotation support
"""
import os
import base64
import hashlib
import hmac
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from functools import lru_cache

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('security')


class EncryptionError(Exception):
    """Custom exception for encryption errors"""
    pass


class KeyManager:
    """
    Encryption key management with rotation support
    Keys are derived from master key and version identifier
    """
    
    CACHE_PREFIX = 'encryption_key:'
    KEY_VERSION_PREFIX = 'key_version:'
    
    def __init__(self, master_key: str = None):
        """
        Initialize with master key from settings or environment
        """
        self.master_key = master_key or getattr(
            settings, 'ENCRYPTION_MASTER_KEY',
            os.environ.get('ENCRYPTION_MASTER_KEY', '')
        )
        
        if not self.master_key:
            raise EncryptionError(
                "ENCRYPTION_MASTER_KEY must be set in settings or environment"
            )
        
        self._backend = default_backend()
    
    def derive_key(self, purpose: str, version: int = 1) -> bytes:
        """
        Derive a purpose-specific key using PBKDF2
        
        Args:
            purpose: Key purpose identifier (e.g., 'user_data', 'api_tokens')
            version: Key version for rotation support
        
        Returns:
            32-byte derived key
        """
        cache_key = f"{self.CACHE_PREFIX}{purpose}:{version}"
        cached_key = cache.get(cache_key)
        
        if cached_key:
            return base64.b64decode(cached_key)
        
        # Create salt from purpose and version
        salt = hashlib.sha256(
            f"{purpose}:{version}:{self.master_key[:8]}".encode()
        ).digest()
        
        # Derive key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,  # AES-256
            salt=salt,
            iterations=100000,
            backend=self._backend
        )
        
        key = kdf.derive(self.master_key.encode())
        
        # Cache the derived key
        cache.set(cache_key, base64.b64encode(key).decode(), timeout=3600)
        
        return key
    
    def get_current_version(self, purpose: str) -> int:
        """Get current key version for a purpose"""
        version = cache.get(f"{self.KEY_VERSION_PREFIX}{purpose}")
        return version if version else 1
    
    def rotate_key(self, purpose: str) -> int:
        """
        Rotate to a new key version
        Returns the new version number
        """
        current = self.get_current_version(purpose)
        new_version = current + 1
        cache.set(f"{self.KEY_VERSION_PREFIX}{purpose}", new_version, timeout=None)
        
        logger.info(f"Key rotated for purpose '{purpose}' to version {new_version}")
        
        return new_version


class AESEncryptor:
    """
    AES-256-GCM encryption for data at rest
    Provides authenticated encryption with associated data (AEAD)
    """
    
    NONCE_SIZE = 12  # 96 bits for GCM
    TAG_SIZE = 16    # 128 bits authentication tag
    
    def __init__(self, key: bytes):
        """
        Initialize with a 32-byte key
        """
        if len(key) != 32:
            raise EncryptionError("Key must be 32 bytes for AES-256")
        
        self._aesgcm = AESGCM(key)
    
    def encrypt(self, plaintext: bytes, associated_data: bytes = None) -> bytes:
        """
        Encrypt data using AES-256-GCM
        
        Args:
            plaintext: Data to encrypt
            associated_data: Optional data to authenticate but not encrypt
        
        Returns:
            nonce + ciphertext + tag
        """
        nonce = secrets.token_bytes(self.NONCE_SIZE)
        
        try:
            ciphertext = self._aesgcm.encrypt(
                nonce,
                plaintext,
                associated_data
            )
            return nonce + ciphertext
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            raise EncryptionError("Encryption failed") from e
    
    def decrypt(self, ciphertext: bytes, associated_data: bytes = None) -> bytes:
        """
        Decrypt data using AES-256-GCM
        
        Args:
            ciphertext: nonce + encrypted data + tag
            associated_data: Same data used during encryption
        
        Returns:
            Decrypted plaintext
        """
        if len(ciphertext) < self.NONCE_SIZE + self.TAG_SIZE:
            raise EncryptionError("Invalid ciphertext: too short")
        
        nonce = ciphertext[:self.NONCE_SIZE]
        encrypted = ciphertext[self.NONCE_SIZE:]
        
        try:
            return self._aesgcm.decrypt(nonce, encrypted, associated_data)
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise EncryptionError("Decryption failed - data may be corrupted or tampered") from e


class FieldEncryptor:
    """
    High-level encryption for database fields
    Handles string encoding/decoding and key versioning
    """
    
    VERSION_SEPARATOR = '$'
    
    def __init__(self, purpose: str = 'default'):
        """
        Initialize with a purpose identifier for key derivation
        """
        self.purpose = purpose
        self.key_manager = KeyManager()
    
    def encrypt_field(self, value: str, context: str = None) -> str:
        """
        Encrypt a string field for database storage
        
        Args:
            value: String to encrypt
            context: Optional context string for additional authentication
        
        Returns:
            Base64-encoded encrypted value with version prefix
        """
        if not value:
            return value
        
        version = self.key_manager.get_current_version(self.purpose)
        key = self.key_manager.derive_key(self.purpose, version)
        encryptor = AESEncryptor(key)
        
        # Use context as associated data
        associated_data = context.encode() if context else None
        
        # Encrypt
        ciphertext = encryptor.encrypt(value.encode('utf-8'), associated_data)
        
        # Encode and add version prefix
        encoded = base64.urlsafe_b64encode(ciphertext).decode('ascii')
        return f"v{version}{self.VERSION_SEPARATOR}{encoded}"
    
    def decrypt_field(self, encrypted_value: str, context: str = None) -> str:
        """
        Decrypt a string field from database
        
        Args:
            encrypted_value: Base64-encoded encrypted value with version prefix
            context: Same context used during encryption
        
        Returns:
            Decrypted string
        """
        if not encrypted_value:
            return encrypted_value
        
        # Parse version and ciphertext
        if self.VERSION_SEPARATOR not in encrypted_value:
            raise EncryptionError("Invalid encrypted value format")
        
        version_str, encoded = encrypted_value.split(self.VERSION_SEPARATOR, 1)
        
        try:
            version = int(version_str[1:])  # Remove 'v' prefix
        except ValueError:
            raise EncryptionError("Invalid version number")
        
        # Get key for this version
        key = self.key_manager.derive_key(self.purpose, version)
        encryptor = AESEncryptor(key)
        
        # Decode and decrypt
        ciphertext = base64.urlsafe_b64decode(encoded.encode('ascii'))
        associated_data = context.encode() if context else None
        
        plaintext = encryptor.decrypt(ciphertext, associated_data)
        return plaintext.decode('utf-8')
    
    def rotate_encryption(self, encrypted_value: str, context: str = None) -> str:
        """
        Re-encrypt a value with the current key version
        Use this during key rotation
        """
        # Decrypt with old key
        plaintext = self.decrypt_field(encrypted_value, context)
        
        # Re-encrypt with current key
        return self.encrypt_field(plaintext, context)


class TokenEncryptor:
    """
    Specialized encryption for tokens (API keys, OAuth tokens, etc.)
    Uses Fernet for simple symmetric encryption
    """
    
    def __init__(self):
        self.key_manager = KeyManager()
        self._fernet_key = self._derive_fernet_key()
        self._fernet = Fernet(self._fernet_key)
    
    def _derive_fernet_key(self) -> bytes:
        """Derive a Fernet-compatible key"""
        key = self.key_manager.derive_key('tokens', 1)
        return base64.urlsafe_b64encode(key)
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token"""
        return self._fernet.encrypt(token.encode()).decode('ascii')
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a token"""
        try:
            return self._fernet.decrypt(encrypted_token.encode()).decode('utf-8')
        except Exception as e:
            logger.error(f"Token decryption failed: {e}")
            raise EncryptionError("Token decryption failed")


class HashUtility:
    """
    Secure hashing utilities for passwords and verification
    """
    
    @staticmethod
    def hash_password(password: str, salt: bytes = None) -> Tuple[str, str]:
        """
        Hash a password using Scrypt (memory-hard function)
        
        Returns:
            Tuple of (hash, salt) both base64-encoded
        """
        if salt is None:
            salt = secrets.token_bytes(32)
        
        kdf = Scrypt(
            salt=salt,
            length=32,
            n=2**14,  # CPU/memory cost
            r=8,       # Block size
            p=1,       # Parallelization
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode())
        
        return (
            base64.b64encode(key).decode('ascii'),
            base64.b64encode(salt).decode('ascii')
        )
    
    @staticmethod
    def verify_password(password: str, hash_value: str, salt: str) -> bool:
        """
        Verify a password against its hash
        """
        salt_bytes = base64.b64decode(salt.encode('ascii'))
        computed_hash, _ = HashUtility.hash_password(password, salt_bytes)
        
        # Constant-time comparison
        return hmac.compare_digest(computed_hash, hash_value)
    
    @staticmethod
    def hash_api_key(api_key: str) -> str:
        """
        Hash an API key using SHA-256
        For storing and comparing API keys
        """
        return hashlib.sha256(api_key.encode()).hexdigest()
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """Generate a cryptographically secure token"""
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def generate_verification_code(length: int = 6) -> str:
        """Generate a numeric verification code"""
        return ''.join(secrets.choice('0123456789') for _ in range(length))


# ===================== DJANGO MODEL FIELD =====================

class EncryptedTextField:
    """
    Descriptor for encrypted text fields in Django models
    Usage: 
        class MyModel(models.Model):
            sensitive_data = models.TextField()
            _encrypted_data = EncryptedTextField('sensitive_data', 'my_purpose')
    """
    
    def __init__(self, field_name: str, purpose: str = 'default'):
        self.field_name = field_name
        self.purpose = purpose
        self._encryptor = None
    
    @property
    def encryptor(self):
        if self._encryptor is None:
            self._encryptor = FieldEncryptor(self.purpose)
        return self._encryptor
    
    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = f'_encrypted_{name}'
    
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        
        encrypted_value = getattr(obj, self.field_name, None)
        if not encrypted_value:
            return None
        
        try:
            return self.encryptor.decrypt_field(
                encrypted_value,
                context=str(obj.pk) if hasattr(obj, 'pk') else None
            )
        except EncryptionError:
            logger.error(f"Failed to decrypt field {self.field_name}")
            return None
    
    def __set__(self, obj, value):
        if value is None:
            setattr(obj, self.field_name, None)
            return
        
        encrypted_value = self.encryptor.encrypt_field(
            value,
            context=str(obj.pk) if hasattr(obj, 'pk') and obj.pk else None
        )
        setattr(obj, self.field_name, encrypted_value)


# ===================== UTILITY FUNCTIONS =====================

def encrypt_sensitive_data(data: Dict[str, Any], fields_to_encrypt: list) -> Dict[str, Any]:
    """
    Encrypt specific fields in a dictionary
    """
    encryptor = FieldEncryptor('sensitive_data')
    result = data.copy()
    
    for field in fields_to_encrypt:
        if field in result and result[field]:
            result[field] = encryptor.encrypt_field(str(result[field]))
    
    return result


def decrypt_sensitive_data(data: Dict[str, Any], fields_to_decrypt: list) -> Dict[str, Any]:
    """
    Decrypt specific fields in a dictionary
    """
    encryptor = FieldEncryptor('sensitive_data')
    result = data.copy()
    
    for field in fields_to_decrypt:
        if field in result and result[field]:
            try:
                result[field] = encryptor.decrypt_field(result[field])
            except EncryptionError:
                result[field] = None
    
    return result


def generate_data_encryption_key() -> str:
    """Generate a new data encryption key for .env file"""
    return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('ascii')
