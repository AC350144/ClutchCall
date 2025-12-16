"""
Clipboard Encryption Module
Handles encryption/decryption of clipboard content with secure memory management
"""

import os
import gc
import ctypes
import sys
from typing import Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64
import logging
from secure_storage import key_manager

logger = logging.getLogger(__name__)

class SecureMemory:
    """Utilities for secure memory management and clearing"""
    
    @staticmethod
    def clear_string(s: str) -> None:
        """
        Attempt to clear string from memory (best effort on CPython)
        Note: This is a best-effort approach as Python strings are immutable
        """
        try:
            # Force garbage collection
            gc.collect()
            
            # Avoid risky ctypes memory overwrites by default (can cause access violations on Windows)
            # Enable only if explicitly opted-in for specialized environments.
            if SecureMemory._ctype_clear_enabled() and sys.platform == "win32":
                try:
                    address = id(s)
                    size = sys.getsizeof(s)
                    zeros = ctypes.create_string_buffer(size)
                    ctypes.memmove(address, zeros, size)
                except Exception:
                    # Silent best-effort
                    pass
                    
        except Exception as e:
            logger.debug(f"Memory clearing attempt failed: {e}")
    
    @staticmethod
    def clear_bytes(b: bytes) -> None:
        """
        Attempt to clear bytes from memory
        """
        try:
            if hasattr(b, '__array_interface__'):
                # If it's a mutable buffer, we can zero it
                for i in range(len(b)):
                    b[i] = 0
            gc.collect()
        except Exception as e:
            logger.debug(f"Bytes clearing attempt failed: {e}")

    @staticmethod
    def _ctype_clear_enabled() -> bool:
        """Return True if dangerous ctypes clearing is explicitly enabled via env."""
        return os.getenv("CLIPVAULT_ENABLE_CTYPE_CLEAR", "0") == "1"

class ClipboardCrypto:
    """Handles encryption and decryption of clipboard content"""
    
    def __init__(self):
        """Initialize clipboard encryption with key from secure storage"""
        self._fernet = None
        self._init_encryption()
    
    def _init_encryption(self):
        """Initialize Fernet encryption with key from secure storage"""
        try:
            key = key_manager.get_clipboard_key()
            if not key:
                raise ValueError("No clipboard encryption key found in secure storage")
            
            # Convert key string back to bytes for Fernet
            key_bytes = key.encode('utf-8')
            self._fernet = Fernet(key_bytes)
            
            # Clear the key from local memory (after Fernet is initialized)
            # Note: We clear a copy, not the original variables that Fernet might still reference
            key_copy = key
            key_bytes_copy = key_bytes
            SecureMemory.clear_string(key_copy)
            SecureMemory.clear_bytes(key_bytes_copy)
            
        except Exception as e:
            logger.error(f"Failed to initialize clipboard encryption: {e}")
            raise
    
    def encrypt_content(self, content: str) -> str:
        """
        Encrypt clipboard content and return base64 encoded result
        
        Args:
            content: Plain text content to encrypt
            
        Returns:
            Base64 encoded encrypted content
        """
        if not content:
            return ""
        
        try:
            # Convert content to bytes
            content_bytes = content.encode('utf-8')
            
            # Encrypt the content
            encrypted_bytes = self._fernet.encrypt(content_bytes)
            
            # Encode to base64 for storage
            encrypted_b64 = base64.b64encode(encrypted_bytes).decode('utf-8')
            
            return encrypted_b64
            
        except Exception as e:
            logger.error(f"Failed to encrypt clipboard content: {e}")
            raise
    
    def decrypt_content(self, encrypted_content: str) -> str:
        """
        Decrypt clipboard content from base64 encoded encrypted data
        
        Args:
            encrypted_content: Base64 encoded encrypted content
            
        Returns:
            Decrypted plain text content
        """
        if not encrypted_content:
            return ""
        
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_content.encode('utf-8'))
            
            # Decrypt the content
            decrypted_bytes = self._fernet.decrypt(encrypted_bytes)
            
            # Convert back to string
            decrypted_content = decrypted_bytes.decode('utf-8')
            
            return decrypted_content
            
        except Exception as e:
            logger.error(f"Failed to decrypt clipboard content: {e}")
            raise
    
    def rotate_key(self):
        """Rotate the encryption key (note: this will invalidate existing encrypted data)"""
        try:
            logger.warning("Rotating clipboard encryption key - existing encrypted data will become inaccessible")
            key_manager.rotate_clipboard_key()
            self._init_encryption()
        except Exception as e:
            logger.error(f"Failed to rotate encryption key: {e}")
            raise
    
    def verify_encryption(self, test_content: str = "test_encryption") -> bool:
        """
        Verify that encryption/decryption is working correctly
        
        Args:
            test_content: Content to use for testing
            
        Returns:
            True if encryption/decryption works correctly
        """
        try:
            # Encrypt test content
            encrypted = self.encrypt_content(test_content)
            
            # Decrypt it back
            decrypted = self.decrypt_content(encrypted)
            
            # Check if they match
            result = (decrypted == test_content)
            
            # Clear test data
            SecureMemory.clear_string(test_content)
            SecureMemory.clear_string(encrypted)
            SecureMemory.clear_string(decrypted)
            
            return result
            
        except Exception as e:
            logger.error(f"Encryption verification failed: {e}")
            return False

# Context manager for secure string handling
class SecureString:
    """Context manager for secure string handling with automatic memory clearing"""
    
    def __init__(self, content: str):
        self.content = content
    
    def __enter__(self) -> str:
        return self.content
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        SecureMemory.clear_string(self.content)
        self.content = None

# Global instance for the application
clipboard_crypto = ClipboardCrypto()