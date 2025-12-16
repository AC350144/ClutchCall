import unittest
from app.logic import suggest_budget


class TestBudgetStress(unittest.TestCase):
    """Stress and edge case tests for AI Financial Assistant"""

    def test_low_income_high_expenses(self):
        """Test when expenses exceed income"""
        result = suggest_budget(1500, 1800, 500, 6)
        self.assertIsInstance(result, str)
        self.assertIn("not realistic", result)
        print("\n✅ test_low_income_high_expenses passed — Properly flagged unrealistic expense scenario.")

    def test_high_income_small_goal(self):
        """Test when income is large and goal is small"""
        result = suggest_budget(10000, 2000, 1000, 12)
        self.assertIsInstance(result, dict)
        allocations = result["Budget Allocation"]
        self.assertGreater(allocations["Food"], 0)
        self.assertGreater(allocations["Entertainment"], 0)
        print("\n✅ test_high_income_small_goal passed — Allocations scale correctly for high-income scenario.")

    def test_extreme_savings_goal(self):
        """Test when user tries to save almost entire income"""
        result = suggest_budget(4000, 1000, 3500, 3)
        if isinstance(result, dict):
            total_alloc = sum(result["Budget Allocation"].values())
            self.assertLess(total_alloc, 4000)
        else:
            self.assertIn("not realistic", result)
        print("\n✅ test_extreme_savings_goal passed — Handled over-aggressive savings correctly.")

    def test_zero_income(self):
        """Test when income is zero"""
        result = suggest_budget(0, 0, 0, 6)
        self.assertIsInstance(result, str)
        self.assertIn("not realistic", result)
        print("\n✅ test_zero_income passed — Properly rejects zero income input.")

    def test_negative_values(self):
        """Test with negative income and expenses"""
        result = suggest_budget(-5000, -2000, -1000, 6)
        self.assertIsInstance(result, str)
        self.assertIn("not realistic", result)
        print("\n✅ test_negative_values passed — Caught invalid negative inputs.")

    def test_large_goal_long_timeframe(self):
        """Test large savings goal over long months"""
        result = suggest_budget(5000, 2500, 60000, 36)
        self.assertIsInstance(result, dict)
        print("\n✅ test_large_goal_long_timeframe passed — Long-term savings handled properly.")

    def test_tiny_goal_short_time(self):
        """Test very small savings goal"""
        result = suggest_budget(3000, 1500, 100, 1)
        self.assertIsInstance(result, dict)
        print("\n✅ test_tiny_goal_short_time passed — Small goals computed correctly.")

    def test_output_sum(self):
        """Ensure allocations + savings + fixed expenses ≈ income"""
        result = suggest_budget(5000, 2000, 3000, 6)
        if isinstance(result, dict):
            total = result["Fixed Expenses"] + result["Savings per Month"] + sum(result["Budget Allocation"].values())
            self.assertLessEqual(abs(total - 5000), 100, "Total allocation should not exceed income")
        print("\n✅ test_output_sum passed — Allocations consistent with income.")

    def test_randomized_inputs(self):
        """Run random-like inputs to test model stability"""
        combos = [
            (3200, 1200, 2000, 8),
            (6000, 2500, 10000, 12),
            (4500, 1000, 4000, 4),
        ]
        for income, fixed, goal, months in combos:
            result = suggest_budget(income, fixed, goal, months)
            self.assertIn("Budget Allocation", result)
        print("\n✅ test_randomized_inputs passed — Model stable under various realistic scenarios.")

    def test_output_structure(self):
        """Check structure of returned dictionary"""
        result = suggest_budget(4000, 1500, 2400, 6)
        keys = ["Income", "Fixed Expenses", "Savings per Month", "Budget Allocation"]
        for key in keys:
            self.assertIn(key, result)
        self.assertIsInstance(result["Budget Allocation"], dict)
        print("\n✅ test_output_structure passed — Result structure validated.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
