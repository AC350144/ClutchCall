def analyze_bet(parsed_bet: dict) -> dict:
    """
    Analyze parsed bet data and return risk insights.
    """
    legs = parsed_bet.get("legs", [])
    bet_type = parsed_bet.get("bet_type", "single")

    risk = "low"
    warnings = []

    if bet_type == "parlay" and len(legs) > 1:
        risk = "high"
        warnings.append("Multi-leg parlays increase variance and risk.")

    if parsed_bet.get("stake") and parsed_bet["stake"] > 100:
        warnings.append("Large stake detected. Consider bankroll management.")

    return {
        "risk": risk,
        "warnings": warnings,
        "summary": f"{len(legs)}-leg {bet_type}"
    }
