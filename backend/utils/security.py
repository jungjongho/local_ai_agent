"""
Security utilities for the Local AI Agent.
"""
import hashlib
import secrets
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
from backend.config.settings import settings
from backend.utils.logger import logger


class SecurityManager:
    """Security manager for handling encryption, API key protection, and access control."""
    
    def __init__(self):
        self._cipher_suite = None
        self._setup_encryption()
    
    def _setup_encryption(self):
        """Setup encryption cipher suite."""
        try:
            # Generate or use existing key for encryption
            key = self._get_or_create_encryption_key()
            self._cipher_suite = Fernet(key)
            logger.info("Encryption system initialized")
        except Exception as e:
            logger.error(f"Failed to setup encryption: {e}")
            self._cipher_suite = None
    
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key."""
        # In production, this should be stored securely
        # For now, derive from secret key
        key_material = settings.secret_key.encode()
        derived_key = hashlib.sha256(key_material).digest()
        return Fernet.generate_key()  # Use generated key for now
    
    def encrypt_sensitive_data(self, data: str) -> Optional[str]:
        """
        Encrypt sensitive data.
        
        Args:
            data: Data to encrypt
        
        Returns:
            Encrypted data as string or None if encryption fails
        """
        if not self._cipher_suite:
            logger.warning("Encryption not available, returning data as-is")
            return data
        
        try:
            encrypted_data = self._cipher_suite.encrypt(data.encode())
            return encrypted_data.decode()
        except Exception as e:
            logger.error(f"Encryption failed: {e}")
            return None
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> Optional[str]:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data string
        
        Returns:
            Decrypted data or None if decryption fails
        """
        if not self._cipher_suite:
            logger.warning("Encryption not available, returning data as-is")
            return encrypted_data
        
        try:
            decrypted_data = self._cipher_suite.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            return None
    
    def mask_api_key(self, api_key: str) -> str:
        """
        Mask API key for logging purposes.
        
        Args:
            api_key: API key to mask
        
        Returns:
            Masked API key
        """
        if not api_key or len(api_key) < 8:
            return "****"
        
        return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"
    
    def validate_api_key_format(self, api_key: str) -> bool:
        """
        Validate OpenAI API key format.
        
        Args:
            api_key: API key to validate
        
        Returns:
            True if format is valid
        """
        if not api_key:
            return False
        
        # OpenAI API keys start with 'sk-' and are 51 characters long
        if api_key.startswith('sk-') and len(api_key) == 51:
            return True
        
        logger.warning(f"Invalid API key format: {self.mask_api_key(api_key)}")
        return False
    
    def generate_session_token(self) -> str:
        """Generate secure session token."""
        return secrets.token_urlsafe(32)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> tuple:
        """
        Hash password with salt.
        
        Args:
            password: Password to hash
            salt: Optional salt (will generate if not provided)
        
        Returns:
            Tuple of (hashed_password, salt)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 for password hashing
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode(),
            salt.encode(),
            100000  # iterations
        )
        
        return password_hash.hex(), salt
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """
        Verify password against hash.
        
        Args:
            password: Plain text password
            hashed_password: Stored password hash
            salt: Password salt
        
        Returns:
            True if password matches
        """
        computed_hash, _ = self.hash_password(password, salt)
        return secrets.compare_digest(computed_hash, hashed_password)
    
    def sanitize_file_path(self, file_path: str) -> str:
        """
        Sanitize file path to prevent directory traversal.
        
        Args:
            file_path: File path to sanitize
        
        Returns:
            Sanitized file path
        """
        import os
        
        # Remove any directory traversal attempts
        sanitized = file_path.replace('..', '').replace('//', '/')
        
        # Ensure path is relative and doesn't start with /
        sanitized = sanitized.lstrip('/')
        
        # Normalize path
        sanitized = os.path.normpath(sanitized)
        
        return sanitized
    
    def validate_command_safety(self, command: str) -> bool:
        """
        Validate if a system command is safe to execute.
        
        Args:
            command: Command to validate
        
        Returns:
            True if command is considered safe
        """
        # Define whitelist of safe commands (Phase 3 implementation)
        safe_commands = {
            'ls', 'dir', 'pwd', 'echo', 'cat', 'type',
            'grep', 'find', 'which', 'whoami', 'date',
            'python', 'pip', 'node', 'npm'
        }
        
        # Define dangerous patterns
        dangerous_patterns = [
            'rm -rf', 'del /f', 'format', 'mkfs',
            'dd if=', '> /dev/', 'sudo rm', 'sudo dd',
            'chmod 777', 'chown root', '&& rm',
            '| rm', '; rm', 'wget | sh', 'curl | sh'
        ]
        
        command_lower = command.lower()
        
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if pattern in command_lower:
                logger.warning(f"Blocked dangerous command pattern: {pattern}")
                return False
        
        # Check if command starts with safe command
        first_word = command.split()[0] if command.split() else ''
        
        if first_word in safe_commands:
            return True
        
        logger.warning(f"Command not in whitelist: {first_word}")
        return False
    
    def create_secure_headers(self) -> Dict[str, str]:
        """
        Create secure HTTP headers.
        
        Returns:
            Dictionary of security headers
        """
        return {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
            'Content-Security-Policy': "default-src 'self'",
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
    
    def audit_log(self, action: str, user_id: str = None, details: Dict[str, Any] = None):
        """
        Log security-relevant actions.
        
        Args:
            action: Action being performed
            user_id: User identifier (if applicable)
            details: Additional details to log
        """
        audit_entry = {
            'action': action,
            'user_id': user_id or 'system',
            'details': details or {},
            'timestamp': logger.datetime.now().isoformat()
        }
        
        logger.info(f"AUDIT: {action}", **audit_entry)


# Global security manager instance
security_manager = SecurityManager()


def require_api_key(func):
    """Decorator to require valid API key for function execution."""
    def wrapper(*args, **kwargs):
        if not security_manager.validate_api_key_format(settings.openai_api_key):
            raise ValueError("Invalid or missing OpenAI API key")
        return func(*args, **kwargs)
    return wrapper


def sanitize_input(max_length: int = 1000):
    """Decorator to sanitize string inputs."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Sanitize string arguments
            sanitized_kwargs = {}
            for key, value in kwargs.items():
                if isinstance(value, str):
                    # Basic sanitization
                    sanitized_value = value[:max_length].strip()
                    # Remove potentially dangerous characters
                    sanitized_value = ''.join(char for char in sanitized_value 
                                            if char.isprintable() or char.isspace())
                    sanitized_kwargs[key] = sanitized_value
                else:
                    sanitized_kwargs[key] = value
            
            return func(*args, **sanitized_kwargs)
        return wrapper
    return decorator
