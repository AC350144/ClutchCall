import unittest
from app.logic import suggest_budget


class TestBudgetSuggestion(unittest.TestCase):

    def test_reasonable_budget(self):
        """Test a reasonable budget allocation scenario"""
        result = suggest_budget(
            income=4000,
            fixed_expenses=1500,
            savings_goal=2400,
            months_to_goal=6
        )
        self.assertIsInstance(result, dict, "Result should be a dictionary")
        self.assertIn("Income", result)
        self.assertIn("Budget Allocation", result)

        allocations = result["Budget Allocation"]
        for category, amount in allocations.items():
            self.assertGreaterEqual(amount, 0, f"{category} should not be negative")

        print("\n✅ test_reasonable_budget passed — Budget allocations are valid and non-negative.")

    def test_unrealistic_goal(self):
        """Test an unrealistic savings goal scenario"""
        result = suggest_budget(
            income=2000,
            fixed_expenses=1800,
            savings_goal=10000,
            months_to_goal=6
        )
        self.assertIsInstance(result, str)
        self.assertIn("not realistic", result)

        print("\n✅ test_unrealistic_goal passed — Unrealistic goal properly handled with warning.")


if __name__ == "__main__":
    unittest.main(verbosity=2)