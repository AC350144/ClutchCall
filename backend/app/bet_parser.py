"""
AI Bet Parser & Analyzer Module

This module provides intelligent parsing and analysis of sports betting slips.
It extracts structured bet data from natural language input and provides
AI-powered recommendations based on odds analysis.
"""

import re
import math
from typing import List, Dict, Optional, Tuple, Any


# Common sports keywords for detection
SPORTS_KEYWORDS = {
    'NBA': ['nba', 'lakers', 'celtics', 'warriors', 'nuggets', 'heat', 'bulls', 'knicks', 
            'nets', 'suns', 'bucks', 'sixers', '76ers', 'mavs', 'mavericks', 'clippers',
            'rockets', 'spurs', 'thunder', 'jazz', 'kings', 'hawks', 'hornets', 'magic',
            'pacers', 'pistons', 'raptors', 'wizards', 'timberwolves', 'pelicans', 'grizzlies',
            'blazers', 'trail blazers', 'cavaliers', 'cavs'],
    'NFL': ['nfl', 'chiefs', 'eagles', 'cowboys', 'bills', 'ravens', 'lions', 'dolphins',
            '49ers', 'niners', 'packers', 'bengals', 'jets', 'patriots', 'broncos', 'raiders',
            'chargers', 'seahawks', 'vikings', 'bears', 'saints', 'falcons', 'buccaneers',
            'bucs', 'panthers', 'commanders', 'giants', 'cardinals', 'rams', 'steelers',
            'browns', 'colts', 'titans', 'jaguars', 'texans'],
    'NHL': ['nhl', 'bruins', 'rangers', 'maple leafs', 'leafs', 'canadiens', 'habs',
            'blackhawks', 'penguins', 'capitals', 'caps', 'lightning', 'avalanche', 'oilers',
            'flames', 'canucks', 'jets', 'wild', 'blues', 'stars', 'predators', 'hurricanes',
            'panthers', 'devils', 'islanders', 'flyers', 'senators', 'sabres', 'red wings',
            'sharks', 'kings', 'ducks', 'coyotes', 'kraken', 'golden knights', 'knights'],
    'MLB': ['mlb', 'yankees', 'red sox', 'dodgers', 'giants', 'cubs', 'mets', 'braves',
            'astros', 'phillies', 'padres', 'cardinals', 'brewers', 'mariners', 'guardians',
            'twins', 'orioles', 'rays', 'blue jays', 'rangers', 'angels', 'white sox',
            'tigers', 'royals', 'athletics', 'as', 'rockies', 'diamondbacks', 'dbacks',
            'marlins', 'nationals', 'reds', 'pirates'],
    'Soccer': ['soccer', 'mls', 'premier league', 'epl', 'la liga', 'bundesliga', 
               'serie a', 'ligue 1', 'champions league', 'ucl', 'manchester united',
               'man united', 'manchester city', 'man city', 'liverpool', 'chelsea',
               'arsenal', 'tottenham', 'spurs', 'barcelona', 'real madrid', 'bayern',
               'psg', 'juventus', 'inter', 'ac milan', 'dortmund']
}

# Bet type patterns
BET_TYPE_PATTERNS = {
    'Spread': [
        r'([+-]\d+\.?\d*)\s*(?:spread|pts?|points?)?',
        r'(?:spread|pts?|points?)\s*([+-]\d+\.?\d*)',
    ],
    'Moneyline': [
        r'\b(?:ml|moneyline|money\s*line|to\s*win)\b',
        r'\bwin\s*outright\b',
    ],
    'Total': [
        r'(?:over|under|o|u)\s*(\d+\.?\d*)',
        r'(\d+\.?\d*)\s*(?:over|under|o|u)',
        r'(?:total|o/u)\s*(\d+\.?\d*)',
    ],
    'Prop': [
        r'(?:prop|player\s*prop|anytime|first|last|scorer|yards|points|rebounds|assists)',
    ],
    'Parlay': [
        r'\bparlay\b',
        r'\bcombo\b',
        r'\baccumulator\b',
        r'\bacca\b',
    ]
}


def parse_american_odds(odds_str: str) -> Optional[int]:
    """Parse American odds from string format."""
    try:
        odds_str = odds_str.strip().replace(' ', '')
        # Handle formats like "+150", "-110", "150", etc.
        match = re.search(r'([+-]?\d+)', odds_str)
        if match:
            odds = int(match.group(1))
            # If no sign and odds >= 100, assume positive
            if odds >= 100 and not odds_str.startswith('-'):
                return odds
            elif odds > 0 and odds < 100:
                # Likely missing the sign, assume negative (common for favorites)
                return -odds if odds_str.startswith('-') else odds
            return odds
    except (ValueError, AttributeError):
        pass
    return None


def detect_sport(text: str) -> str:
    """Detect the sport from the bet text."""
    text_lower = text.lower()
    
    for sport, keywords in SPORTS_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return sport
    
    return 'Unknown'


