"""
Tests for sports data integration and multi-leg parlay analysis.

These tests cover the NBA data fetching, team analysis, matchup analysis,
and the new multi-leg parlay slider feature.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.sports_data import (
    get_team_analysis,
    get_matchup_analysis,
    get_enhanced_bet_analysis,
    get_multi_leg_analysis,
    extract_teams_from_bet,
    generate_betting_insight,
    TEAM_ALIASES,
    MOCK_TEAM_STATS
)


class TestTeamAliases(unittest.TestCase):
    """Tests for team alias mapping."""

    def test_common_aliases_exist(self):
        """Test that common team aliases are mapped."""
        self.assertIn('lakers', TEAM_ALIASES)
        self.assertIn('celtics', TEAM_ALIASES)
        self.assertIn('warriors', TEAM_ALIASES)

    def test_alias_maps_to_full_name(self):
        """Test that aliases map to full team names."""
        self.assertEqual(TEAM_ALIASES['lakers'], 'Los Angeles Lakers')
        self.assertEqual(TEAM_ALIASES['celtics'], 'Boston Celtics')
        self.assertEqual(TEAM_ALIASES['cavs'], 'Cleveland Cavaliers')

    def test_all_30_teams_have_stats(self):
        """Test that all 30 NBA teams have mock stats."""
        self.assertEqual(len(MOCK_TEAM_STATS), 30)


class TestGetTeamAnalysis(unittest.TestCase):
    """Tests for individual team analysis."""

    def test_get_team_by_alias(self):
        """Test getting team analysis by alias."""
        result = get_team_analysis('lakers')
        self.assertIsNotNone(result)
        self.assertEqual(result['team'], 'Los Angeles Lakers')
        self.assertEqual(result['abbreviation'], 'LAL')

    def test_get_team_has_all_fields(self):
        """Test that team analysis has all required fields."""
        result = get_team_analysis('celtics')
        required_fields = ['team', 'abbreviation', 'record', 'winPercentage', 
                          'recentForm', 'avgPointsScored', 'avgPointsAllowed', 
                          'pointsDifferential', 'gamesAnalyzed']
        for field in required_fields:
            self.assertIn(field, result)

    def test_win_percentage_calculation(self):
        """Test win percentage is calculated correctly."""
        result = get_team_analysis('thunder')
        # Thunder is 22-5, win% should be ~81.5%
        self.assertGreater(result['winPercentage'], 80)
        self.assertLess(result['winPercentage'], 85)

    def test_invalid_team_returns_none(self):
        """Test that invalid team name returns None."""
        result = get_team_analysis('faketeam')
        self.assertIsNone(result)

    def test_partial_match_works(self):
        """Test that partial team name matching works."""
        result = get_team_analysis('cavaliers')
        self.assertIsNotNone(result)
        self.assertEqual(result['abbreviation'], 'CLE')


class TestGetMatchupAnalysis(unittest.TestCase):
    """Tests for matchup analysis between two teams."""

    def test_basic_matchup(self):
        """Test basic matchup analysis."""
        result = get_matchup_analysis('lakers', 'celtics')
        self.assertIsNotNone(result)
        self.assertIn('team1', result)
        self.assertIn('team2', result)
        self.assertIn('headToHead', result)

    def test_matchup_has_head_to_head(self):
        """Test that matchup includes head-to-head data."""
        result = get_matchup_analysis('thunder', 'nuggets')
        h2h = result['headToHead']
        self.assertIn('team1Wins', h2h)
        self.assertIn('team2Wins', h2h)
        self.assertIn('gamesPlayed', h2h)

    def test_matchup_with_invalid_team(self):
        """Test matchup with one invalid team."""
        result = get_matchup_analysis('lakers', 'faketeam')
        self.assertIsNone(result)

    def test_matchup_teams_have_stats(self):
        """Test that both teams in matchup have complete stats."""
        result = get_matchup_analysis('rockets', 'grizzlies')
        self.assertIsNotNone(result['team1']['avgPointsScored'])
        self.assertIsNotNone(result['team2']['avgPointsScored'])


class TestExtractTeamsFromBet(unittest.TestCase):
    """Tests for extracting team names from bet text."""

    def test_extract_vs_format(self):
        """Test extracting teams from 'vs' format."""
        team1, team2 = extract_teams_from_bet('Lakers vs Celtics -5.5')
        self.assertIsNotNone(team1)
        self.assertIsNotNone(team2)

    def test_extract_at_format(self):
        """Test extracting teams from '@' format."""
        team1, team2 = extract_teams_from_bet('Lakers @ Celtics')
        self.assertIsNotNone(team1)

    def test_single_team_mention(self):
        """Test extracting when only one team mentioned."""
        team1, team2 = extract_teams_from_bet('Cavaliers moneyline')
        self.assertEqual(team1, 'cavaliers')
        self.assertIsNone(team2)

    def test_no_teams_found(self):
        """Test when no teams are found."""
        team1, team2 = extract_teams_from_bet('some random text')
        self.assertIsNone(team1)
        self.assertIsNone(team2)


class TestGenerateBettingInsight(unittest.TestCase):
    """Tests for AI betting insight generation."""

    def test_insight_generation_basic(self):
        """Test basic insight generation."""
        matchup = get_matchup_analysis('thunder', 'nuggets')
        insight = generate_betting_insight(matchup, 'spread', -3.5)
        self.assertIsInstance(insight, str)
        self.assertGreater(len(insight), 10)

    def test_insight_includes_hot_team(self):
        """Test that insight mentions hot teams."""
        matchup = get_matchup_analysis('cavaliers', 'celtics')
        insight = generate_betting_insight(matchup)
        # Both teams are hot, should mention at least one
        self.assertTrue('HOT' in insight or 'record' in insight.lower())

    def test_insight_includes_projected_score(self):
        """Test that insight includes projected score."""
        matchup = get_matchup_analysis('lakers', 'warriors')
        insight = generate_betting_insight(matchup)
        self.assertIn('Projected score', insight)

    def test_insight_with_none_matchup(self):
        """Test insight with no matchup data."""
        insight = generate_betting_insight(None)
        self.assertEqual(insight, "Unable to fetch team data for analysis.")


class TestGetEnhancedBetAnalysis(unittest.TestCase):
    """Tests for enhanced bet analysis with live data."""

    def test_single_leg_bet(self):
        """Test analysis of single leg bet."""
        result = get_enhanced_bet_analysis('Lakers vs Celtics -5.5 @ -110')
        self.assertIsNotNone(result)
        self.assertTrue(result['hasData'])
        self.assertIsNotNone(result['matchup'])

    def test_single_leg_has_insight(self):
        """Test that single leg has insight."""
        result = get_enhanced_bet_analysis('Thunder vs Nuggets -3.5')
        self.assertIn('insight', result)
        self.assertIsInstance(result['insight'], str)

    def test_single_team_bet(self):
        """Test analysis of single team mention."""
        result = get_enhanced_bet_analysis('Cavaliers moneyline @ -150')
        self.assertIsNotNone(result)
        self.assertTrue(result['hasData'])
        self.assertIsNotNone(result.get('team'))

    def test_no_team_returns_none(self):
        """Test that bet with no team returns None."""
        result = get_enhanced_bet_analysis('random text without teams')
        self.assertIsNone(result)


class TestMultiLegAnalysis(unittest.TestCase):
    """Tests for multi-leg parlay analysis (slider feature)."""

    def test_multi_leg_comma_separated(self):
        """Test parsing comma-separated multi-leg bet."""
        result = get_enhanced_bet_analysis(
            'Thunder vs Nuggets -3.5 @ -110, Cavaliers moneyline @ -150, Grizzlies vs Rockets Over 220.5 @ -105'
        )
        self.assertIsNotNone(result)
        self.assertTrue(result['hasData'])
        self.assertIsNotNone(result.get('allMatchups'))

    def test_multi_leg_newline_separated(self):
        """Test parsing newline-separated multi-leg bet."""
        result = get_enhanced_bet_analysis(
            'Lakers vs Celtics -5.5 @ -110\nWarriors moneyline @ +150\nBucks vs Knicks Over 220 @ -105'
        )
        self.assertIsNotNone(result)
        self.assertIsNotNone(result.get('allMatchups'))

    def test_multi_leg_returns_all_matchups(self):
        """Test that multi-leg returns all matchups."""
        result = get_enhanced_bet_analysis(
            'Thunder vs Nuggets @ -110, Rockets vs Grizzlies @ +120'
        )
        self.assertIn('allMatchups', result)
        self.assertEqual(len(result['allMatchups']), 2)

    def test_multi_leg_total_matchups_count(self):
        """Test totalMatchups count is correct."""
        result = get_enhanced_bet_analysis(
            'Lakers vs Celtics, Warriors vs Suns, Bulls vs Knicks'
        )
        self.assertEqual(result['totalMatchups'], 3)

    def test_multi_leg_each_matchup_has_leg_number(self):
        """Test each matchup has leg number."""
        result = get_enhanced_bet_analysis(
            'Thunder vs Nuggets, Cavaliers vs Celtics'
        )
        for idx, matchup in enumerate(result['allMatchups']):
            self.assertIn('legNumber', matchup)
            self.assertEqual(matchup['legNumber'], idx + 1)

    def test_multi_leg_each_matchup_has_bet_line(self):
        """Test each matchup preserves original bet line."""
        result = get_enhanced_bet_analysis(
            'Lakers vs Celtics -5.5 @ -110, Warriors moneyline @ +150'
        )
        self.assertIn('betLine', result['allMatchups'][0])
        self.assertIn('Lakers', result['allMatchups'][0]['betLine'])

    def test_multi_leg_each_matchup_has_insight(self):
        """Test each matchup has its own insight."""
        result = get_enhanced_bet_analysis(
            'Thunder vs Nuggets @ -110, Rockets vs Grizzlies @ +120'
        )
        for matchup in result['allMatchups']:
            self.assertIn('insight', matchup)
            self.assertIsInstance(matchup['insight'], str)

    def test_multi_leg_combined_insight(self):
        """Test that multi-leg has combined insight."""
        result = get_enhanced_bet_analysis(
            'Thunder vs Nuggets, Cavaliers vs Celtics'
        )
        # Combined insight should mention hot teams
        self.assertIn('insight', result)
        self.assertGreater(len(result['insight']), 20)

    def test_multi_leg_includes_single_team_bets(self):
        """Test that multi-leg handles single team mentions."""
        result = get_enhanced_bet_analysis(
            'Cavaliers moneyline @ -150, Lakers vs Celtics @ -110'
        )
        self.assertEqual(len(result['allMatchups']), 2)
        # First should be single team (Cavaliers)
        self.assertIsNotNone(result['allMatchups'][0].get('team'))
        # Second should be matchup
        self.assertIsNotNone(result['allMatchups'][1].get('matchup'))

    def test_multi_leg_first_matchup_is_default(self):
        """Test that first matchup is used as default display."""
        result = get_enhanced_bet_analysis(
            'Thunder vs Nuggets @ -110, Lakers vs Celtics @ -110'
        )
        # The default 'matchup' should match the first allMatchups entry
        self.assertEqual(
            result['matchup']['team1']['abbreviation'],
            result['allMatchups'][0]['matchup']['team1']['abbreviation']
        )


class TestMultiLegDirectFunction(unittest.TestCase):
    """Tests for the get_multi_leg_analysis function directly."""

    def test_direct_function_call(self):
        """Test calling get_multi_leg_analysis directly."""
        lines = [
            'Thunder vs Nuggets -3.5',
            'Cavaliers moneyline',
            'Grizzlies vs Rockets Over 220.5'
        ]
        result = get_multi_leg_analysis(lines)
        self.assertIsNotNone(result)
        self.assertEqual(len(result['allMatchups']), 3)

    def test_empty_list_returns_none(self):
        """Test that empty list returns None."""
        result = get_multi_leg_analysis([])
        self.assertIsNone(result)

    def test_no_valid_teams_returns_none(self):
        """Test that no valid teams returns None."""
        lines = ['random text', 'more random text']
        result = get_multi_leg_analysis(lines)
        self.assertIsNone(result)

    def test_partial_valid_lines(self):
        """Test with some valid and some invalid lines."""
        lines = [
            'Lakers vs Celtics',
            'random text',
            'Thunder vs Nuggets'
        ]
        result = get_multi_leg_analysis(lines)
        self.assertIsNotNone(result)
        self.assertEqual(len(result['allMatchups']), 2)


class TestTeamStats(unittest.TestCase):
    """Tests for mock team stats data integrity."""

    def test_all_teams_have_required_fields(self):
        """Test all teams have required stat fields."""
        required_fields = ['abbr', 'wins', 'losses', 'ppg', 'opp_ppg', 'form']
        for team, stats in MOCK_TEAM_STATS.items():
            for field in required_fields:
                self.assertIn(field, stats, f"{team} missing {field}")

    def test_win_loss_totals_reasonable(self):
        """Test that win/loss totals are reasonable for mid-season."""
        for team, stats in MOCK_TEAM_STATS.items():
            total_games = stats['wins'] + stats['losses']
            self.assertGreater(total_games, 10, f"{team} has too few games")
            self.assertLess(total_games, 82, f"{team} has too many games")

    def test_ppg_values_reasonable(self):
        """Test that PPG values are in reasonable NBA range."""
        for team, stats in MOCK_TEAM_STATS.items():
            self.assertGreater(stats['ppg'], 95, f"{team} PPG too low")
            self.assertLess(stats['ppg'], 130, f"{team} PPG too high")

    def test_form_string_format(self):
        """Test that form strings are properly formatted."""
        for team, stats in MOCK_TEAM_STATS.items():
            form = stats['form']
            self.assertIsInstance(form, str)
            # Should contain W and/or L
            self.assertTrue(any(c in form for c in ['W', 'L']), 
                          f"{team} form '{form}' invalid")


if __name__ == '__main__':
    unittest.main()
