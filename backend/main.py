from flask import Flask, render_template, request, jsonify, make_response, send_file
import re
import hashlib
from db import create_tables, get_connection
import datetime
import os
import jwt
import bcrypt
import pymysql
import io
import pyotp
import qrcode
from app.bet_parser import parse_bet_text, get_stake_recommendation
from app.bank_account import (
    BankAccount,
    encrypt_data,
    decrypt_data,
    validate_routing_number,
    validate_account_number,
    mask_account_number,
    mask_routing_number
)

app = Flask(__name__)

def get_db():
    """Get a fresh database connection"""
    return get_connection()
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


def get_current_user():
    """
    Get the current authenticated user from the access token.
    Returns user dict on success, or None on failure.
    """
    token = request.cookies.get("token")
    
    if not token:
        return None
    
    payload = decode_token(token)
    
    if not payload or payload.get("type") != "access":
        return None
    
    email = payload.get("email")
    if not email:
        return None
    
    db_conn = get_db()
    cursor = db_conn.cursor(pymysql.cursors.DictCursor)
    try:
        cursor.execute("SELECT id, email, is_active FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
    finally:
        cursor.close()
        db_conn.close()
    
    if not user or not user.get("is_active", True):
        return None
    
    return user


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

    # Check password - support both password and password_hash columns
    stored_hash = user.get("password_hash") or user.get("password")
    if not stored_hash:
        return make_response("Invalid email or password.", 401)
    
    if not bcrypt.checkpw(password.encode(), stored_hash.encode()):
        return make_response("Invalid email or password.", 401)
    
    # Update username and display_name if missing (for existing users)
    if not user.get("username") or not user.get("display_name"):
        username = email.split('@')[0]
        display_name = username.capitalize()
        try:
            with conn.cursor() as c:
                c.execute(
                    "UPDATE users SET username = %s, display_name = %s WHERE id = %s",
                    (username, display_name, user["id"])
                )
            conn.commit()
        except Exception as e:
            print(f"Error updating username: {e}")
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
    # Derive username from email (part before @)
    username = email.split('@')[0]
    display_name = username.capitalize()
    
    password_hash = bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt()
    ).decode()

    try:
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO users (email, password_hash, username, display_name, password) VALUES (%s, %s, %s, %s, %s)",
                (email, password_hash, username, display_name, password_hash)
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