def detect_bet_type(text: str) -> str:
    """Detect the type of bet from the text."""
    text_lower = text.lower()
    
    # Check for spread
    if re.search(r'[+-]\d+\.?\d*', text) and not re.search(r'@\s*[+-]', text):
        return 'Spread'
    
    # Check for totals
    if re.search(r'(?:over|under|o|u)\s*\d+', text_lower):
        return 'Total'
    
    # Check for moneyline
    if re.search(r'\b(?:ml|moneyline|money\s*line|to\s*win)\b', text_lower):
        return 'Moneyline'
    
    # Check for props
    if re.search(r'(?:prop|anytime|first|last|scorer|yards|rebounds|assists)', text_lower):
        return 'Prop'
    
    # Default to moneyline if we find a team name with odds
    if re.search(r'@?\s*[+-]\d{3}', text):
        return 'Moneyline'
    
    return 'Moneyline'


def extract_odds(text: str) -> List[int]:
    """Extract all American odds from text."""
    odds_list = []
    
    # Match patterns like "+150", "-110", "@ +150", "@-110"
    patterns = [
        r'@\s*([+-]\d{2,4})',
        r'\(\s*([+-]\d{2,4})\s*\)',
        r'(?:odds?:?\s*)([+-]\d{2,4})',
        r'\b([+-]\d{3})\b',
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            odds = parse_american_odds(match)
            if odds is not None:
                odds_list.append(odds)
    
    return odds_list


def extract_teams_and_games(text: str) -> List[Dict[str, str]]:
    """Extract team matchups from text."""
    games = []
    
    # Common matchup patterns
    patterns = [
        r'(\w+(?:\s+\w+)?)\s+(?:vs\.?|v\.?|@|at)\s+(\w+(?:\s+\w+)?)',
        r'(\w+)\s+(?:over|under)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match.groups()) >= 2:
                games.append({
                    'team_a': match.group(1).strip(),
                    'team_b': match.group(2).strip(),
                    'game': f"{match.group(1).strip()} vs {match.group(2).strip()}"
                })
            elif len(match.groups()) == 1:
                games.append({
                    'team_a': match.group(1).strip(),
                    'team_b': 'Unknown',
                    'game': match.group(1).strip()
                })
    
    return games


def calculate_implied_probability(odds: int) -> float:
    """Calculate implied probability from American odds."""
    if odds > 0:
        return 100 / (odds + 100)
    else:
        return abs(odds) / (abs(odds) + 100)


def calculate_parlay_odds(odds_list: List[int]) -> int:
    """Calculate combined American odds for a parlay."""
    if not odds_list:
        return 0
    
    # Convert to decimal, multiply, convert back
    decimal_odds = []
    for odds in odds_list:
        if odds > 0:
            decimal_odds.append(odds / 100 + 1)
        else:
            decimal_odds.append(100 / abs(odds) + 1)
    
    combined_decimal = 1
    for dec in decimal_odds:
        combined_decimal *= dec
    
    # Convert back to American
    if combined_decimal >= 2:
        return int((combined_decimal - 1) * 100)
    else:
        return int(-100 / (combined_decimal - 1))


def calculate_payout(stake: float, odds: int) -> float:
    """Calculate potential payout for a bet."""
    if odds > 0:
        return stake * (odds / 100)
    else:
        return stake * (100 / abs(odds))


def analyze_bet_quality(legs: List[Dict], total_odds: int) -> Tuple[int, str, str]:
    """
    Analyze the quality of a bet based on various factors.
    Returns (quality_score, analysis, recommendation).
    """
    quality_score = 70  # Base score
    analysis_points = []
    
    num_legs = len(legs)
    
    # Penalty for too many legs
    if num_legs > 6:
        quality_score -= 20
        analysis_points.append("High-risk parlay with many legs. Consider reducing the number of selections.")
    elif num_legs > 4:
        quality_score -= 10
        analysis_points.append("Multi-leg parlay increases risk. Each additional leg compounds the chance of loss.")
    elif num_legs <= 2:
        quality_score += 5
        analysis_points.append("Conservative bet size with manageable risk.")
    
    # Analyze individual leg odds
    heavy_favorites = 0
    long_shots = 0
    
    for leg in legs:
        odds = leg.get('odds', 0)
        if odds < -200:
            heavy_favorites += 1
        elif odds > 200:
            long_shots += 1
    
    if heavy_favorites > 0:
        quality_score -= heavy_favorites * 3
        analysis_points.append(f"Contains {heavy_favorites} heavy favorite(s). Low payout relative to risk.")
    
    if long_shots > 0:
        quality_score += long_shots * 2  # Slight bonus for value
        analysis_points.append(f"Contains {long_shots} underdog pick(s). Higher variance but potential value.")
    
    # Implied probability analysis
    total_implied = 0
    for leg in legs:
        odds = leg.get('odds', -110)
        total_implied += calculate_implied_probability(odds)
    
    avg_implied = total_implied / num_legs if num_legs > 0 else 0.5
    
    if avg_implied > 0.6:
        analysis_points.append("Average implied probability suggests favorites. Lower payouts expected.")
    elif avg_implied < 0.4:
        quality_score += 5
        analysis_points.append("Contains value picks with lower implied probabilities.")
    
    # Parlay probability
    parlay_prob = 1
    for leg in legs:
        odds = leg.get('odds', -110)
        parlay_prob *= calculate_implied_probability(odds)
    
    if parlay_prob < 0.05:
        quality_score -= 15
        analysis_points.append(f"Combined probability is only {parlay_prob*100:.1f}%. Very unlikely to hit.")
    elif parlay_prob < 0.15:
        quality_score -= 5
        analysis_points.append(f"Combined probability of {parlay_prob*100:.1f}%. Moderate difficulty.")
    else:
        quality_score += 5
        analysis_points.append(f"Reasonable combined probability of {parlay_prob*100:.1f}%.")
    
    # Cap the score
    quality_score = max(10, min(95, quality_score))
    
    # Determine recommendation
    if quality_score >= 75:
        recommendation = 'good'
    elif quality_score >= 55:
        recommendation = 'caution'
    else:
        recommendation = 'avoid'
    
    analysis = " ".join(analysis_points) if analysis_points else "Standard bet with typical risk profile."
    
    return quality_score, analysis, recommendation


def parse_bet_text(bet_text: str) -> Dict[str, Any]:
    """
    Main function to parse bet text and return structured data.
    
    Args:
        bet_text: Raw bet slip text (copied from sportsbook or written manually)
    
    Returns:
        Dictionary containing parsed legs, analysis, and recommendations
    """
    if not bet_text or not bet_text.strip():
        return {
            'success': False,
            'error': 'No bet text provided',
            'legs': [],
            'qualityScore': 0,
            'analysis': '',
            'recommendation': 'avoid'
        }
    
    legs = []
    lines = [line.strip() for line in bet_text.split('\n') if line.strip()]
    
    # If single line, try to split by common delimiters
    if len(lines) == 1:
        # Try splitting by commas or semicolons
        parts = re.split(r'[,;]', lines[0])
        if len(parts) > 1:
            lines = [p.strip() for p in parts if p.strip()]
    
    leg_id = 1
    for line in lines:
        if not line:
            continue
            
        sport = detect_sport(line)
        bet_type = detect_bet_type(line)
        odds_found = extract_odds(line)
        games = extract_teams_and_games(line)
        
        # Try to extract selection text
        selection = line
        
        # Clean up selection - remove odds
        selection = re.sub(r'@?\s*[+-]\d{2,4}', '', selection).strip()
        selection = re.sub(r'\(\s*[+-]\d{2,4}\s*\)', '', selection).strip()
        
        # Default odds if none found
        odds = odds_found[0] if odds_found else -110
        
        # Determine game name
        game = games[0]['game'] if games else 'Unknown Game'
        
        leg = {
            'id': f'leg-{leg_id}',
            'sport': sport,
            'game': game,
            'betType': bet_type,
            'selection': selection[:100],  # Truncate long selections
            'odds': odds
        }
        
        legs.append(leg)
        leg_id += 1
    
    # If no legs parsed, try to create at least one from the whole text
    if not legs:
        sport = detect_sport(bet_text)
        odds_found = extract_odds(bet_text)
        
        legs.append({
            'id': 'leg-1',
            'sport': sport,
            'game': 'Unknown Game',
            'betType': detect_bet_type(bet_text),
            'selection': bet_text[:100],
            'odds': odds_found[0] if odds_found else -110
        })
    
    # Calculate total odds
    all_odds = [leg['odds'] for leg in legs]
    total_odds = calculate_parlay_odds(all_odds) if len(all_odds) > 1 else all_odds[0]
    
    # Analyze bet quality
    quality_score, analysis, recommendation = analyze_bet_quality(legs, total_odds)
    
    return {
        'success': True,
        'legs': legs,
        'totalOdds': total_odds,
        'qualityScore': quality_score,
        'analysis': analysis,
        'recommendation': recommendation
    }


def get_stake_recommendation(bankroll: float, quality_score: int, recommendation: str) -> Dict[str, float]:
    """
    Get stake recommendations based on bankroll and bet quality.
    
    Uses Kelly Criterion-inspired sizing:
    - Good bets: 2-3% of bankroll
    - Caution bets: 1-2% of bankroll
    - Avoid bets: 0.5-1% of bankroll (if betting anyway)
    """
    if recommendation == 'good':
        base_pct = 0.025  # 2.5%
        max_pct = 0.03    # 3%
    elif recommendation == 'caution':
        base_pct = 0.015  # 1.5%
        max_pct = 0.02    # 2%
    else:
        base_pct = 0.005  # 0.5%
        max_pct = 0.01    # 1%
    
    # Adjust based on quality score
    quality_factor = quality_score / 100
    recommended_pct = base_pct + (max_pct - base_pct) * quality_factor
    
    return {
        'recommended': round(bankroll * recommended_pct, 2),
        'conservative': round(bankroll * base_pct * 0.5, 2),
        'aggressive': round(bankroll * max_pct * 1.5, 2),
        'percentage': round(recommended_pct * 100, 2)
    }
