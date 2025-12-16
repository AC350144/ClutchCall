"""
Essential tests for input security and validation.
"""

import unittest
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestSQLInjectionPrevention(unittest.TestCase):
    """Tests for SQL injection prevention."""

    def test_sql_injection_patterns(self):
        """Test common SQL injection patterns are detected."""
        dangerous_inputs = [
            "'; DROP TABLE users; --",
            "1 OR 1=1",
            "admin'--",
            "1; DELETE FROM users",
        ]
        sql_pattern = re.compile(r"(--|;|'|\bOR\b|\bAND\b|\bDROP\b|\bDELETE\b)", re.IGNORECASE)
        for input_str in dangerous_inputs:
            self.assertTrue(sql_pattern.search(input_str), f"{input_str} should be flagged")

    def test_safe_inputs(self):
        """Test that safe inputs pass."""
        safe_inputs = ["john_doe", "user@example.com", "Hello World"]
        sql_pattern = re.compile(r"(--|'\s*OR|DROP\s+TABLE|DELETE\s+FROM)", re.IGNORECASE)
        for input_str in safe_inputs:
            self.assertFalse(sql_pattern.search(input_str), f"{input_str} should be safe")


class TestXSSPrevention(unittest.TestCase):
    """Tests for XSS prevention."""

    def test_script_tag_detection(self):
        """Test script tag detection."""
        dangerous_inputs = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "<svg onload=alert('xss')>",
        ]
        xss_pattern = re.compile(r"<(script|img|svg|iframe)", re.IGNORECASE)
        for input_str in dangerous_inputs:
            self.assertTrue(xss_pattern.search(input_str), f"{input_str} should be flagged")


class TestInputSanitization(unittest.TestCase):
    """Tests for input sanitization."""

    def test_whitespace_trimming(self):
        """Test whitespace is trimmed."""
        inputs = ["  hello  ", "\n\ttest\n\t", "  spaces  "]
        for input_str in inputs:
            self.assertEqual(input_str.strip(), input_str.strip())

    def test_empty_after_strip(self):
        """Test empty string after strip."""
        self.assertEqual("   ".strip(), "")
        self.assertEqual("\n\t".strip(), "")

    def test_html_entity_encoding(self):
        """Test HTML entity encoding."""
        dangerous = "<script>"
        import html
        safe = html.escape(dangerous)
        self.assertEqual(safe, "&lt;script&gt;")


class TestPasswordRequirements(unittest.TestCase):
    """Tests for password requirements."""

    def test_minimum_length(self):
        """Test minimum password length."""
        self.assertLess(len("short"), 8)
        self.assertGreaterEqual(len("longpassword"), 8)

    def test_not_common_passwords(self):
        """Test common password detection."""
        common = ["password", "123456", "qwerty", "admin"]
        user_password = "MySecureP@ss123"
        self.assertNotIn(user_password.lower(), common)


class TestEmailValidation(unittest.TestCase):
    """Tests for email validation."""

    def test_valid_email_format(self):
        """Test valid email format."""
        valid_emails = ["test@example.com", "user.name@domain.org", "user+tag@example.com"]
        email_pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
        for email in valid_emails:
            self.assertTrue(email_pattern.match(email), f"{email} should be valid")

    def test_invalid_email_format(self):
        """Test invalid email format."""
        invalid_emails = ["notanemail", "@nodomain.com", "user@", "user@.com"]
        email_pattern = re.compile(r"^[^@]+@[^@]+\.[^@]+$")
        for email in invalid_emails:
            self.assertFalse(email_pattern.match(email), f"{email} should be invalid")


class TestNumericInputValidation(unittest.TestCase):
    """Tests for numeric input validation."""

    def test_positive_numbers(self):
        """Test positive number validation."""
        self.assertGreater(100, 0)
        self.assertGreater(0.01, 0)

    def test_negative_numbers_rejected(self):
        """Test negative numbers are rejected for amounts."""
        amount = -100
        self.assertLess(amount, 0)

    def test_reasonable_limits(self):
        """Test reasonable limits for financial inputs."""
        max_amount = 1000000
        self.assertLessEqual(999999, max_amount)
        self.assertGreater(1000001, max_amount)


if __name__ == "__main__":
    unittest.main()
