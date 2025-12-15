from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# defualt user info
user_data = {
    "income": 3000,
    "expenses": 1500,
    "savings": 200,
    "categories": {
        "food": 300,
        "entertainment": 200,
        "bills": 1000
    },

    # NEW: bankroll + mode for betting guidance (demo mode / in-memory)
    "bankroll": 5000.0,
    "risk_mode": "conservative"  # conservative | aggressive
}

# -----------------------------
# Existing helpers (unchanged)
# -----------------------------
def calculate_remaining_budget():
    total_spent = sum(user_data["categories"].values()) + user_data["savings"]
    return user_data["income"] - total_spent

# -----------------------------
# New: Betting / odds helpers
# -----------------------------
def _extract_first_american_odds(text: str):
    """
    Extract first American odds token from text: -110, +145, 110.
    Returns int or None.
    """
    m = re.search(r"(?<!\d)([+-]?\d{2,4})(?!\d)", text)
    if not m:
        return None
    try:
        return int(m.group(1))
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
    """
    Accept: 'stake 100' / 'stake: 100' / 'stake $100'
    """
    m = re.search(r"stake\s*[:=]?\s*\$?\s*(\d+(?:\.\d+)?)", text.lower())
    if not m:
        return None
    return float(m.group(1))

def parse_percent(text: str):
    """
    Extract percentage like '2%' or '2.5%'.
    """
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", text)
    if not m:
        return None
    return float(m.group(1))

def payout_for_stake(stake: float, odds: int):
    dec = american_to_decimal(odds)
    profit = stake * (dec - 1.0)
    total = stake + profit
    return {
        "decimal_odds": round(dec, 4),
        "profit": round(profit, 2),
        "total_payout": round(total, 2),
    }

def recommend_stake(bankroll: float, mode: str):
    """
    Conservative: 1–2%
    Aggressive: 2–5%
    """
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

