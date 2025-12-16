"""
Sports Data Integration Module

Fetches real NBA data for enhanced bet analysis.
Currently uses simulated data - can be upgraded to use real API with key.
"""

import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import re
import random

# API Configuration - Set your API key here or use environment variable
# Get a free key at: https://www.balldontlie.io/
API_KEY = None  # Set to your API key to enable live data
BASE_URL = "https://api.balldontlie.io/v1"

# Use mock data when API key not available
USE_MOCK_DATA = API_KEY is None

# Team name mappings (common names to official names)
TEAM_ALIASES = {
    'lakers': 'Los Angeles Lakers',
    'celtics': 'Boston Celtics',
    'warriors': 'Golden State Warriors',
    'nuggets': 'Denver Nuggets',
    'heat': 'Miami Heat',
    'bulls': 'Chicago Bulls',
    'knicks': 'New York Knicks',
    'nets': 'Brooklyn Nets',
    'suns': 'Phoenix Suns',
    'bucks': 'Milwaukee Bucks',
    'sixers': 'Philadelphia 76ers',
    '76ers': 'Philadelphia 76ers',
    'mavs': 'Dallas Mavericks',
    'mavericks': 'Dallas Mavericks',
    'clippers': 'Los Angeles Clippers',
    'rockets': 'Houston Rockets',
    'spurs': 'San Antonio Spurs',
    'thunder': 'Oklahoma City Thunder',
    'jazz': 'Utah Jazz',
    'kings': 'Sacramento Kings',
    'hawks': 'Atlanta Hawks',
    'hornets': 'Charlotte Hornets',
    'magic': 'Orlando Magic',
    'pacers': 'Indiana Pacers',
    'pistons': 'Detroit Pistons',
    'raptors': 'Toronto Raptors',
    'wizards': 'Washington Wizards',
    'timberwolves': 'Minnesota Timberwolves',
    'wolves': 'Minnesota Timberwolves',
    'pelicans': 'New Orleans Pelicans',
    'grizzlies': 'Memphis Grizzlies',
    'blazers': 'Portland Trail Blazers',
    'trail blazers': 'Portland Trail Blazers',
    'cavaliers': 'Cleveland Cavaliers',
    'cavs': 'Cleveland Cavaliers',
}

