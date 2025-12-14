import unittest
from app.logic import suggest_budget

class TestBudgetMaliciousInputs(unittest.TestCase):
    """Tests AI Financial Assistant against malicious/bad actor inputs"""

    def test_sql_injection_attempt(self):
        """Test if SQL-like input is handled safely"""
        malicious_input = "1000; DROP TABLE users;"
        result = suggest_budget(malicious_input, 500, 200, 6)
        self.assertIsInstance(result, str)
        self.assertIn("not realistic", result)
        print("\n✅ test_sql_injection_attempt passed — SQL-like input safely rejected.")

    def test_code_injection_attempt(self):
        """Test if code injection is handled safely"""
        malicious_input = "__import__('os').system('rm -rf /')"
        result = suggest_budget(5000, 2000, malicious_input, 6)
        self.assertIsInstance(result, str)
        self.assertIn("not realistic", result)
        print("\n✅ test_code_injection_attempt passed — Code injection safely rejected.")

    def test_xss_input(self):
        """Test if HTML/JS injection input is handled"""
        malicious_input = "<script>alert('hacked')</script>"
        result = suggest_budget(4000, 1500, malicious_input, 6)
        self.assertIsInstance(result, str)
        self.assertIn("not realistic", result)
        print("\n✅ test_xss_input passed — HTML/JS input safely rejected.")

    def test_extremely_long_input(self):
        """Test system behavior with extremely long strings"""
        long_input = "1" * 10000
        result = suggest_budget(long_input, 500, 200, 6)
        self.assertIsInstance(result, str)
        self.assertIn("not realistic", result)
        print("\n✅ test_extremely_long_input passed — Long input safely rejected.")

    def test_negative_strings(self):
        """Test if negative-like strings are handled"""
        malicious_input = "-5000abc"
        result = suggest_budget(malicious_input, 500, 200, 6)
        self.assertIsInstance(result, str)
        self.assertIn("not realistic", result)
        print("\n✅ test_negative_strings passed — Invalid numeric strings safely rejected.")

    def test_non_numeric_inputs(self):
        """Test various non-numeric inputs"""
        combos = ["hello", "NaN", None, True, [], {}]
        for input_val in combos:
            result = suggest_budget(input_val, 1000, 500, 6)
            self.assertIsInstance(result, str)
            self.assertIn("not realistic", result)
        print("\n✅ test_non_numeric_inputs passed — Non-numeric inputs safely rejected.")

if __name__ == "__main__":
    unittest.main(verbosity=2)