def handle_input(user_input):
    text = user_input.lower().strip()

    # ---------------------------------
    # Existing: greet user (unchanged)
    # ---------------------------------
    if text in ["hi", "hello", "hey"]:
        return ("Hey there! I'm your AI Financial Assistant.<br>"
                "You can ask me to:<br>"
                "- Update your income or expenses<br>"
                "- Add to food, bills, or entertainment<br>"
                "- Type 'help' for a list of all commands!")

    # -------------------------------------------------
    # UPDATED: help list (keeps old commands + adds new)
    # ----------------------------------------------------
    if "help" in text:
        return ("Here's what you can say:<br>"
                "<b>Budget / Finance:</b><br>"
                "- 'Show my budget'<br>"
                "- 'Add 200 to food'<br>"
                "- 'Update entertainment to 400'<br>"
                "- 'Set income to 5000'<br>"
                "- 'Update savings to 300'<br>"
                "- 'Reset data'<br><br>"
                "<b>Bankroll / Betting Math:</b><br>"
                "- 'Set bankroll to 5000'<br>"
                "- 'What is 2% of bankroll?'<br>"
                "- 'Recommend conservative stake'<br>"
                "- 'Recommend aggressive stake'<br>"
                "- 'Set risk mode to conservative'<br>"
                "- 'Set risk mode to aggressive'<br>"
                "- 'Implied probability for -110'<br>"
                "- 'Payout for stake 100 at -110'<br>"
                "- 'Parlay odds for -110, +145, -105'")

    # ----------------------------------------------------------------
    # NEW: betting/bankroll commands (added BEFORE budget/show/default)
    # -----------------------------------------------------------------

    # set bankroll to 5000
    if "bankroll" in text and any(word in text for word in ["set", "update", "change", "make"]):
        m = re.search(r"(?:set|update|change|make)\s+bankroll\s+(?:to\s+)?(\d+(?:\.\d+)?)", text)
        if not m:
            return "Try: <b>Set bankroll to 5000</b>"
        user_data["bankroll"] = float(m.group(1))
        return f"Bankroll updated to <b>${user_data['bankroll']:,.2f}</b>."

    # set risk mode
    if "risk mode" in text or ("set" in text and "aggressive" in text) or ("set" in text and "conservative" in text):
        if "aggressive" in text:
            user_data["risk_mode"] = "aggressive"
            return "Risk mode set to <b>aggressive</b> (2–5% stake guidance)."
        if "conservative" in text:
            user_data["risk_mode"] = "conservative"
            return "Risk mode set to <b>conservative</b> (1–2% stake guidance)."
        return "Try: <b>Set risk mode to conservative</b> or <b>Set risk mode to aggressive</b>."

    # recommend stake
    if "recommend" in text and "stake" in text:
        rec = recommend_stake(float(user_data.get("bankroll", 0)), user_data.get("risk_mode", "conservative"))
        if not rec:
            return "Bankroll must be set to a positive number first. Try: <b>Set bankroll to 5000</b>"
        return (f"Recommended stake range (<b>{rec['mode']}</b>):<br>"
                f"- {rec['low_pct']}%: <b>${rec['low']:,.2f}</b><br>"
                f"- {rec['high_pct']}%: <b>${rec['high']:,.2f}</b>")

    # percent of bankroll
    if "bankroll" in text and parse_percent(text) is not None:
        pct = parse_percent(text)
        bankroll = float(user_data.get("bankroll", 0))
        amt = bankroll * (pct / 100.0)
        return f"{pct}% of bankroll (<b>${bankroll:,.2f}</b>) is <b>${amt:,.2f}</b>."

    # implied probability for -110
    if "implied" in text and "prob" in text:
        odds = _extract_first_american_odds(text)
        if odds is None:
            return "Try: <b>Implied probability for -110</b>"
        try:
            p = implied_probability(odds) * 100.0
            return f"Implied probability for <b>{odds}</b> is <b>{p:.2f}%</b>."
        except ValueError as e:
            return str(e)

    # payout for stake 100 at -110
    if "payout" in text or "profit" in text:
        stake = parse_stake(text)
        odds = _extract_first_american_odds(text)
        if stake is None or odds is None:
            return "Try: <b>Payout for stake 100 at -110</b>"
        if stake <= 0:
            return "Stake must be greater than 0."
        try:
            res = payout_for_stake(stake, odds)
            return (f"For stake <b>${stake:,.2f}</b> at <b>{odds}</b>:<br>"
                    f"- Decimal odds: <b>{res['decimal_odds']}</b><br>"
                    f"- Profit: <b>${res['profit']:,.2f}</b><br>"
                    f"- Total payout: <b>${res['total_payout']:,.2f}</b>")
        except ValueError as e:
            return str(e)

    # parlay odds for -110, +145, -105
    if "parlay" in text and ("odds" in text or "for" in text):
        odds_list = re.findall(r"(?<!\d)([+-]?\d{2,4})(?!\d)", text)
        if not odds_list or len(odds_list) < 2:
            return "Try: <b>Parlay odds for -110, +145, -105</b>"
        try:
            decimals = [american_to_decimal(int(o)) for o in odds_list]
            parlay_decimal = 1.0
            for d in decimals:
                parlay_decimal *= d

            # Convert decimal -> American approximation
            if parlay_decimal >= 2.0:
                parlay_american = int(round((parlay_decimal - 1.0) * 100))
                american_str = f"+{parlay_american}"
            else:
                parlay_american = int(round(-100 / (parlay_decimal - 1.0)))
                american_str = f"{parlay_american}"

            return (f"Parlay decimal odds: <b>{parlay_decimal:.4f}</b><br>"
                    f"Approx. parlay American odds: <b>{american_str}</b>")
        except Exception:
            return "Could not parse parlay odds. Make sure you include valid odds like -110, +145."

    # NEW: keyword-based suggestions (makes it feel smarter)
    if "odds" in text or "probability" in text:
        return "Try: <b>Implied probability for -110</b> or <b>Payout for stake 100 at -110</b>."
    if "bankroll" in text or "stake" in text:
        return "Try: <b>Set bankroll to 5000</b> then <b>Recommend conservative stake</b>."
    if "bet" in text or "parlay" in text:
        return "Try: <b>Parlay odds for -110, +145, -105</b>."

    # ---------------------------------
    # Existing: reset data (unchanged)
    # ---------------------------------
    if "reset" in text:
        user_data.update({
            "income": 3000,
            "expenses": 1500,
            "savings": 200,
            "categories": {"food": 300, "entertainment": 200, "bills": 1000},
            "bankroll": 5000.0,
            "risk_mode": "conservative"
        })
        return "All data reset to default values."

    # ------------------------------------
    # Existing: update income (unchanged)
    # -------------------------------------
    if "income" in text:
        try:
            amount = float("".join([c for c in text if c.isdigit() or c == "."]))
            if any(word in text for word in ["update", "set", "change", "make"]):
                user_data["income"] = amount
                return f"Income updated to ${amount:,.2f}."
            else:
                user_data["income"] += amount
                return f"Added ${amount:,.2f} to income. Total: ${user_data['income']:,.2f}."
        except:
            return "Couldn't process income update."

    # -------------------------------------
    # Existing: update expenses (unchanged)
    # --------------------------------------
    if "expense" in text or "expenses" in text:
        try:
            amount = float("".join([c for c in text if c.isdigit() or c == "."]))
            if any(word in text for word in ["update", "set", "change"]):
                user_data["expenses"] = amount
                return f"Expenses updated to ${amount:,.2f}."
            else:
                user_data["expenses"] += amount
                return f"Added ${amount:,.2f} to expenses. Total: ${user_data['expenses']:,.2f}."
        except:
            return "Couldn't process expenses update."

    # -----------------------------------------
    # Existing: update the savings (unchanged)
    # ------------------------------------------
    if "saving" in text or "savings" in text:
        try:
            amount = float("".join([c for c in text if c.isdigit() or c == "."]))
            if any(word in text for word in ["update", "set", "change"]):
                user_data["savings"] = amount
                return f"Savings updated to ${amount:,.2f}."
            else:
                user_data["savings"] += amount
                return f"Added ${amount:,.2f} to savings. Total: ${user_data['savings']:,.2f}."
        except:
            return "Couldn't process savings update."

    # ----------------------------------------
    # Existing: update categories (unchanged)
    # ------------------------------------------
    for category in user_data["categories"]:
        if category in text:
            try:
                amount = float("".join([c for c in text if c.isdigit() or c == "."]))
                if any(word in text for word in ["update", "set", "change", "make"]):
                    user_data["categories"][category] = amount
                    return f"{category.capitalize()} updated to ${amount:,.2f}."
                else:
                    user_data["categories"][category] += amount
                    return f"Added ${amount:,.2f} to {category}. Total: ${user_data['categories'][category]:,.2f}."
            except:
                return f"Please specify a valid amount for {category}."

    # ---------------------------------------
    # Existing: show user budget (unchanged)
    # ----------------------------------------
    if "budget" in text or "show" in text:
        remaining = calculate_remaining_budget()
        category_breakdown = "<br>".join([f"- {k.capitalize()}: ${v:,.2f}" for k, v in user_data["categories"].items()])
        return (f"Here's your budget breakdown:<br><br>"
                f"<b>Income:</b> ${user_data['income']:,.2f}<br>"
                f"<b>Expenses:</b> ${user_data['expenses']:,.2f}<br>"
                f"<b>Savings:</b> ${user_data['savings']:,.2f}<br><br>"
                f"{category_breakdown}<br><br>"
                f"<b>Remaining:</b> ${remaining:,.2f}")

    # -------------------------------------
    # Existing: default summary (unchanged)
    # ------------------------------------------
    remaining = calculate_remaining_budget()
    return (f"Here's your quick financial summary:<br><br>"
            f"- Income: ${user_data['income']:,.2f}<br>"
            f"- Expenses: ${user_data['expenses']:,.2f}<br>"
            f"- Savings: ${user_data['savings']:,.2f}<br>"
            f"- Remaining budget: ${remaining:,.2f}<br><br>"
            "Need help? Type <b>help</b> to see what else I can do.")

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    reply = handle_input(user_message)
    return jsonify({"response": reply})

if __name__ == "__main__":
    # Keep port 3000 for the Vite proxy target
    app.run(host="127.0.0.1", port=3000, debug=True)