import re

def parse_bet_text(raw_text: str) -> dict:
    """
    Parse raw clipboard bet text into structured bet data.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    stake = None
    legs = []
    bet_type = "single"

    for line in lines:
        # Detect stake
        stake_match = re.search(r"\$(\d+)", line)
        if stake_match:
            stake = int(stake_match.group(1))
            continue

        # Detect totals (Over / Under)
        total_match = re.match(r"(over|under)\s+(\d+(\.\d+)?)", line, re.IGNORECASE)
        if total_match:
            legs.append({
                "type": "total",
                "side": total_match.group(1).lower(),
                "line": float(total_match.group(2))
            })
            continue

        # Detect spread (Team -3.5)
        spread_match = re.match(r"(.+?)\s+([-+]\d+(\.\d+)?)", line)
        if spread_match:
            legs.append({
                "type": "spread",
                "team": spread_match.group(1).strip(),
                "line": float(spread_match.group(2))
            })
            continue

        # Detect parlay keyword
        if "parlay" in line.lower():
            bet_type = "parlay"

    if len(legs) > 1:
        bet_type = "parlay"

    return {
        "stake": stake,
        "bet_type": bet_type,
        "legs": legs
    }
