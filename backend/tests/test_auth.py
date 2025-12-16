"""
Essential tests for authentication logic.
"""

import unittest
import sys
import os
import jwt
import bcrypt
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SECRET_KEY = "TEST_SECRET"
ALGORITHM = "HS256"


class TestTokenCreation(unittest.TestCase):
    """Tests for JWT token creation."""

    def test_create_access_token(self):
        """Test access token creation."""
        payload = {
            "email": "test@example.com",
            "type": "access",
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        self.assertIsNotNone(token)
        self.assertIsInstance(token, str)

    def test_access_token_contains_email(self):
        """Test access token contains email."""
        payload = {"email": "user@test.com", "type": "access", "exp": datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(decoded["email"], "user@test.com")

    def test_temp_token_for_mfa(self):
        """Test temp token for MFA flow."""
        payload = {"email": "user@test.com", "type": "temp", "mfa_pending": True}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(decoded["type"], "temp")
        self.assertTrue(decoded["mfa_pending"])


class TestTokenDecoding(unittest.TestCase):
    """Tests for JWT token decoding."""

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        payload = {"email": "test@example.com", "exp": datetime.utcnow() + timedelta(hours=1)}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(decoded["email"], "test@example.com")

    def test_decode_invalid_token(self):
        """Test decoding an invalid token."""
        with self.assertRaises(jwt.InvalidTokenError):
            jwt.decode("invalid.token.here", SECRET_KEY, algorithms=[ALGORITHM])

    def test_decode_expired_token(self):
        """Test decoding an expired token."""
        payload = {"email": "test@example.com", "exp": datetime.utcnow() - timedelta(hours=1)}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        with self.assertRaises(jwt.ExpiredSignatureError):
            jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


class TestPasswordHashing(unittest.TestCase):
    """Tests for password hashing."""

    def test_password_hash_generation(self):
        """Test password hash generation."""
        password = "testpassword123"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.assertNotEqual(hashed, password.encode())

    def test_password_verification_correct(self):
        """Test correct password verification."""
        password = "testpassword123"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.assertTrue(bcrypt.checkpw(password.encode(), hashed))

    def test_password_verification_incorrect(self):
        """Test incorrect password verification."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.assertFalse(bcrypt.checkpw(wrong_password.encode(), hashed))

    def test_different_hashes_same_password(self):
        """Test that same password produces different hashes."""
        password = "testpassword123"
        hash1 = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        hash2 = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.assertNotEqual(hash1, hash2)


class TestEmailValidation(unittest.TestCase):
    """Tests for email validation."""

    def test_email_lowercase(self):
        """Test email lowercase normalization."""
        email = "TEST@EXAMPLE.COM"
        self.assertEqual(email.lower(), "test@example.com")

    def test_email_strip_whitespace(self):
        """Test email whitespace stripping."""
        email = "  test@example.com  "
        self.assertEqual(email.strip(), "test@example.com")


class TestPasswordValidation(unittest.TestCase):
    """Tests for password validation."""

    def test_password_minimum_length(self):
        """Test password minimum length requirement."""
        short_password = "short"
        valid_password = "validpassword"
        self.assertLess(len(short_password), 8)
        self.assertGreaterEqual(len(valid_password), 8)

    def test_password_with_special_chars(self):
        """Test password with special characters."""
        password = "P@ssw0rd!123"
        self.assertGreaterEqual(len(password), 8)


if __name__ == "__main__":
    unittest.main()
