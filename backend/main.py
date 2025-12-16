from flask import Flask, render_template, request, jsonify, make_response, send_file
import re
from db import create_tables, get_connection
import datetime
import os
import jwt
import bcrypt
import pymysql
import io
import pyotp
import qrcode
from app.logic import (
    american_to_decimal,
    extract_first_american_odds,
    implied_probability,
    parse_percent,
    parse_stake,
    payout_for_stake,
    recommend_stake,
)

app = Flask(__name__)
conn = create_tables()
ALGORITHM = "HS256"
SECRET_KEY = "TEST_SECRET" # CHANGE LATER!!!

#defualt user info
user_data = {
    "income": 3000,
    "expenses": 1500,
    "savings": 200,
    "categories": {
        "food": 300,
        "entertainment": 200,
        "bills": 1000
    },
    "bankroll": 5000.0,
    "risk_mode": "conservative"
}

def calculate_remaining_budget():
    total_spent = sum(user_data["categories"].values()) + user_data["savings"]
    return user_data["income"] - total_spent

def ensure_connection():
    """Ensure the global DB connection is alive, recreating it if needed."""
    global conn
    try:
        conn.ping(reconnect=True)
    except Exception:
        conn = get_connection(create_db_if_missing=False)


def authenticate_user(include_user=False):
    token = request.cookies.get("token")

    if not token:
        return False, make_response("No token provided.", 401), None

    payload = decode_token(token)

    if not payload or payload.get("type") != "access" or not payload.get("email"):
        resp = make_response("Unauthorized.", 401)
        resp.delete_cookie(
            "token",
            path="/",
            httponly=True,
            secure=False,
            samesite="Lax",
        )
        return False, resp, None

    if not include_user:
        return True, None, payload

    ensure_connection()
    with conn.cursor() as c:
        c.execute("SELECT id, email FROM users WHERE email = %s", (payload.get("email"),))
        user = c.fetchone()

    if not user:
        return False, make_response("Unauthorized.", 401), None

    return True, user, payload

