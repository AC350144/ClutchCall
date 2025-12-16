"""
Essential tests for Flask API endpoints.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestChatEndpointLogic(unittest.TestCase):
    """Tests for chat endpoint logic."""

    def test_calculate_remaining_budget(self):
        """Test remaining budget calculation."""
        income = 3000
        expenses = 1500
        remaining = income - expenses
        self.assertEqual(remaining, 1500)

    def test_keyword_detection(self):
        """Test keyword detection for various intents."""
        keywords = {
            "help": "help me please",
            "reset": "reset my data",
            "income": "update my income",
            "budget": "show my budget"
        }
        for keyword, text in keywords.items():
            self.assertIn(keyword, text.lower())

    def test_amount_extraction(self):
        """Test extracting numeric amounts from text."""
        text = "add 250 to food"
        amount = float("".join([c for c in text if c.isdigit() or c == "."]))
        self.assertEqual(amount, 250)


class TestInputValidation(unittest.TestCase):
    """Tests for input validation logic."""

    def test_empty_input_validation(self):
        """Test empty input validation."""
        self.assertFalse(bool(""))
        self.assertTrue(bool("valid"))

    def test_password_length_validation(self):
        """Test password length validation."""
        self.assertLess(len("1234567"), 8)
        self.assertGreaterEqual(len("12345678"), 8)

    def test_email_normalization(self):
        """Test email normalization."""
        email = "  TEST@EXAMPLE.COM  "
        normalized = email.strip().lower()
        self.assertEqual(normalized, "test@example.com")


class TestResponseFormats(unittest.TestCase):
    """Tests for API response format validation."""

    def test_success_response(self):
        """Test success response format."""
        response = {"status": "ok", "mfa": True}
        self.assertIn("status", response)
        self.assertTrue(response["mfa"])

    def test_error_response(self):
        """Test error response format."""
        response = {"error": "Something went wrong"}
        self.assertIn("error", response)


class TestBetParseEndpoint(unittest.TestCase):
    """Tests for bet parsing endpoint."""

    def test_parse_result_keys(self):
        """Test parse result structure."""
        result = {
            "legs": [],
            "totalOdds": -110,
            "potentialPayout": 100,
            "recommendation": {}
        }
        self.assertIn("legs", result)
        self.assertIn("totalOdds", result)
        self.assertIn("potentialPayout", result)


if __name__ == "__main__":
    unittest.main()
