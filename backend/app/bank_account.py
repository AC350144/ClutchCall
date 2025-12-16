"""
Bank Account Encryption Module

This module provides secure encryption and decryption for sensitive
bank account information using Fernet symmetric encryption.
"""

import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import hashlib


# Get or generate encryption key
# In production, this should be stored securely (e.g., environment variable, secrets manager)
ENCRYPTION_KEY = os.getenv("BANK_ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    # For development, generate a key from a passphrase
    # In production, use a proper key management system
    passphrase = os.getenv("SECRET_KEY", "ClutchCall_Development_Key_2024")
    salt = b'clutchcall_bank_salt_v1'
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(passphrase.encode()))
    ENCRYPTION_KEY = key
else:
    ENCRYPTION_KEY = ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY


def get_fernet():
    """Get a Fernet instance for encryption/decryption."""
    return Fernet(ENCRYPTION_KEY)


def encrypt_data(plaintext: str) -> str:
    """
    Encrypt sensitive data using Fernet symmetric encryption.
    
    Args:
        plaintext: The string to encrypt
        
    Returns:
        Base64-encoded encrypted string
    """
    if not plaintext:
        return ""
    
    f = get_fernet()
    encrypted = f.encrypt(plaintext.encode())
    return encrypted.decode()


def decrypt_data(ciphertext: str) -> str:
    """
    Decrypt data that was encrypted with encrypt_data.
    
    Args:
        ciphertext: The encrypted string
        
    Returns:
        Decrypted plaintext string
    """
    if not ciphertext:
        return ""
    
    try:
        f = get_fernet()
        decrypted = f.decrypt(ciphertext.encode())
        return decrypted.decode()
    except Exception as e:
        print(f"Decryption error: {e}")
        return ""


def mask_account_number(account_number: str) -> str:
    """
    Mask account number for display, showing only last 4 digits.
    
    Args:
        account_number: Full account number
        
    Returns:
        Last 4 digits of account number
    """
    if not account_number:
        return ""
    
    if len(account_number) <= 4:
        return account_number
    
    return account_number[-4:]


def mask_routing_number(routing_number: str) -> str:
    """
    Mask routing number for display, showing only last 4 digits.
    
    Args:
        routing_number: Full routing number
        
    Returns:
        Masked routing number (e.g., "•••••6789")
    """
    if not routing_number or len(routing_number) < 4:
        return "•••••"
    
    return "•••••" + routing_number[-4:]


def validate_routing_number(routing_number: str) -> bool:
    """
    Validate a US bank routing number using the checksum algorithm.
    
    The routing number must be 9 digits and pass the checksum validation:
    3(d1 + d4 + d7) + 7(d2 + d5 + d8) + (d3 + d6 + d9) mod 10 = 0
    
    Args:
        routing_number: 9-digit routing number
        
    Returns:
        True if valid, False otherwise
    """
    if not routing_number:
        return False
    
    # Remove any non-digit characters
    routing_number = ''.join(filter(str.isdigit, routing_number))
    
    if len(routing_number) != 9:
        return False
    
    try:
        digits = [int(d) for d in routing_number]
        checksum = (
            3 * (digits[0] + digits[3] + digits[6]) +
            7 * (digits[1] + digits[4] + digits[7]) +
            (digits[2] + digits[5] + digits[8])
        )
        return checksum % 10 == 0
    except (ValueError, IndexError):
        return False


def validate_account_number(account_number: str) -> bool:
    """
    Validate a bank account number format.
    
    Account numbers are typically 8-17 digits.
    
    Args:
        account_number: The account number to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not account_number:
        return False
    
    # Check if input contains only digits
    if not account_number.isdigit():
        return False
    
    # Account numbers are typically 8-17 digits
    if len(account_number) < 8 or len(account_number) > 17:
        return False
    
    return True


def hash_for_verification(data: str) -> str:
    """
    Create a SHA-256 hash of data for verification purposes.
    This can be used to verify data without decrypting.
    
    Args:
        data: Data to hash
        
    Returns:
        Hex digest of the hash
    """
    return hashlib.sha256(data.encode()).hexdigest()


class BankAccount:
    """Class representing an encrypted bank account."""
    
    def __init__(
        self,
        user_id: int,
        routing_number: str,
        account_number: str,
        account_type: str = "checking",
        bank_name: str = "",
        account_holder_name: str = "",
        is_primary: bool = False,
        id: int = None
    ):
        self.id = id
        self.user_id = user_id
        self.account_holder_name = account_holder_name
        self._routing_number = routing_number
        self._account_number = account_number
        self.account_type = account_type
        self.bank_name = bank_name
        self.is_primary = is_primary
    
    @property
    def encrypted_routing_number(self) -> str:
        """Get encrypted routing number."""
        return encrypt_data(self._routing_number)
    
    @property
    def encrypted_account_number(self) -> str:
        """Get encrypted account number."""
        return encrypt_data(self._account_number)
    
    @property
    def masked_routing_number(self) -> str:
        """Get masked routing number for display."""
        return mask_routing_number(self._routing_number)
    
    @property
    def masked_account_number(self) -> str:
        """Get masked account number for display."""
        return mask_account_number(self._account_number)
    
    @property
    def last_four(self) -> str:
        """Get last 4 digits of account number."""
        return mask_account_number(self._account_number)
    
    @property
    def routing_number_hash(self) -> str:
        """Get hash of routing number for verification."""
        return hash_for_verification(self._routing_number)
    
    @property
    def account_number_hash(self) -> str:
        """Get hash of account number for verification."""
        return hash_for_verification(self._account_number)
    
    def get_routing_number(self) -> str:
        """Get the decrypted routing number."""
        return self._routing_number
    
    def get_account_number(self) -> str:
        """Get the decrypted account number."""
        return self._account_number
    
    def __str__(self) -> str:
        """String representation without sensitive data."""
        return f"BankAccount(bank={self.bank_name}, type={self.account_type}, last_four={self.last_four})"
    
    def __repr__(self) -> str:
        """Repr without sensitive data."""
        return self.__str__()
    
    def validate(self) -> tuple:
        """
        Validate the bank account information.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not validate_routing_number(self._routing_number):
            return False, "Invalid routing number"
        
        if not validate_account_number(self._account_number):
            return False, "Invalid account number"
        
        if self.account_type not in ["checking", "savings"]:
            return False, "Account type must be 'checking' or 'savings'"
        
        return True, ""
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        Convert to dictionary for JSON serialization.
        
        Args:
            include_sensitive: If True, include masked sensitive fields
            
        Returns:
            Dictionary representation
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "account_type": self.account_type,
            "bank_name": self.bank_name,
            "last_four": self.last_four,
            "masked_routing": self.masked_routing_number,
            "is_primary": self.is_primary,
        }
        
        if self.account_holder_name:
            data["account_holder_name"] = self.account_holder_name
        
        return data
    
    @staticmethod
    def from_db_row(row: dict) -> 'BankAccount':
        """
        Create a BankAccount from a database row.
        
        Args:
            row: Database row dictionary with encrypted fields
            
        Returns:
            BankAccount instance
        """
        return BankAccount(
            id=row.get("id"),
            user_id=row.get("user_id"),
            account_holder_name=row.get("account_holder_name", ""),
            routing_number=decrypt_data(row.get("encrypted_routing_number", "")),
            account_number=decrypt_data(row.get("encrypted_account_number", "")),
            account_type=row.get("account_type", "checking"),
            bank_name=row.get("bank_name", ""),
            is_primary=row.get("is_primary", False)
        )
