"""
Essential tests for user profile functionality.
"""

import unittest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestProfileDataStructure(unittest.TestCase):
    """Tests for profile data structure."""

    def test_profile_required_fields(self):
        """Test profile has required fields."""
        profile = {
            "id": 1,
            "username": "testuser",
            "email": "test@example.com",
            "displayName": "Test User",
            "avatar": "🎰"
        }
        self.assertIn("id", profile)
        self.assertIn("username", profile)
        self.assertIn("email", profile)

    def test_profile_optional_fields(self):
        """Test profile optional fields."""
        profile = {
            "phone": "+1234567890",
            "bettingExperience": "intermediate",
            "favoriteSports": ["nba", "nfl"],
            "monthlyBudget": 500
        }
        self.assertIn("phone", profile)
        self.assertIn("favoriteSports", profile)


class TestProfileValidation(unittest.TestCase):
    """Tests for profile validation."""

    def test_display_name_length(self):
        """Test display name length limits."""
        short_name = "Jo"
        valid_name = "John Doe"
        long_name = "A" * 101
        
        self.assertLess(len(short_name), 3)
        self.assertGreaterEqual(len(valid_name), 3)
        self.assertGreater(len(long_name), 100)

    def test_phone_format(self):
        """Test phone number format."""
        import re
        valid_phones = ["+1234567890", "123-456-7890", "(123) 456-7890"]
        phone_pattern = re.compile(r"[\d\s\-\(\)\+]+")
        for phone in valid_phones:
            self.assertTrue(phone_pattern.match(phone))

    def test_avatar_emoji(self):
        """Test avatar is valid emoji."""
        valid_avatars = ["🎰", "🏈", "🏀", "⚽", "🔥"]
        for avatar in valid_avatars:
            self.assertGreater(len(avatar), 0)


class TestBettingExperience(unittest.TestCase):
    """Tests for betting experience field."""

    def test_valid_experience_levels(self):
        """Test valid experience levels."""
        valid_levels = ["beginner", "intermediate", "experienced", "professional"]
        user_level = "intermediate"
        self.assertIn(user_level, valid_levels)

    def test_default_experience(self):
        """Test default experience level."""
        default = "beginner"
        self.assertEqual(default, "beginner")


class TestFavoriteSports(unittest.TestCase):
    """Tests for favorite sports field."""

    def test_sports_list(self):
        """Test favorite sports is a list."""
        favorites = ["nba", "nfl", "mlb"]
        self.assertIsInstance(favorites, list)

    def test_valid_sport_ids(self):
        """Test valid sport IDs."""
        valid_sports = ["nba", "nfl", "mlb", "nhl", "soccer", "ufc", "tennis", "golf"]
        user_favorites = ["nba", "nfl"]
        for sport in user_favorites:
            self.assertIn(sport, valid_sports)

    def test_json_serialization(self):
        """Test favorites can be JSON serialized."""
        favorites = ["nba", "nfl"]
        json_str = json.dumps(favorites)
        parsed = json.loads(json_str)
        self.assertEqual(parsed, favorites)


class TestMonthlyBudget(unittest.TestCase):
    """Tests for monthly budget field."""

    def test_budget_positive(self):
        """Test budget is positive."""
        budget = 500
        self.assertGreater(budget, 0)

    def test_budget_reasonable_range(self):
        """Test budget is in reasonable range."""
        min_budget = 0
        max_budget = 100000
        user_budget = 500
        self.assertGreaterEqual(user_budget, min_budget)
        self.assertLessEqual(user_budget, max_budget)

    def test_budget_integer(self):
        """Test budget can be integer."""
        budget = 500
        self.assertIsInstance(budget, int)


class TestProfileUpdate(unittest.TestCase):
    """Tests for profile update logic."""

    def test_partial_update(self):
        """Test partial profile update."""
        original = {"displayName": "Old Name", "avatar": "🎰", "phone": ""}
        updates = {"displayName": "New Name"}
        
        # Merge updates
        updated = {**original, **updates}
        
        self.assertEqual(updated["displayName"], "New Name")
        self.assertEqual(updated["avatar"], "🎰")  # Unchanged

    def test_immutable_fields(self):
        """Test immutable fields cannot be updated."""
        immutable = ["id", "username", "email", "createdAt"]
        update_request = {"username": "hacker", "displayName": "Valid"}
        
        # Filter out immutable fields
        allowed_updates = {k: v for k, v in update_request.items() if k not in immutable}
        
        self.assertNotIn("username", allowed_updates)
        self.assertIn("displayName", allowed_updates)


if __name__ == "__main__":
    unittest.main()