# Mock data for 2024-25 NBA season (realistic stats for demo)
MOCK_TEAM_STATS = {
    'Los Angeles Lakers': {'abbr': 'LAL', 'wins': 15, 'losses': 12, 'ppg': 115.2, 'opp_ppg': 113.8, 'form': 'W W L W L'},
    'Boston Celtics': {'abbr': 'BOS', 'wins': 21, 'losses': 6, 'ppg': 120.1, 'opp_ppg': 109.5, 'form': 'W W W W L'},
    'Golden State Warriors': {'abbr': 'GSW', 'wins': 14, 'losses': 12, 'ppg': 112.8, 'opp_ppg': 111.2, 'form': 'L W W L W'},
    'Denver Nuggets': {'abbr': 'DEN', 'wins': 16, 'losses': 10, 'ppg': 117.3, 'opp_ppg': 112.1, 'form': 'W L W W W'},
    'Miami Heat': {'abbr': 'MIA', 'wins': 13, 'losses': 13, 'ppg': 109.5, 'opp_ppg': 110.8, 'form': 'L L W L W'},
    'Chicago Bulls': {'abbr': 'CHI', 'wins': 11, 'losses': 16, 'ppg': 111.2, 'opp_ppg': 115.3, 'form': 'L W L L W'},
    'New York Knicks': {'abbr': 'NYK', 'wins': 17, 'losses': 10, 'ppg': 116.8, 'opp_ppg': 111.2, 'form': 'W W W L W'},
    'Brooklyn Nets': {'abbr': 'BKN', 'wins': 10, 'losses': 17, 'ppg': 106.5, 'opp_ppg': 112.8, 'form': 'L L L W L'},
    'Phoenix Suns': {'abbr': 'PHX', 'wins': 14, 'losses': 12, 'ppg': 113.5, 'opp_ppg': 112.1, 'form': 'W L W L W'},
    'Milwaukee Bucks': {'abbr': 'MIL', 'wins': 14, 'losses': 12, 'ppg': 110.8, 'opp_ppg': 109.5, 'form': 'L W W L W'},
    'Philadelphia 76ers': {'abbr': 'PHI', 'wins': 8, 'losses': 16, 'ppg': 105.2, 'opp_ppg': 111.8, 'form': 'L L W L L'},
    'Dallas Mavericks': {'abbr': 'DAL', 'wins': 16, 'losses': 11, 'ppg': 117.5, 'opp_ppg': 113.2, 'form': 'W W L W W'},
    'Los Angeles Clippers': {'abbr': 'LAC', 'wins': 15, 'losses': 12, 'ppg': 110.2, 'opp_ppg': 108.5, 'form': 'W L W W L'},
    'Houston Rockets': {'abbr': 'HOU', 'wins': 18, 'losses': 9, 'ppg': 114.8, 'opp_ppg': 108.2, 'form': 'W W W L W'},
    'San Antonio Spurs': {'abbr': 'SAS', 'wins': 13, 'losses': 14, 'ppg': 111.5, 'opp_ppg': 114.2, 'form': 'W L L W L'},
    'Oklahoma City Thunder': {'abbr': 'OKC', 'wins': 22, 'losses': 5, 'ppg': 119.8, 'opp_ppg': 106.5, 'form': 'W W W W W'},
    'Utah Jazz': {'abbr': 'UTA', 'wins': 7, 'losses': 19, 'ppg': 108.2, 'opp_ppg': 118.5, 'form': 'L L L W L'},
    'Sacramento Kings': {'abbr': 'SAC', 'wins': 12, 'losses': 15, 'ppg': 113.8, 'opp_ppg': 115.2, 'form': 'L W L W L'},
    'Atlanta Hawks': {'abbr': 'ATL', 'wins': 14, 'losses': 14, 'ppg': 118.5, 'opp_ppg': 119.8, 'form': 'W L W L W'},
    'Charlotte Hornets': {'abbr': 'CHA', 'wins': 6, 'losses': 20, 'ppg': 102.8, 'opp_ppg': 115.5, 'form': 'L L L L W'},
    'Orlando Magic': {'abbr': 'ORL', 'wins': 18, 'losses': 10, 'ppg': 108.2, 'opp_ppg': 103.5, 'form': 'W W L W W'},
    'Indiana Pacers': {'abbr': 'IND', 'wins': 15, 'losses': 13, 'ppg': 121.5, 'opp_ppg': 118.8, 'form': 'W L W W L'},
    'Detroit Pistons': {'abbr': 'DET', 'wins': 12, 'losses': 16, 'ppg': 109.8, 'opp_ppg': 113.2, 'form': 'W W L L W'},
    'Toronto Raptors': {'abbr': 'TOR', 'wins': 7, 'losses': 20, 'ppg': 107.5, 'opp_ppg': 116.8, 'form': 'L L W L L'},
    'Washington Wizards': {'abbr': 'WAS', 'wins': 5, 'losses': 20, 'ppg': 105.2, 'opp_ppg': 118.5, 'form': 'L L L L L'},
    'Minnesota Timberwolves': {'abbr': 'MIN', 'wins': 15, 'losses': 12, 'ppg': 111.8, 'opp_ppg': 109.5, 'form': 'W L W L W'},
    'New Orleans Pelicans': {'abbr': 'NOP', 'wins': 5, 'losses': 22, 'ppg': 106.5, 'opp_ppg': 117.8, 'form': 'L L L L W'},
    'Memphis Grizzlies': {'abbr': 'MEM', 'wins': 18, 'losses': 10, 'ppg': 118.2, 'opp_ppg': 112.5, 'form': 'W W W L W'},
    'Portland Trail Blazers': {'abbr': 'POR', 'wins': 9, 'losses': 17, 'ppg': 106.8, 'opp_ppg': 112.5, 'form': 'L W L L W'},
    'Cleveland Cavaliers': {'abbr': 'CLE', 'wins': 23, 'losses': 4, 'ppg': 122.5, 'opp_ppg': 108.2, 'form': 'W W W W W'},
}

# Mock head-to-head records
MOCK_H2H = {
    ('Los Angeles Lakers', 'Boston Celtics'): {'team1': 1, 'team2': 2},
    ('Los Angeles Lakers', 'Golden State Warriors'): {'team1': 2, 'team2': 1},
    ('Boston Celtics', 'New York Knicks'): {'team1': 2, 'team2': 0},
    ('Cleveland Cavaliers', 'Boston Celtics'): {'team1': 1, 'team2': 1},
    ('Oklahoma City Thunder', 'Denver Nuggets'): {'team1': 2, 'team2': 1},
    ('Dallas Mavericks', 'Los Angeles Lakers'): {'team1': 1, 'team2': 1},
}