def handle_input(user_input, bankroll_record=None, user_id=None):
    text = user_input.lower().strip()

    def get_bankroll_balance():
        if bankroll_record and bankroll_record.get("current_balance") is not None:
            return float(bankroll_record.get("current_balance", 0))
        return float(user_data.get("bankroll", 0))

    def set_bankroll_balance(amount: float):
        nonlocal bankroll_record

        if not user_id:
            raise PermissionError("Please log in to update your bankroll.")

        bankroll_record = update_bankroll_balance(user_id, amount, bankroll_record)
        return bankroll_record

    #Greet user
    if text in ["hi", "hello", "hey"]:
        return ("Hey there! I'm your AI Financial Assistant.<br>"
                "You can ask me to:<br>"
                "- Update your income or expenses<br>"
                "- Add to food, bills, or entertainment<br>"
                "- Type 'help' for a list of all commands!")

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

    # set bankroll to 5000
    if "bankroll" in text and any(word in text for word in ["set", "update", "change", "make"]):
        m = re.search(r"(?:set|update|change|make)\s+bankroll\s+(?:to\s+)?(\d+(?:\.\d+)?)", text)
        if not m:
            return "Try: <b>Set bankroll to 5000</b>"

        updated_record = set_bankroll_balance(float(m.group(1)))
        return f"Bankroll updated to <b>${updated_record.get('current_balance', 0):,.2f}</b>."

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
        rec = recommend_stake(float(get_bankroll_balance()), user_data.get("risk_mode", "conservative"))
        if not rec:
            return "Bankroll must be set to a positive number first. Try: <b>Set bankroll to 5000</b>"
        return (f"Recommended stake range (<b>{rec['mode']}</b>):<br>"
                f"- {rec['low_pct']}%: <b>${rec['low']:,.2f}</b><br>"
                f"- {rec['high_pct']}%: <b>${rec['high']:,.2f}</b>")

    # percent of bankroll
    if "bankroll" in text and parse_percent(text) is not None:
        pct = parse_percent(text)
        bankroll = float(get_bankroll_balance())
        amt = bankroll * (pct / 100.0)
        return f"{pct}% of bankroll (<b>${bankroll:,.2f}</b>) is <b>${amt:,.2f}</b>."

    # implied probability for -110
    if "implied" in text and "prob" in text:
        odds = extract_first_american_odds(text)
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
        odds = extract_first_american_odds(text)
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

    if "odds" in text or "probability" in text:
        return "Try: <b>Implied probability for -110</b> or <b>Payout for stake 100 at -110</b>."
    if "bankroll" in text or "stake" in text:
        return "Try: <b>Set bankroll to 5000</b> then <b>Recommend conservative stake</b>."
    if "bet" in text or "parlay" in text:
        return "Try: <b>Parlay odds for -110, +145, -105</b>."

    # reset data 
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

    # update income
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

    # update expenses
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

    # update the savings
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

    # update categories
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

    # show user budget
    if "budget" in text or "show" in text:
        remaining = calculate_remaining_budget()
        category_breakdown = "<br>".join([f"- {k.capitalize()}: ${v:,.2f}" for k, v in user_data["categories"].items()])
        return (f"Here's your budget breakdown:<br><br>"
                f"<b>Income:</b> ${user_data['income']:,.2f}<br>"
                f"<b>Expenses:</b> ${user_data['expenses']:,.2f}<br>"
                f"<b>Savings:</b> ${user_data['savings']:,.2f}<br><br>"
                f"{category_breakdown}<br><br>"
                f"<b>Remaining:</b> ${remaining:,.2f}")

    # default
    remaining = calculate_remaining_budget()
    return (f"Here's your quick financial summary:<br><br>"
            f"- Income: ${user_data['income']:,.2f}<br>"
            f"- Expenses: ${user_data['expenses']:,.2f}<br>"
            f"- Savings: ${user_data['savings']:,.2f}<br>"
            f"- Remaining budget: ${remaining:,.2f}<br><br>"
            "Need help? Type <b>help</b> to see what else I can do.")

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def create_temp_token(data: dict, expires_minutes=5):
    payload = data.copy()

    payload["mfa_pending"] = True

    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_minutes)
    payload["exp"] = expire

    payload["type"] = "temporary"

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def check_temp_token(token: str):
    if not token:
        return False, make_response("No token provided.", 400)

    payload = decode_token(token)

    if not payload or payload.get("mfa_pending") is not True:
        resp = make_response("Unauthorized.", 401)
        resp.delete_cookie(
            "temp_token",
            path="/",
            httponly=True,
            secure=False,
            samesite="Lax"
        )
        return False, resp

    if not payload.get("email"):
        resp = make_response("Invalid token payload.", 401)
        resp.delete_cookie("temp_token", path="/")
        return False, resp

    return True, payload