@app.route("/parse-bet", methods=["POST"])
def parse_bet():
    """
    Parse and analyze a bet slip text.
    
    Request body:
    {
        "betText": "Lakers -3.5 @ -110, Warriors ML @ +150",
        "bankroll": 5000  (optional)
    }
    
    Returns parsed legs with AI analysis and recommendations.
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    bet_text = data.get("betText", "")
    bankroll = data.get("bankroll", 1000)
    
    if not bet_text:
        return jsonify({"error": "No bet text provided"}), 400
    
    try:
        result = parse_bet_text(bet_text)
        
        if result.get("success"):
            # Add stake recommendations if bankroll provided
            stake_rec = get_stake_recommendation(
                bankroll,
                result.get("qualityScore", 50),
                result.get("recommendation", "caution")
            )
            result["stakeRecommendation"] = stake_rec
        
        return jsonify(result)
    
    except Exception as e:
        print(f"Error parsing bet: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to parse bet text",
            "legs": [],
            "qualityScore": 0,
            "analysis": "An error occurred while parsing.",
            "recommendation": "avoid"
        }), 500


@app.route("/analyze-odds", methods=["POST"])
def analyze_odds():
    """
    Analyze odds and calculate probabilities/payouts.
    
    Request body:
    {
        "odds": [-110, +150, -200],
        "stake": 100
    }
    """
    from app.bet_parser import calculate_implied_probability, calculate_parlay_odds, calculate_payout
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    odds_list = data.get("odds", [])
    stake = data.get("stake", 100)
    
    if not odds_list:
        return jsonify({"error": "No odds provided"}), 400
    
    try:
        analysis = []
        for odds in odds_list:
            prob = calculate_implied_probability(odds)
            payout = calculate_payout(stake, odds)
            analysis.append({
                "odds": odds,
                "impliedProbability": round(prob * 100, 2),
                "potentialPayout": round(payout, 2),
                "totalReturn": round(stake + payout, 2)
            })
        
        parlay_odds = calculate_parlay_odds(odds_list) if len(odds_list) > 1 else odds_list[0]
        parlay_payout = calculate_payout(stake, parlay_odds)
        
        # Calculate combined probability
        combined_prob = 1
        for odds in odds_list:
            combined_prob *= calculate_implied_probability(odds)
        
        return jsonify({
            "individualLegs": analysis,
            "parlay": {
                "combinedOdds": parlay_odds,
                "combinedProbability": round(combined_prob * 100, 2),
                "potentialPayout": round(parlay_payout, 2),
                "totalReturn": round(stake + parlay_payout, 2)
            },
            "stake": stake
        })
    
    except Exception as e:
        print(f"Error analyzing odds: {e}")
        return jsonify({"error": "Failed to analyze odds"}), 500


# ===== Profile Endpoints =====

@app.route("/profile", methods=["GET"])
def get_profile():
    """Get the current user's profile information"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("""
            SELECT id, username, email, display_name, avatar, phone, 
                   betting_experience, favorite_sports, monthly_budget, created_at
            FROM users WHERE id = %s
        """, (user["id"],))
        
        profile = cursor.fetchone()
        
        if not profile:
            return jsonify({"error": "Profile not found"}), 404
        
        # Parse favorite_sports if stored as JSON string
        favorite_sports = profile.get("favorite_sports") or "[]"
        if isinstance(favorite_sports, str):
            try:
                import json
                favorite_sports = json.loads(favorite_sports)
            except:
                favorite_sports = []
        
        return jsonify({
            "id": profile["id"],
            "username": profile["username"],
            "email": profile.get("email", ""),
            "displayName": profile.get("display_name") or profile["username"],
            "avatar": profile.get("avatar") or "🎰",
            "phone": profile.get("phone") or "",
            "bettingExperience": profile.get("betting_experience") or "beginner",
            "favoriteSports": favorite_sports,
            "monthlyBudget": profile.get("monthly_budget") or 500,
            "createdAt": profile["created_at"].isoformat() if profile.get("created_at") else None
        })
    
    except Exception as e:
        print(f"Error fetching profile: {e}")
        return jsonify({"error": "Failed to fetch profile"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/profile", methods=["PUT"])
def update_profile():
    """Update the current user's profile information"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        import json
        
        # Build update query dynamically based on provided fields
        updates = []
        values = []
        
        if "displayName" in data:
            updates.append("display_name = %s")
            values.append(data["displayName"])
        
        if "avatar" in data:
            updates.append("avatar = %s")
            values.append(data["avatar"])
        
        if "phone" in data:
            updates.append("phone = %s")
            values.append(data["phone"])
        
        if "bettingExperience" in data:
            updates.append("betting_experience = %s")
            values.append(data["bettingExperience"])
        
        if "favoriteSports" in data:
            updates.append("favorite_sports = %s")
            values.append(json.dumps(data["favoriteSports"]))
        
        if "monthlyBudget" in data:
            updates.append("monthly_budget = %s")
            values.append(data["monthlyBudget"])
        
        if not updates:
            return jsonify({"message": "No fields to update"}), 200
        
        values.append(user["id"])
        
        cursor.execute(f"""
            UPDATE users SET {', '.join(updates)} WHERE id = %s
        """, tuple(values))
        
        conn.commit()
        
        return jsonify({"message": "Profile updated successfully"})
    
    except Exception as e:
        conn.rollback()
        print(f"Error updating profile: {e}")
        return jsonify({"error": "Failed to update profile"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/change-password", methods=["POST"])
def change_password():
    """Change the current user's password"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")
    
    if not current_password or not new_password:
        return jsonify({"error": "Current and new password are required"}), 400
    
    if len(new_password) < 8:
        return jsonify({"error": "New password must be at least 8 characters"}), 400
    
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Get current password hash
        cursor.execute("SELECT password FROM users WHERE id = %s", (user["id"],))
        result = cursor.fetchone()
        
        if not result:
            return jsonify({"error": "User not found"}), 404
        
        # Verify current password
        stored_hash = result["password"]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        
        if not bcrypt.checkpw(current_password.encode('utf-8'), stored_hash):
            return jsonify({"error": "Current password is incorrect"}), 400
        
        # Hash new password
        new_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update password
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (new_hash, user["id"]))
        conn.commit()
        
        return jsonify({"message": "Password changed successfully"})
    
    except Exception as e:
        conn.rollback()
        print(f"Error changing password: {e}")
        return jsonify({"error": "Failed to change password"}), 500
    finally:
        cursor.close()
        conn.close()


# ===== Bank Account Endpoints =====

@app.route("/bank-accounts", methods=["GET"])
def get_bank_accounts():
    """Get all bank accounts for the current user (masked)"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("""
            SELECT id, bank_name, account_type, last_four, is_primary, created_at 
            FROM bank_accounts 
            WHERE user_id = %s AND is_active = TRUE
            ORDER BY is_primary DESC, created_at DESC
        """, (user["id"],))
        
        accounts = cursor.fetchall()
        
        return jsonify({
            "accounts": [{
                "id": acc["id"],
                "bankName": acc["bank_name"],
                "accountType": acc["account_type"],
                "lastFour": acc["last_four"],
                "isPrimary": bool(acc["is_primary"]),
                "createdAt": acc["created_at"].isoformat() if acc["created_at"] else None
            } for acc in accounts]
        })
    
    except Exception as e:
        print(f"Error fetching bank accounts: {e}")
        return jsonify({"error": "Failed to fetch bank accounts"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/bank-accounts", methods=["POST"])
def add_bank_account():
    """Add a new bank account with encrypted data"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    
    # Validate required fields
    required_fields = ["bankName", "routingNumber", "accountNumber", "accountType"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    routing_number = data["routingNumber"]
    account_number = data["accountNumber"]
    bank_name = data["bankName"]
    account_type = data.get("accountType", "checking")
    is_primary = data.get("isPrimary", False)
    
    # Validate routing number
    if not validate_routing_number(routing_number):
        return jsonify({"error": "Invalid routing number"}), 400
    
    # Validate account number
    if not validate_account_number(account_number):
        return jsonify({"error": "Invalid account number. Must be 4-17 digits."}), 400
    
    # Validate account type
    if account_type not in ["checking", "savings"]:
        return jsonify({"error": "Account type must be 'checking' or 'savings'"}), 400
    
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Check account limit (max 5 accounts per user)
        cursor.execute(
            "SELECT COUNT(*) as count FROM bank_accounts WHERE user_id = %s AND is_active = TRUE",
            (user["id"],)
        )
        result = cursor.fetchone()
        if result and result["count"] >= 5:
            return jsonify({"error": "Maximum of 5 bank accounts allowed"}), 400
        
        # Check for duplicate account
        account_hash = hashlib.sha256(account_number.encode()).hexdigest()
        routing_hash = hashlib.sha256(routing_number.encode()).hexdigest()
        
        cursor.execute("""
            SELECT id FROM bank_accounts 
            WHERE user_id = %s AND routing_number_hash = %s AND account_number_hash = %s AND is_active = TRUE
        """, (user["id"], routing_hash, account_hash))
        
        if cursor.fetchone():
            return jsonify({"error": "This bank account is already linked"}), 400
        
        # Encrypt sensitive data
        encrypted_routing = encrypt_data(routing_number)
        encrypted_account = encrypt_data(account_number)
        last_four = mask_account_number(account_number)
        
        # If this is primary, unset other primary accounts
        if is_primary:
            cursor.execute(
                "UPDATE bank_accounts SET is_primary = FALSE WHERE user_id = %s",
                (user["id"],)
            )
        
        # Insert new bank account
        cursor.execute("""
            INSERT INTO bank_accounts 
            (user_id, bank_name, account_type, encrypted_routing_number, encrypted_account_number, 
             routing_number_hash, account_number_hash, last_four, is_primary, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, TRUE)
        """, (user["id"], bank_name, account_type, encrypted_routing, encrypted_account,
              routing_hash, account_hash, last_four, is_primary))
        
        conn.commit()
        account_id = cursor.lastrowid
        
        return jsonify({
            "message": "Bank account added successfully",
            "account": {
                "id": account_id,
                "bankName": bank_name,
                "accountType": account_type,
                "lastFour": last_four,
                "isPrimary": is_primary
            }
        }), 201
    
    except Exception as e:
        conn.rollback()
        print(f"Error adding bank account: {e}")
        return jsonify({"error": "Failed to add bank account"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/bank-accounts/<int:account_id>", methods=["DELETE"])
def delete_bank_account(account_id):
    """Soft delete a bank account"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Verify account belongs to user
        cursor.execute(
            "SELECT id, is_primary FROM bank_accounts WHERE id = %s AND user_id = %s AND is_active = TRUE",
            (account_id, user["id"])
        )
        account = cursor.fetchone()
        
        if not account:
            return jsonify({"error": "Bank account not found"}), 404
        
        # Soft delete
        cursor.execute(
            "UPDATE bank_accounts SET is_active = FALSE WHERE id = %s",
            (account_id,)
        )
        
        # If this was primary, set another account as primary
        if account["is_primary"]:
            cursor.execute("""
                UPDATE bank_accounts 
                SET is_primary = TRUE 
                WHERE user_id = %s AND is_active = TRUE 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (user["id"],))
        
        conn.commit()
        
        return jsonify({"message": "Bank account removed successfully"})
    
    except Exception as e:
        conn.rollback()
        print(f"Error deleting bank account: {e}")
        return jsonify({"error": "Failed to remove bank account"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/bank-accounts/<int:account_id>/primary", methods=["PUT"])
def set_primary_bank_account(account_id):
    """Set a bank account as primary"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    
    conn = get_db()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # Verify account belongs to user
        cursor.execute(
            "SELECT id FROM bank_accounts WHERE id = %s AND user_id = %s AND is_active = TRUE",
            (account_id, user["id"])
        )
        
        if not cursor.fetchone():
            return jsonify({"error": "Bank account not found"}), 404
        
        # Unset all primary
        cursor.execute(
            "UPDATE bank_accounts SET is_primary = FALSE WHERE user_id = %s",
            (user["id"],)
        )
        
        # Set new primary
        cursor.execute(
            "UPDATE bank_accounts SET is_primary = TRUE WHERE id = %s",
            (account_id,)
        )
        
        conn.commit()
        
        return jsonify({"message": "Primary account updated successfully"})
    
    except Exception as e:
        conn.rollback()
        print(f"Error setting primary account: {e}")
        return jsonify({"error": "Failed to update primary account"}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    app.run(host="localhost", port=3000, debug=True)