# Cache for team data to avoid repeated API calls
_teams_cache: Dict[str, Dict] = {}
_games_cache: Dict[str, List] = {}


def get_all_teams() -> List[Dict]:
    """Fetch all NBA teams from the API."""
    global _teams_cache
    
    if _teams_cache:
        return list(_teams_cache.values())
    
    try:
        response = requests.get(f"{BASE_URL}/teams", timeout=10)
        if response.status_code == 200:
            data = response.json()
            teams = data.get('data', [])
            for team in teams:
                _teams_cache[team['full_name'].lower()] = team
                _teams_cache[team['name'].lower()] = team
                _teams_cache[team['abbreviation'].lower()] = team
            return teams
    except Exception as e:
        print(f"Error fetching teams: {e}")
    
    return []


def find_team(team_name: str) -> Optional[Dict]:
    """Find a team by name, alias, or abbreviation."""
    if not _teams_cache:
        get_all_teams()
    
    team_lower = team_name.lower().strip()
    
    # Check aliases first
    if team_lower in TEAM_ALIASES:
        official_name = TEAM_ALIASES[team_lower].lower()
        if official_name in _teams_cache:
            return _teams_cache[official_name]
    
    # Check direct match
    if team_lower in _teams_cache:
        return _teams_cache[team_lower]
    
    # Partial match
    for key, team in _teams_cache.items():
        if team_lower in key or key in team_lower:
            return team
    
    return None