def create_access_token(data: dict, expires_minutes: int = 60):
    payload = data.copy()
    payload["exp"] = datetime.datetime.utcnow() + datetime.timedelta(minutes=expires_minutes)
    payload["type"] = "access"
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def get_or_create_bankroll(user_id: int, default_amount: float = 5000.0):
    ensure_connection()
    with conn.cursor() as c:
        c.execute(
            "SELECT id, current_balance, initial_bankroll, peak_balance, lowest_balance FROM bankrolls WHERE user_id = %s",
            (user_id,),
        )
        bankroll = c.fetchone()

        if bankroll:
            return bankroll

        c.execute(
            """
            INSERT INTO bankrolls (user_id, current_balance, initial_bankroll, peak_balance, lowest_balance)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (user_id, default_amount, default_amount, default_amount, default_amount),
        )
        conn.commit()

    with conn.cursor() as c:
        c.execute(
            "SELECT id, current_balance, initial_bankroll, peak_balance, lowest_balance FROM bankrolls WHERE user_id = %s",
            (user_id,),
        )
        return c.fetchone()


def update_bankroll_balance(user_id: int, new_balance: float, bankroll_record: dict = None):
    ensure_connection()
    bankroll_record = bankroll_record or get_or_create_bankroll(user_id)

    try:
        new_balance = float(new_balance)
    except (TypeError, ValueError):
        raise ValueError("Invalid bankroll amount.")

    if new_balance < 0:
        raise ValueError("Bankroll cannot be negative.")

    peak_balance = bankroll_record.get("peak_balance") or new_balance
    lowest_balance = bankroll_record.get("lowest_balance") or new_balance

    peak_balance = max(float(peak_balance), new_balance)
    lowest_balance = min(float(lowest_balance), new_balance)

    with conn.cursor() as c:
        c.execute(
            """
            UPDATE bankrolls
            SET current_balance = %s,
                peak_balance = %s,
                lowest_balance = %s
            WHERE user_id = %s
            """,
            (new_balance, peak_balance, lowest_balance, user_id),
        )
    conn.commit()

    bankroll_record.update(
        {
            "current_balance": float(new_balance),
            "peak_balance": float(peak_balance),
            "lowest_balance": float(lowest_balance),
        }
    )

    return bankroll_record


def serialize_bankroll(record: dict):
    if not record:
        return {}

    return {
        "id": record.get("id"),
        "current_balance": float(record.get("current_balance", 0)),
        "initial_bankroll": float(record.get("initial_bankroll", 0)),
        "peak_balance": float(record.get("peak_balance", 0)),
        "lowest_balance": float(record.get("lowest_balance", 0)),
    }

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    authenticated, user, _ = authenticate_user(include_user=True)
    bankroll_record = None

    if authenticated:
        bankroll_record = get_or_create_bankroll(user.get("id"))

    user_message = request.json.get("message", "")
    try:
        reply = handle_input(
            user_message,
            bankroll_record=bankroll_record,
            user_id=user.get("id") if authenticated else None,
        )
    except PermissionError as exc:
        return make_response(jsonify({"response": str(exc)}), 401)

    return jsonify({"response": reply})

@app.route("/bankroll", methods=["GET", "PUT"])
@app.route("/api/bankroll", methods=["GET", "PUT"])
def bankroll():
    authenticated, user, _ = authenticate_user(include_user=True)
    if not authenticated:
        return user

    bankroll_record = get_or_create_bankroll(user.get("id"))

    if request.method == "GET":
        return jsonify(serialize_bankroll(bankroll_record))

    data = request.get_json() or {}
    new_balance = data.get("current_balance")

    try:
        updated_record = update_bankroll_balance(user.get("id"), new_balance, bankroll_record)
    except ValueError as exc:
        return make_response(str(exc), 400)

    return jsonify(serialize_bankroll(updated_record))



@app.route("/mfa/setup", methods=["GET"])
def mfa_setup():
    temp_token = request.cookies.get("temp_token")
    success, data = check_temp_token(temp_token)

    if not success:
        return make_response("Invalid or expired token.", 401)

    email = data.get("email")
    if not email:
        return make_response("Invalid token payload.", 401)

    try:
        ensure_connection()
        with conn.cursor() as c:
            c.execute(
                "SELECT mfa_secret FROM users WHERE email = %s",
                (email,)
            )
            user = c.fetchone()

            if not user:
                return make_response("Invalid user.", 401)

            if user.get("mfa_secret"):
                return make_response("MFA already enabled.", 400)

            secret = pyotp.random_base32()
            c.execute(
                "UPDATE users SET mfa_secret = %s WHERE email = %s",
                (secret, email)
            )
        conn.commit()

    except Exception as e:
        print("DB ERROR:", e)
        return make_response("Internal server error.", 500)

    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=email,
        issuer_name="ClutchCall"
    )

    qr = qrcode.make(totp_uri)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")


@app.route("/mfa/validate", methods=["POST"])
def mfa_validate():
    data = request.get_json()
    code = data.get("code")

    if not code:
        return make_response("Missing MFA code.", 400)

    temp_token = request.cookies.get("temp_token")
    success, token_data = check_temp_token(temp_token)

    if not success:
        return make_response("Invalid or expired token.", 401)

    email = token_data.get("email")
    if not email:
        return make_response("Invalid token payload.", 401)

    ensure_connection()
    with conn.cursor() as c:
        c.execute(
            "SELECT email, mfa_secret FROM users WHERE email = %s",
            (email,)
        )
        user = c.fetchone()

    if not user or not user.get("mfa_secret"):
        return make_response("Unauthorized.", 401)

    totp = pyotp.TOTP(user["mfa_secret"])
    if not totp.verify(code, valid_window=1):
        return make_response("Invalid MFA code.", 401)

    access_token = create_access_token({
        "email": user["email"],
    })

    resp = make_response('{"status":"ok","mfa":false}', 200)
    resp.headers["Content-Type"] = "application/json"
    resp.set_cookie(
        "token",
        access_token,
        path="/",
        httponly=True,
        secure=False,  # change later
        samesite="Lax"
    )
    resp.delete_cookie("temp_token")

    return resp

@app.route("/validate", methods=["GET"])
def validate_token():
    token = request.cookies.get("token")

    if not token:
        return make_response("No token provided.", 400)

    payload = decode_token(token)

    if not payload or payload.get("type") != "access":
        resp = make_response("Unauthorized.", 401)
        resp.delete_cookie(
            "token",
            path="/",
            httponly=True,
            secure=False,
            samesite="Lax"
        )
        return resp

    if not payload.get("email"):
        resp = make_response("Unauthorized.", 401)
        resp.delete_cookie("token", path="/")
        return resp

    return make_response("OK", 200)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("pass")

    if not email or not password:
        return make_response("Missing email or password.", 400)

    ensure_connection()
    with conn.cursor() as c:
        c.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = c.fetchone()

    if not user:
        return make_response("Invalid email or password.", 401)

    if not bcrypt.checkpw(password.encode(), user["password_hash"].encode()):
        return make_response("Invalid email or password.", 401)

    if not user.get("mfa_secret"):
        temp_token = create_temp_token({
            "email": user["email"],
            "mfa_pending": True
        })

        resp = make_response(
            '{"status":"ok","mfa":false}',
            200
        )
        resp.headers["Content-Type"] = "application/json"
        resp.set_cookie(
            "temp_token",
            temp_token,
            path="/",
            httponly=True,
            secure=False,   # change later
            samesite="Lax"
        )
        return resp

    temp_token = create_temp_token({
        "email": user["email"],
        "mfa_pending": True
    })

    resp = make_response(
        '{"status":"ok","mfa":true}',
        200
    )
    resp.headers["Content-Type"] = "application/json"
    resp.set_cookie(
        "temp_token",
        temp_token,
        path="/",
        httponly=True,
        secure=False,   # change later
        samesite="Lax"
    )

    return resp

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("pass")

    if not email or not password:
        return make_response("Missing email or password.", 400)

    if len(password) < 8:
        return make_response("Password must be at least 8 characters.", 400)

    email = email.strip().lower()
    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    try:
        ensure_connection()
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s)",
                (email, password_hash)
            )
        conn.commit()

    except pymysql.err.IntegrityError:
        return make_response("Email already exists.", 409)

    except Exception as e:
        print("DB ERROR:", e)
        return make_response("Internal server error.", 500)

    resp = make_response('{"status":"ok"}', 200)
    resp.headers["Content-Type"] = "application/json"
    return resp

@app.route("/logout", methods=["POST"])
def logout():
    resp = make_response('{"status":"logged_out"}', 200)
    resp.headers["Content-Type"] = "application/json"
    resp.delete_cookie(
        "token",
        path="/",
        httponly=True,
        secure=False,  # change later
        samesite="Lax"
    )
    resp.delete_cookie("temp_token", path="/")
    return resp

if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=True)
