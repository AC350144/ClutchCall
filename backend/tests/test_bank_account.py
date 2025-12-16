"""
Essential tests for bank account functionality.
"""

import unittest
import sys
import os
import hashlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.bank_account import (
    validate_routing_number,
    validate_account_number,
    mask_account_number,
    mask_routing_number,
    encrypt_data,
    decrypt_data,
    BankAccount
)


class TestRoutingNumberValidation(unittest.TestCase):
    """Tests for routing number validation."""

    def test_valid_routing_numbers(self):
        """Test valid routing numbers pass validation."""
        valid_numbers = ["021000021", "011401533", "091000019"]
        for num in valid_numbers:
            self.assertTrue(validate_routing_number(num), f"{num} should be valid")

    def test_invalid_routing_number_wrong_length(self):
        """Test routing numbers with wrong length fail."""
        self.assertFalse(validate_routing_number("12345678"))  # 8 digits
        self.assertFalse(validate_routing_number("1234567890"))  # 10 digits

    def test_invalid_routing_number_non_numeric(self):
        """Test non-numeric routing numbers fail."""
        self.assertFalse(validate_routing_number("12345678a"))
        self.assertFalse(validate_routing_number("abcdefghi"))


class TestAccountNumberValidation(unittest.TestCase):
    """Tests for account number validation."""

    def test_valid_account_numbers(self):
        """Test valid account numbers pass validation (8-17 digits)."""
        valid_numbers = ["12345678", "123456789012", "12345678901234567"]
        for num in valid_numbers:
            self.assertTrue(validate_account_number(num), f"{num} should be valid")

    def test_invalid_too_short(self):
        """Test account numbers that are too short fail."""
        self.assertFalse(validate_account_number("1234567"))  # 7 digits

    def test_invalid_too_long(self):
        """Test account numbers that are too long fail."""
        self.assertFalse(validate_account_number("123456789012345678"))  # 18 digits

    def test_invalid_non_numeric(self):
        """Test non-numeric account numbers fail."""
        self.assertFalse(validate_account_number("1234abcd"))


class TestMasking(unittest.TestCase):
    """Tests for account/routing number masking."""

    def test_mask_account_number(self):
        """Test account number masking (returns last 4 digits)."""
        masked = mask_account_number("123456789012")
        self.assertEqual(masked, "9012")

    def test_mask_routing_number(self):
        """Test routing number masking (uses bullet characters)."""
        masked = mask_routing_number("021000021")
        self.assertEqual(masked, "•••••0021")

    def test_mask_short_account(self):
        """Test masking short account number (returns as-is if 4 or fewer)."""
        masked = mask_account_number("1234")
        self.assertEqual(masked, "1234")


class TestEncryption(unittest.TestCase):
    """Tests for data encryption."""

    def test_encrypt_decrypt_roundtrip(self):
        """Test encryption and decryption roundtrip."""
        original = "123456789012"
        encrypted = encrypt_data(original)
        decrypted = decrypt_data(encrypted)
        self.assertEqual(decrypted, original)

    def test_encrypted_data_is_not_plaintext(self):
        """Test that encrypted data is not plaintext."""
        original = "123456789012"
        encrypted = encrypt_data(original)
        self.assertNotEqual(encrypted, original)

    def test_encryption_produces_different_ciphertext(self):
        """Test that encryption produces different ciphertext each time."""
        original = "123456789012"
        encrypted1 = encrypt_data(original)
        encrypted2 = encrypt_data(original)
        self.assertNotEqual(encrypted1, encrypted2)


class TestBankAccountClass(unittest.TestCase):
    """Tests for BankAccount class."""

    def test_create_bank_account(self):
        """Test creating a BankAccount instance."""
        account = BankAccount(
            user_id=1,
            bank_name="Chase",
            routing_number="021000021",
            account_number="123456789012",
            account_type="checking"
        )
        self.assertEqual(account.bank_name, "Chase")
        self.assertEqual(account.account_type, "checking")

    def test_bank_account_last_four(self):
        """Test getting last four digits."""
        account = BankAccount(
            user_id=1,
            bank_name="Chase",
            routing_number="021000021",
            account_number="123456789012",
            account_type="checking"
        )
        self.assertEqual(account.last_four, "9012")

    def test_bank_account_to_dict(self):
        """Test converting to dictionary."""
        account = BankAccount(
            user_id=1,
            bank_name="Chase",
            routing_number="021000021",
            account_number="123456789012",
            account_type="checking"
        )
        data = account.to_dict()
        self.assertIn("bank_name", data)
        self.assertIn("last_four", data)
        self.assertIn("masked_routing", data)

    def test_bank_account_is_primary_default(self):
        """Test default is_primary value."""
        account = BankAccount(
            user_id=1,
            bank_name="Chase",
            routing_number="021000021",
            account_number="123456789012",
            account_type="checking"
        )
        self.assertFalse(account.is_primary)


if __name__ == "__main__":
    unittest.main()
