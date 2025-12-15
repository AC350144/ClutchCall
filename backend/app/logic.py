import pandas as pd
import math
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
    input_data = pd.DataFrame(
        [[income, fixed_expenses, savings_goal, months_to_goal]],
        columns=['income', 'fixed_expenses', 'savings_goal', 'months_to_goal']
    )

    food_pct, entertainment_pct, shopping_pct = model.predict(input_data)[0]

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