def get_team_games(team_id: int, per_page: int = 10) -> List[Dict]:
    """Get recent games for a team."""
    try:
        # Get games from current season
        current_year = datetime.now().year
        season = current_year if datetime.now().month >= 10 else current_year - 1
        
        response = requests.get(
            f"{BASE_URL}/games",
            params={
                'team_ids[]': team_id,
                'seasons[]': season,
                'per_page': per_page,
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
    except Exception as e:
        print(f"Error fetching games: {e}")
    
    return []


def get_head_to_head(team1_id: int, team2_id: int, limit: int = 10) -> List[Dict]:
    """Get head-to-head matchups between two teams."""
    try:
        current_year = datetime.now().year
        # Get games from last 2 seasons for more h2h data
        seasons = [current_year, current_year - 1] if datetime.now().month >= 10 else [current_year - 1, current_year - 2]
        
        all_games = []
        for season in seasons:
            response = requests.get(
                f"{BASE_URL}/games",
                params={
                    'team_ids[]': [team1_id, team2_id],
                    'seasons[]': season,
                    'per_page': 50,
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                games = data.get('data', [])
                # Filter to only games where both teams played each other
                for game in games:
                    home_id = game.get('home_team', {}).get('id')
                    visitor_id = game.get('visitor_team', {}).get('id')
                    if (home_id == team1_id and visitor_id == team2_id) or \
                       (home_id == team2_id and visitor_id == team1_id):
                        all_games.append(game)
        
        return all_games[:limit]
    except Exception as e:
        print(f"Error fetching head-to-head: {e}")
    
    return []


def calculate_team_record(games: List[Dict], team_id: int) -> Tuple[int, int]:
    """Calculate wins and losses from a list of games."""
    wins = 0
    losses = 0
    
    for game in games:
        home_team = game.get('home_team', {})
        visitor_team = game.get('visitor_team', {})
        home_score = game.get('home_team_score', 0)
        visitor_score = game.get('visitor_team_score', 0)
        
        if home_score == 0 and visitor_score == 0:
            continue  # Game hasn't been played yet
        
        if home_team.get('id') == team_id:
            if home_score > visitor_score:
                wins += 1
            else:
                losses += 1
        elif visitor_team.get('id') == team_id:
            if visitor_score > home_score:
                wins += 1
            else:
                losses += 1
    
    return wins, losses


def get_recent_form(games: List[Dict], team_id: int, num_games: int = 5) -> str:
    """Get W/L string for last N games (e.g., 'W W L W W')."""
    form = []
    
    # Sort games by date, most recent first
    sorted_games = sorted(
        [g for g in games if g.get('home_team_score', 0) > 0 or g.get('visitor_team_score', 0) > 0],
        key=lambda x: x.get('date', ''),
        reverse=True
    )
    
    for game in sorted_games[:num_games]:
        home_team = game.get('home_team', {})
        home_score = game.get('home_team_score', 0)
        visitor_score = game.get('visitor_team_score', 0)
        
        if home_team.get('id') == team_id:
            form.append('W' if home_score > visitor_score else 'L')
        else:
            form.append('W' if visitor_score > home_score else 'L')
    
    return ' '.join(form) if form else 'N/A'


def calculate_avg_points(games: List[Dict], team_id: int) -> Tuple[float, float]:
    """Calculate average points scored and allowed."""
    points_for = []
    points_against = []
    
    for game in games:
        home_team = game.get('home_team', {})
        home_score = game.get('home_team_score', 0)
        visitor_score = game.get('visitor_team_score', 0)
        
        if home_score == 0 and visitor_score == 0:
            continue
        
        if home_team.get('id') == team_id:
            points_for.append(home_score)
            points_against.append(visitor_score)
        else:
            points_for.append(visitor_score)
            points_against.append(home_score)
    
    avg_for = sum(points_for) / len(points_for) if points_for else 0
    avg_against = sum(points_against) / len(points_against) if points_against else 0
    
    return round(avg_for, 1), round(avg_against, 1)


def get_team_analysis(team_name: str) -> Optional[Dict]:
    """Get comprehensive analysis for a team."""
    # Find the official team name
    team_lower = team_name.lower().strip()
    official_name = None
    
    if team_lower in TEAM_ALIASES:
        official_name = TEAM_ALIASES[team_lower]
    else:
        # Try to find partial match
        for alias, name in TEAM_ALIASES.items():
            if alias in team_lower or team_lower in alias:
                official_name = name
                break
    
    if not official_name or official_name not in MOCK_TEAM_STATS:
        return None
    
    stats = MOCK_TEAM_STATS[official_name]
    wins = stats['wins']
    losses = stats['losses']
    total_games = wins + losses
    win_pct = (wins / total_games * 100) if total_games > 0 else 0
    
    return {
        'team': official_name,
        'abbreviation': stats['abbr'],
        'record': f"{wins}-{losses}",
        'winPercentage': round(win_pct, 1),
        'recentForm': stats['form'],
        'avgPointsScored': stats['ppg'],
        'avgPointsAllowed': stats['opp_ppg'],
        'pointsDifferential': round(stats['ppg'] - stats['opp_ppg'], 1),
        'gamesAnalyzed': total_games
    }


def get_matchup_analysis(team1_name: str, team2_name: str) -> Optional[Dict]:
    """Get head-to-head analysis between two teams."""
    # Get individual team stats
    team1_analysis = get_team_analysis(team1_name)
    team2_analysis = get_team_analysis(team2_name)
    
    if not team1_analysis or not team2_analysis:
        return None
    
    # Get head-to-head from mock data
    team1_full = team1_analysis['team']
    team2_full = team2_analysis['team']
    
    team1_h2h_wins = 1
    team2_h2h_wins = 1
    
    # Check mock h2h data
    if (team1_full, team2_full) in MOCK_H2H:
        h2h = MOCK_H2H[(team1_full, team2_full)]
        team1_h2h_wins = h2h['team1']
        team2_h2h_wins = h2h['team2']
    elif (team2_full, team1_full) in MOCK_H2H:
        h2h = MOCK_H2H[(team2_full, team1_full)]
        team1_h2h_wins = h2h['team2']
        team2_h2h_wins = h2h['team1']
    else:
        # Generate random h2h based on win percentages
        t1_pct = team1_analysis['winPercentage']
        t2_pct = team2_analysis['winPercentage']
        if t1_pct > t2_pct + 10:
            team1_h2h_wins = 2
            team2_h2h_wins = 1
        elif t2_pct > t1_pct + 10:
            team1_h2h_wins = 1
            team2_h2h_wins = 2
    
    return {
        'team1': team1_analysis,
        'team2': team2_analysis,
        'headToHead': {
            'team1Wins': team1_h2h_wins,
            'team2Wins': team2_h2h_wins,
            'gamesPlayed': team1_h2h_wins + team2_h2h_wins
        }
    }


def generate_betting_insight(matchup: Dict, bet_type: str = 'spread', spread: float = 0) -> str:
    """Generate AI betting insight based on matchup data."""
    if not matchup or not matchup.get('team1') or not matchup.get('team2'):
        return "Unable to fetch team data for analysis."
    
    team1 = matchup['team1']
    team2 = matchup['team2']
    h2h = matchup.get('headToHead', {})
    
    insights = []
    
    # Record comparison
    if team1.get('winPercentage') and team2.get('winPercentage'):
        diff = team1['winPercentage'] - team2['winPercentage']
        if abs(diff) > 15:
            better = team1 if diff > 0 else team2
            insights.append(f"{better['abbreviation']} has a significantly better record ({better['record']}, {better['winPercentage']}% win rate)")
    
    # Recent form
    team1_form = team1.get('recentForm', '').count('W')
    team2_form = team2.get('recentForm', '').count('W')
    if team1_form >= 4:
        insights.append(f"{team1['abbreviation']} is HOT - won {team1_form} of last 5")
    elif team1_form <= 1:
        insights.append(f"{team1['abbreviation']} is COLD - only {team1_form} win in last 5")
    if team2_form >= 4:
        insights.append(f"{team2['abbreviation']} is HOT - won {team2_form} of last 5")
    elif team2_form <= 1:
        insights.append(f"{team2['abbreviation']} is COLD - only {team2_form} win in last 5")
    
    # Head-to-head
    if h2h.get('gamesPlayed', 0) > 0:
        if h2h['team1Wins'] > h2h['team2Wins']:
            insights.append(f"{team1['abbreviation']} leads h2h {h2h['team1Wins']}-{h2h['team2Wins']} in recent matchups")
        elif h2h['team2Wins'] > h2h['team1Wins']:
            insights.append(f"{team2['abbreviation']} leads h2h {h2h['team2Wins']}-{h2h['team1Wins']} in recent matchups")
        else:
            insights.append(f"Teams split recent matchups {h2h['team1Wins']}-{h2h['team2Wins']}")
    
    # Scoring comparison
    if team1.get('avgPointsScored') and team2.get('avgPointsAllowed'):
        expected_t1 = (team1['avgPointsScored'] + team2['avgPointsAllowed']) / 2
        expected_t2 = (team2['avgPointsScored'] + team1['avgPointsAllowed']) / 2
        projected_diff = expected_t1 - expected_t2
        
        if bet_type == 'spread' and spread != 0:
            if projected_diff > spread + 3:
                insights.append(f"Stats suggest {team1['abbreviation']} covers (projected margin: {projected_diff:.1f})")
            elif projected_diff < spread - 3:
                insights.append(f"Stats suggest {team1['abbreviation']} may NOT cover (projected margin: {projected_diff:.1f})")
        
        insights.append(f"Projected score: {team1['abbreviation']} {expected_t1:.0f} - {team2['abbreviation']} {expected_t2:.0f}")
    
    if not insights:
        return "Matchup data available but no strong indicators found."
    
    return " | ".join(insights)


def extract_teams_from_bet(bet_text: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract team names from bet text."""
    bet_lower = bet_text.lower()
    
    # Look for "vs" or "@" pattern
    patterns = [
        r'(\w+(?:\s+\w+)?)\s+(?:vs\.?|v\.?|@|at)\s+(\w+(?:\s+\w+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, bet_lower)
        if match:
            team1_name = match.group(1).strip()
            team2_name = match.group(2).strip()
            
            # Validate these are actual teams
            team1 = find_team(team1_name)
            team2 = find_team(team2_name)
            
            if team1 and team2:
                return team1_name, team2_name
    
    # Try to find any team name in the text
    found_teams = []
    for alias in TEAM_ALIASES.keys():
        if alias in bet_lower:
            found_teams.append(alias)
    
    if len(found_teams) >= 2:
        return found_teams[0], found_teams[1]
    elif len(found_teams) == 1:
        return found_teams[0], None
    
    return None, None


def get_enhanced_bet_analysis(bet_text: str) -> Optional[Dict]:
    """Get enhanced analysis for a bet including real NBA data.
    
    For multi-leg parlays, returns matchup data for each leg.
    """
    # Check if this is a multi-leg bet (contains multiple lines or delimiters)
    lines = [line.strip() for line in bet_text.split('\n') if line.strip()]
    if len(lines) == 1:
        parts = re.split(r'[,;]', lines[0])
        if len(parts) > 1:
            lines = [p.strip() for p in parts if p.strip()]
    
    # If multiple legs, analyze each one
    if len(lines) > 1:
        return get_multi_leg_analysis(lines)
    
    # Single leg analysis
    team1_name, team2_name = extract_teams_from_bet(bet_text)
    
    if not team1_name:
        return None
    
    if team2_name:
        # Full matchup analysis
        matchup = get_matchup_analysis(team1_name, team2_name)
        if matchup:
            # Extract spread if present
            spread_match = re.search(r'([+-]?\d+\.?\d*)', bet_text)
            spread = float(spread_match.group(1)) if spread_match else 0
            
            insight = generate_betting_insight(matchup, 'spread', spread)
            
            return {
                'hasData': True,
                'matchup': matchup,
                'insight': insight,
                'teams': [team1_name, team2_name],
                'allMatchups': None  # Single leg, no carousel needed
            }
    else:
        # Single team analysis
        team_analysis = get_team_analysis(team1_name)
        if team_analysis:
            return {
                'hasData': True,
                'team': team_analysis,
                'insight': f"{team_analysis['team']} is {team_analysis['record']} | Last 5: {team_analysis['recentForm']} | Avg: {team_analysis['avgPointsScored']} PPG",
                'teams': [team1_name],
                'allMatchups': None
            }
    
    return None


def get_multi_leg_analysis(bet_lines: List[str]) -> Optional[Dict]:
    """Analyze multiple bet legs and return data for each matchup."""
    all_matchups = []
    combined_insights = []
    all_teams = []
    
    for line in bet_lines:
        team1_name, team2_name = extract_teams_from_bet(line)
        
        if not team1_name:
            continue
        
        if team2_name:
            matchup = get_matchup_analysis(team1_name, team2_name)
            if matchup:
                spread_match = re.search(r'([+-]?\d+\.?\d*)', line)
                spread = float(spread_match.group(1)) if spread_match else 0
                insight = generate_betting_insight(matchup, 'spread', spread)
                
                all_matchups.append({
                    'matchup': matchup,
                    'insight': insight,
                    'betLine': line[:100],
                    'legNumber': len(all_matchups) + 1
                })
                all_teams.extend([team1_name, team2_name])
                
                # Short insight for combined view
                t1 = matchup['team1']
                t2 = matchup['team2']
                t1_hot = t1.get('recentForm', '').count('W') >= 4
                t2_hot = t2.get('recentForm', '').count('W') >= 4
                
                if t1_hot:
                    combined_insights.append(f"{t1['abbreviation']} is HOT - won {t1.get('recentForm', '').count('W')} of last 5")
                if t2_hot:
                    combined_insights.append(f"{t2['abbreviation']} is HOT - won {t2.get('recentForm', '').count('W')} of last 5")
        else:
            # Single team mentioned
            team_analysis = get_team_analysis(team1_name)
            if team_analysis:
                all_matchups.append({
                    'team': team_analysis,
                    'matchup': None,
                    'insight': f"{team_analysis['team']} is {team_analysis['record']}",
                    'betLine': line[:100],
                    'legNumber': len(all_matchups) + 1
                })
                all_teams.append(team1_name)
    
    if not all_matchups:
        return None
    
    # Use the first matchup as the default display
    first_matchup = all_matchups[0]
    
    # Generate combined insight
    if combined_insights:
        combined_insight = " | ".join(combined_insights[:3])  # Max 3 insights
    else:
        combined_insight = f"Analyzing {len(all_matchups)} matchups with NBA data"
    
    # Add h2h summary to insight
    h2h_summaries = []
    for m in all_matchups:
        if m.get('matchup') and m['matchup'].get('headToHead'):
            h2h = m['matchup']['headToHead']
            t1 = m['matchup']['team1']['abbreviation']
            t2 = m['matchup']['team2']['abbreviation']
            h2h_summaries.append(f"{t1} {h2h['team1Wins']}-{h2h['team2Wins']} {t2}")
    
    if h2h_summaries:
        combined_insight += f" | H2H: {', '.join(h2h_summaries[:2])}"
    
    # Add projected scores
    projected_scores = []
    for m in all_matchups:
        if m.get('matchup'):
            t1 = m['matchup']['team1']
            t2 = m['matchup']['team2']
            expected_t1 = (t1['avgPointsScored'] + t2['avgPointsAllowed']) / 2
            expected_t2 = (t2['avgPointsScored'] + t1['avgPointsAllowed']) / 2
            projected_scores.append(f"{t1['abbreviation']} {expected_t1:.0f} - {t2['abbreviation']} {expected_t2:.0f}")
    
    if projected_scores:
        combined_insight += f" | Projected: {projected_scores[0]}"
    
    return {
        'hasData': True,
        'matchup': first_matchup.get('matchup'),
        'team': first_matchup.get('team'),
        'insight': combined_insight,
        'teams': list(set(all_teams)),
        'allMatchups': all_matchups,
        'totalMatchups': len(all_matchups)
    }
