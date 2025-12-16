from flask import Flask, render_template, request, jsonify, make_response, send_file
import re
from db import create_tables
import datetime
import os
import jwt
import bcrypt
import pymysql
import io
import pyotp
import qrcode

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
    }
}

def calculate_remaining_budget():
    total_spent = sum(user_data["categories"].values()) + user_data["savings"]
    return user_data["income"] - total_spent

def handle_input(user_input):
    text = user_input.lower().strip()

    #Greet user
    if text in ["hi", "hello", "hey"]:
        return ("Hey there! I'm your AI Financial Assistant.<br>"
                "You can ask me to:<br>"
                "- Update your income or expenses<br>"
                "- Add to food, bills, or entertainment<br>"
                "- Type 'help' for a list of all commands!")

    if "help" in text:
        return ("Here's what you can say:<br>"
                "- 'Show my budget'<br>"
                "- 'Add 200 to food'<br>"
                "- 'Update entertainment to 400'<br>"
                "- 'Set income to 5000'<br>"
                "- 'Update savings to 300'<br>"
                "- 'Reset data'")

    # reset data 
    if "reset" in text:
        user_data.update({
            "income": 3000,
            "expenses": 1500,
            "savings": 200,
            "categories": {"food": 300, "entertainment": 200, "bills": 1000}
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

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    reply = handle_input(user_message)
    return jsonify({"response": reply})

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
