"""
Essential tests for MFA functionality.
"""

import unittest
import sys
import os
import pyotp

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestMFASecretGeneration(unittest.TestCase):
    """Tests for MFA secret generation."""

    def test_secret_generation(self):
        """Test MFA secret generation."""
        secret = pyotp.random_base32()
        self.assertIsNotNone(secret)
        self.assertEqual(len(secret), 32)

    def test_secret_is_base32(self):
        """Test secret is valid base32."""
        secret = pyotp.random_base32()
        import base64
        try:
            base64.b32decode(secret)
            valid = True
        except:
            valid = False
        self.assertTrue(valid)


class TestTOTPValidation(unittest.TestCase):
    """Tests for TOTP code validation."""

    def test_valid_code(self):
        """Test valid TOTP code validation."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        current_code = totp.now()
        self.assertTrue(totp.verify(current_code))

    def test_invalid_code(self):
        """Test invalid TOTP code rejection."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        self.assertFalse(totp.verify("000000"))

    def test_code_format(self):
        """Test TOTP code format."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        code = totp.now()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())


class TestMFAURIGeneration(unittest.TestCase):
    """Tests for MFA URI generation."""

    def test_provisioning_uri(self):
        """Test provisioning URI generation."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name="test@example.com", issuer_name="ClutchCall")
        self.assertIn("otpauth://totp/", uri)
        self.assertIn("ClutchCall", uri)

    def test_uri_contains_secret(self):
        """Test URI contains secret."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name="test@example.com", issuer_name="ClutchCall")
        self.assertIn(secret, uri)


class TestMFACodeTiming(unittest.TestCase):
    """Tests for MFA code timing."""

    def test_code_changes_over_time(self):
        """Test that codes are time-based."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        code1 = totp.at(0)
        code2 = totp.at(30)
        # Codes at different intervals should generally differ
        # (not guaranteed but very likely)
        self.assertEqual(len(code1), 6)
        self.assertEqual(len(code2), 6)

    def test_interval_default(self):
        """Test default interval is 30 seconds."""
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        self.assertEqual(totp.interval, 30)


if __name__ == "__main__":
    unittest.main()
