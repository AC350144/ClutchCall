"""
Essential tests for bet parsing functionality.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.bet_parser import (
    parse_american_odds,
    detect_sport,
    detect_bet_type,
    extract_odds,
    calculate_implied_probability,
    calculate_parlay_odds,
    calculate_payout,
    parse_bet_text,
    get_stake_recommendation
)


class TestParseAmericanOdds(unittest.TestCase):
    """Tests for parsing American odds."""

    def test_negative_odds(self):
        """Test parsing negative odds."""
        self.assertEqual(parse_american_odds("-110"), -110)
        self.assertEqual(parse_american_odds("-150"), -150)

    def test_positive_odds(self):
        """Test parsing positive odds."""
        self.assertEqual(parse_american_odds("+150"), 150)
        self.assertEqual(parse_american_odds("+200"), 200)

    def test_invalid_odds(self):
        """Test parsing invalid odds."""
        self.assertIsNone(parse_american_odds("abc"))
        self.assertIsNone(parse_american_odds(""))


class TestDetectSport(unittest.TestCase):
    """Tests for sport detection."""

    def test_nba_detection(self):
        """Test NBA detection."""
        self.assertEqual(detect_sport("Lakers vs Celtics NBA"), "NBA")

    def test_nfl_detection(self):
        """Test NFL detection."""
        self.assertEqual(detect_sport("Chiefs vs Eagles NFL"), "NFL")

    def test_mlb_detection(self):
        """Test MLB detection."""
        self.assertEqual(detect_sport("Yankees vs Red Sox MLB"), "MLB")

    def test_unknown_sport(self):
        """Test unknown sport."""
        self.assertEqual(detect_sport("Some random text"), "Unknown")


class TestDetectBetType(unittest.TestCase):
    """Tests for bet type detection."""

    def test_spread_detection(self):
        """Test spread bet detection."""
        self.assertEqual(detect_bet_type("Lakers -5.5"), "Spread")

    def test_moneyline_detection(self):
        """Test moneyline bet detection."""
        self.assertEqual(detect_bet_type("Lakers moneyline"), "Moneyline")

    def test_total_detection(self):
        """Test over/under detection."""
        self.assertEqual(detect_bet_type("Over 220.5"), "Total")


class TestExtractOdds(unittest.TestCase):
    """Tests for odds extraction."""

    def test_single_odds(self):
        """Test extracting single odds."""
        odds = extract_odds("Lakers @ -110")
        self.assertIn(-110, odds)

    def test_multiple_odds(self):
        """Test extracting multiple odds."""
        odds = extract_odds("Lakers @ -110, Celtics @ +150")
        self.assertIn(-110, odds)
        self.assertIn(150, odds)

    def test_no_odds(self):
        """Test no odds in text."""
        odds = extract_odds("Lakers vs Celtics")
        self.assertEqual(odds, [])

    def test_odds_without_at_symbol(self):
        """Test extracting odds without @ symbol."""
        odds = extract_odds("Lakers ML +500")
        self.assertIn(500, odds)

    def test_odds_with_moneyline_keyword(self):
        """Test extracting odds with moneyline keyword."""
        odds = extract_odds("Lakers moneyline +350")
        self.assertIn(350, odds)

    def test_odds_at_end_of_string(self):
        """Test extracting odds at the end of the string."""
        odds = extract_odds("Lakers +500")
        self.assertIn(500, odds)

    def test_odds_standalone(self):
        """Test extracting standalone odds."""
        odds = extract_odds("+500")
        self.assertIn(500, odds)

    def test_odds_with_vs_matchup(self):
        """Test extracting odds from matchup format."""
        odds = extract_odds("Lakers vs Celtics ML +500")
        self.assertIn(500, odds)


class TestCalculateImpliedProbability(unittest.TestCase):
    """Tests for implied probability calculation."""

    def test_favorite_odds(self):
        """Test implied probability for favorites."""
        prob = calculate_implied_probability(-110)
        self.assertAlmostEqual(prob, 0.524, places=2)

    def test_underdog_odds(self):
        """Test implied probability for underdogs."""
        prob = calculate_implied_probability(150)
        self.assertAlmostEqual(prob, 0.4, places=2)


class TestCalculateParlayOdds(unittest.TestCase):
    """Tests for parlay odds calculation."""

    def test_two_leg_parlay(self):
        """Test two-leg parlay calculation."""
        odds = calculate_parlay_odds([-110, -110])
        self.assertIsInstance(odds, int)
        self.assertGreater(odds, 0)  # Two -110 legs should result in positive odds

    def test_empty_list(self):
        """Test empty odds list."""
        odds = calculate_parlay_odds([])
        self.assertEqual(odds, 0)

    def test_single_leg(self):
        """Test single leg returns some value."""
        odds = calculate_parlay_odds([-110])
        self.assertIsInstance(odds, int)


class TestCalculatePayout(unittest.TestCase):
    """Tests for payout calculation."""

    def test_negative_odds_payout(self):
        """Test payout for negative odds."""
        payout = calculate_payout(110, -110)
        self.assertGreater(payout, 0)

    def test_positive_odds_payout(self):
        """Test payout for positive odds."""
        payout = calculate_payout(100, 150)
        self.assertAlmostEqual(payout, 150, places=0)

    def test_zero_stake(self):
        """Test zero stake returns zero."""
        payout = calculate_payout(0, 150)
        self.assertEqual(payout, 0)


class TestParseBetText(unittest.TestCase):
    """Tests for full bet text parsing."""

    def test_simple_bet(self):
        """Test parsing simple bet."""
        result = parse_bet_text("Lakers -5.5 (-110)")
        self.assertIn("legs", result)
        self.assertIn("totalOdds", result)

    def test_empty_text(self):
        """Test parsing empty text."""
        result = parse_bet_text("")
        self.assertIn("legs", result)
        self.assertEqual(len(result["legs"]), 0)

    def test_result_structure(self):
        """Test result has expected structure."""
        result = parse_bet_text("Lakers -110")
        self.assertIn("legs", result)
        self.assertIn("totalOdds", result)
        self.assertIn("qualityScore", result)
        self.assertIn("analysis", result)
        self.assertIn("recommendation", result)


class TestGetStakeRecommendation(unittest.TestCase):
    """Tests for stake recommendations."""

    def test_good_recommendation_stake(self):
        """Test stake for good recommendation."""
        rec = get_stake_recommendation(1000, 80, "good")
        self.assertIn("recommended", rec)
        self.assertGreater(rec["recommended"], 0)

    def test_zero_bankroll(self):
        """Test zero bankroll returns zero stake."""
        rec = get_stake_recommendation(0, 80, "good")
        self.assertEqual(rec["recommended"], 0)

    def test_bankroll_scaling(self):
        """Test stake scales with bankroll."""
        rec1 = get_stake_recommendation(1000, 80, "good")
        rec2 = get_stake_recommendation(2000, 80, "good")
        self.assertLess(rec1["recommended"], rec2["recommended"])


if __name__ == "__main__":
    unittest.main()
