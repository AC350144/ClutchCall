"""
Secure Key Management Module
Handles encryption keys using OS secure storage (Windows Credential Manager, macOS Keychain, Linux Secret Service)
"""

import keyring
import secrets
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)

class SecureKeyManager:
    """Manages encryption keys using OS secure storage"""
    
    SERVICE_NAME = "ClipVault"
    CLIPBOARD_KEY_NAME = "clipboard_encryption_key"
    JWT_SECRET_KEY_NAME = "jwt_secret_key"
    MASTER_PASSWORD_KEY_NAME = "master_password"
    
    def __init__(self):
        """Initialize the secure key manager"""
        self._ensure_keys_exist()
    
    def _ensure_keys_exist(self):
        """Ensure all required keys exist in secure storage, create if not"""
        try:
            # Check and create clipboard encryption key
            if not self.get_clipboard_key():
                self._generate_clipboard_key()
                logger.info("Generated new clipboard encryption key")
            
            # Check and create JWT secret key
            if not self.get_jwt_secret():
                self._generate_jwt_secret()
                logger.info("Generated new JWT secret key")
                
        except Exception as e:
            logger.error(f"Failed to ensure keys exist: {e}")
            raise
    
    def _generate_clipboard_key(self) -> str:
        """Generate and store a new clipboard encryption key"""
        try:
            # Generate a Fernet-compatible key (32 bytes, base64 encoded)
            key = Fernet.generate_key()
            key_str = key.decode('utf-8')
            
            # Store in OS secure storage
            keyring.set_password(self.SERVICE_NAME, self.CLIPBOARD_KEY_NAME, key_str)
            
            return key_str
        except Exception as e:
            logger.error(f"Failed to generate clipboard key: {e}")
            raise
    
    def _generate_jwt_secret(self) -> str:
        """Generate and store a new JWT secret key"""
        try:
            # Generate a secure random string for JWT
            jwt_secret = secrets.token_urlsafe(32)
            
            # Store in OS secure storage
            keyring.set_password(self.SERVICE_NAME, self.JWT_SECRET_KEY_NAME, jwt_secret)
            
            return jwt_secret
        except Exception as e:
            logger.error(f"Failed to generate JWT secret: {e}")
            raise
    
    def get_clipboard_key(self) -> str:
        """Retrieve clipboard encryption key from secure storage"""
        try:
            key = keyring.get_password(self.SERVICE_NAME, self.CLIPBOARD_KEY_NAME)
            return key
        except Exception as e:
            logger.error(f"Failed to retrieve clipboard key: {e}")
            return None
    
    def get_jwt_secret(self) -> str:
        """Retrieve JWT secret key from secure storage"""
        try:
            secret = keyring.get_password(self.SERVICE_NAME, self.JWT_SECRET_KEY_NAME)
            return secret
        except Exception as e:
            logger.error(f"Failed to retrieve JWT secret: {e}")
            return None
    
    def rotate_clipboard_key(self) -> str:
        """Rotate (regenerate) the clipboard encryption key"""
        try:
            old_key = self.get_clipboard_key()
            new_key = self._generate_clipboard_key()
            
            logger.info("Clipboard encryption key rotated successfully")
            return new_key
        except Exception as e:
            logger.error(f"Failed to rotate clipboard key: {e}")
            raise
    
    def rotate_jwt_secret(self) -> str:
        """Rotate (regenerate) the JWT secret key"""
        try:
            old_secret = self.get_jwt_secret()
            new_secret = self._generate_jwt_secret()
            
            logger.info("JWT secret key rotated successfully")
            return new_secret
        except Exception as e:
            logger.error(f"Failed to rotate JWT secret: {e}")
            raise
    
    def derive_key_from_password(self, password: str, salt: bytes = None) -> tuple[bytes, bytes]:
        """
        Derive an encryption key from a master password using PBKDF2
        Returns (key, salt) tuple
        """
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,  # OWASP recommended minimum
        )
        key = kdf.derive(password.encode())
        return key, salt
    
    def clear_all_keys(self):
        """Remove all keys from secure storage (use with caution!)"""
        try:
            keyring.delete_password(self.SERVICE_NAME, self.CLIPBOARD_KEY_NAME)
            keyring.delete_password(self.SERVICE_NAME, self.JWT_SECRET_KEY_NAME)
            logger.warning("All keys cleared from secure storage")
        except Exception as e:
            logger.error(f"Failed to clear keys: {e}")
            raise
    
    def get_key_info(self) -> dict:
        """Get information about stored keys (for debugging/admin purposes)"""
        info = {
            "clipboard_key_exists": bool(self.get_clipboard_key()),
            "jwt_secret_exists": bool(self.get_jwt_secret()),
            "service_name": self.SERVICE_NAME
        }
        return info

# Global instance for the application
key_manager = SecureKeyManager()