import pandas as pd
import math
import re
from app.model import load_model

model = load_model()

def suggest_budget(income, fixed_expenses, savings_goal, months_to_goal):
    """Suggest a personalized budget breakdown."""
    try:
        income = float(income)
        fixed_expenses = float(fixed_expenses)
        savings_goal = float(savings_goal)
        months_to_goal = float(months_to_goal)
    except (ValueError, TypeError):
        return "⚠️ Input not realistic. Please enter numeric values."

    # Reject NaN or infinite values
    if any(map(lambda x: math.isnan(x) or math.isinf(x), [income, fixed_expenses, savings_goal, months_to_goal])):
        return "⚠️ Input not realistic. Please enter numeric values."

    if months_to_goal <= 0 or income <= 0 or fixed_expenses < 0 or savings_goal < 0:
        return "⚠️ Input not realistic. Please check your numbers."

    savings_per_month = savings_goal / months_to_goal
    available = income - fixed_expenses - savings_per_month

    if available <= 0:
        return "⚠️ This goal is not realistic with your current income and expenses."

    # Use DataFrame to avoid sklearn warnings
    food_pct, entertainment_pct, shopping_pct = model.predict(
        [[income, fixed_expenses, savings_goal, months_to_goal]]
    )[0]
    
    return {
        "Income": income,
        "Fixed Expenses": fixed_expenses,
        "Savings per Month": round(savings_per_month, 2),
        "Budget Allocation": {
            "Food": round(food_pct * available, 2),
            "Entertainment": round(entertainment_pct * available, 2),
            "Shopping": round(shopping_pct * available, 2)
        }
    }
    
def extract_first_american_odds(text: str):
    """Extract the first American odds token from text (e.g., -110, +145)."""

    match = re.search(r"(?<!\d)([+-]?\d{2,4})(?!\d)", text)
    if not match:
        return None

    try:
        return int(match.group(1))
    except ValueError:
        return None


def american_to_decimal(odds: int) -> float:
    if odds == 0:
        raise ValueError("Odds cannot be 0.")
    return 1.0 + (odds / 100.0) if odds > 0 else 1.0 + (100.0 / abs(odds))


def implied_probability(odds: int) -> float:
    if odds == 0:
        raise ValueError("Odds cannot be 0.")
    return (100.0 / (odds + 100.0)) if odds > 0 else (abs(odds) / (abs(odds) + 100.0))


def parse_stake(text: str):
    """Extract a stake value such as 'stake 100' or 'stake $100'."""

    match = re.search(r"stake\s*[:=]?\s*\$?\s*(\d+(?:\.\d+)?)", text.lower())
    if not match:
        return None
    return float(match.group(1))


def parse_percent(text: str):
    """Extract a percentage like '2%' or '2.5%' from text."""

    match = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    if not match:
        return None
    return float(match.group(1))


def payout_for_stake(stake: float, odds: int):
    decimal = american_to_decimal(odds)
    profit = stake * (decimal - 1.0)
    total = stake + profit

    return {
        "decimal_odds": round(decimal, 4),
        "profit": round(profit, 2),
        "total_payout": round(total, 2),
    }


def recommend_stake(bankroll: float, mode: str):
    """Return suggested stake ranges based on the bankroll and risk mode."""

    if bankroll <= 0:
        return None

    if mode == "aggressive":
        low, high = 0.02, 0.05
    else:
        low, high = 0.01, 0.02

    return {
        "mode": mode,
        "low": round(bankroll * low, 2),
        "high": round(bankroll * high, 2),
        "low_pct": int(low * 100),
        "high_pct": int(high * 100),
    }