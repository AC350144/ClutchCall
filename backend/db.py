import pymysql
import os

DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def get_connection(create_db_if_missing=True):
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.err.OperationalError as e:
        if create_db_if_missing and "Unknown database" in str(e):
            conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                cursorclass=pymysql.cursors.DictCursor
            )
            with conn.cursor() as c:
                c.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
            conn.commit()
            conn.close()

            conn = pymysql.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME,
                cursorclass=pymysql.cursors.DictCursor
            )
        else:
            raise
    return conn


def create_tables():
    conn = get_connection()
    with conn.cursor() as c:

        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100),
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255),
                mfa_secret CHAR(32) UNIQUE DEFAULT NULL,
                display_name VARCHAR(255),
                avatar VARCHAR(50) DEFAULT '🎰',
                phone VARCHAR(20),
                betting_experience ENUM('beginner', 'intermediate', 'experienced', 'professional') DEFAULT 'beginner',
                favorite_sports JSON,
                monthly_budget DECIMAL(12,2) DEFAULT 500.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Add columns if they don't exist (for existing databases)
        # MySQL doesn't support ADD COLUMN IF NOT EXISTS, so we check first
        def add_column_if_not_exists(cursor, table, column, definition):
            try:
                cursor.execute(f"SELECT {column} FROM {table} LIMIT 1")
            except:
                try:
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
                except Exception as e:
                    pass  # Column might already exist
        
        add_column_if_not_exists(c, "users", "username", "VARCHAR(100)")
        add_column_if_not_exists(c, "users", "password", "VARCHAR(255)")
        add_column_if_not_exists(c, "users", "display_name", "VARCHAR(255)")
        add_column_if_not_exists(c, "users", "avatar", "VARCHAR(50) DEFAULT '🎰'")
        add_column_if_not_exists(c, "users", "phone", "VARCHAR(20)")
        add_column_if_not_exists(c, "users", "betting_experience", "ENUM('beginner', 'intermediate', 'experienced', 'professional') DEFAULT 'beginner'")
        add_column_if_not_exists(c, "users", "favorite_sports", "JSON")
        add_column_if_not_exists(c, "users", "monthly_budget", "DECIMAL(12,2) DEFAULT 500.00")

        c.execute("""
            CREATE TABLE IF NOT EXISTS bank_accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                account_holder_name VARCHAR(255),
                bank_name VARCHAR(255),
                account_type ENUM('checking', 'savings') DEFAULT 'checking',
                encrypted_routing_number TEXT NOT NULL,
                encrypted_account_number TEXT NOT NULL,
                routing_number_hash CHAR(64) NOT NULL,
                account_number_hash CHAR(64) NOT NULL,
                last_four VARCHAR(4),
                is_primary BOOLEAN DEFAULT FALSE,
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_accounts (user_id)
            )
        """)
        
        # Add last_four and is_active columns if they don't exist
        add_column_if_not_exists(c, "bank_accounts", "last_four", "VARCHAR(4)")
        add_column_if_not_exists(c, "bank_accounts", "is_active", "BOOLEAN DEFAULT TRUE")

        c.execute("""
            CREATE TABLE IF NOT EXISTS bankrolls (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                current_balance DECIMAL(12,2) NOT NULL DEFAULT 0.00,
                initial_bankroll DECIMAL(12,2) NOT NULL,
                peak_balance DECIMAL(12,2),
                lowest_balance DECIMAL(12,2),
                total_wagered DECIMAL(12,2) DEFAULT 0.00,
                total_won DECIMAL(12,2) DEFAULT 0.00,
                total_lost DECIMAL(12,2) DEFAULT 0.00,
                roi DECIMAL(5,2) DEFAULT 0.00,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_bankroll (user_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS sports (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sport_name VARCHAR(100) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS games (
                id INT AUTO_INCREMENT PRIMARY KEY,
                sport_id INT NOT NULL,
                game_name VARCHAR(255) NOT NULL,
                team_a VARCHAR(100) NOT NULL,
                team_b VARCHAR(100) NOT NULL,
                game_date DATETIME NOT NULL,
                status ENUM('scheduled','live','completed','cancelled') DEFAULT 'scheduled',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (sport_id) REFERENCES sports(id) ON DELETE CASCADE,
                INDEX idx_sport_date (sport_id, game_date),
                INDEX idx_status (status)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS bet_types (
                id INT AUTO_INCREMENT PRIMARY KEY,
                type_name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS bet_legs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                game_id INT NOT NULL,
                bet_type_id INT NOT NULL,
                selection VARCHAR(255) NOT NULL,
                odds DECIMAL(8,2) NOT NULL,
                odds_format ENUM('american','decimal','fractional') DEFAULT 'american',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
                FOREIGN KEY (bet_type_id) REFERENCES bet_types(id) ON DELETE CASCADE,
                INDEX idx_game (game_id)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS bets (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                bankroll_id INT NOT NULL,
                parlay_id INT,
                total_stake DECIMAL(12,2) NOT NULL,
                total_odds DECIMAL(10,2),
                potential_win DECIMAL(12,2),
                actual_payout DECIMAL(12,2),
                status ENUM('pending','won','lost','cancelled','push') DEFAULT 'pending',
                bet_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                settled_date DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (bankroll_id) REFERENCES bankrolls(id) ON DELETE CASCADE,
                FOREIGN KEY (parlay_id) REFERENCES bets(id) ON DELETE SET NULL,
                INDEX idx_user_status (user_id, status),
                INDEX idx_bet_date (bet_date),
                INDEX idx_settled_date (settled_date)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS bet_slip_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bet_id INT NOT NULL,
                bet_leg_id INT NOT NULL,
                leg_order INT NOT NULL,
                stake DECIMAL(12,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_bet_leg (bet_id, bet_leg_id),
                FOREIGN KEY (bet_id) REFERENCES bets(id) ON DELETE CASCADE,
                FOREIGN KEY (bet_leg_id) REFERENCES bet_legs(id) ON DELETE CASCADE
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS ai_recommendations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                game_id INT,
                bet_leg_id INT,
                sport_id INT NOT NULL,
                game_name VARCHAR(255) NOT NULL,
                selection VARCHAR(255) NOT NULL,
                odds DECIMAL(8,2) NOT NULL,
                confidence_score DECIMAL(5,2) NOT NULL,
                recommended_stake DECIMAL(5,2),
                analysis TEXT,
                ai_model VARCHAR(100),
                is_used BOOLEAN DEFAULT FALSE,
                bet_id INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE SET NULL,
                FOREIGN KEY (sport_id) REFERENCES sports(id) ON DELETE CASCADE,
                FOREIGN KEY (bet_id) REFERENCES bets(id) ON DELETE SET NULL,
                INDEX idx_user_created (user_id, created_at),
                INDEX idx_confidence (confidence_score)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS bet_statistics (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                total_bets INT DEFAULT 0,
                winning_bets INT DEFAULT 0,
                losing_bets INT DEFAULT 0,
                cancelled_bets INT DEFAULT 0,
                win_rate DECIMAL(5,2) DEFAULT 0.00,
                average_odds DECIMAL(8,2),
                total_wagered DECIMAL(12,2) DEFAULT 0.00,
                total_returned DECIMAL(12,2) DEFAULT 0.00,
                gross_profit DECIMAL(12,2) DEFAULT 0.00,
                roi DECIMAL(5,2) DEFAULT 0.00,
                longest_win_streak INT DEFAULT 0,
                longest_loss_streak INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_stats (user_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS bet_analysis (
                id INT AUTO_INCREMENT PRIMARY KEY,
                bet_id INT NOT NULL,
                quality_score DECIMAL(5,2),
                ai_analysis TEXT,
                user_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_bet_analysis (bet_id),
                FOREIGN KEY (bet_id) REFERENCES bets(id) ON DELETE CASCADE
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS budget_recommendations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                income DECIMAL(12,2) NOT NULL,
                fixed_expenses DECIMAL(12,2) NOT NULL,
                savings_goal DECIMAL(12,2) NOT NULL,
                months_to_goal INT NOT NULL,
                food_budget DECIMAL(12,2),
                entertainment_budget DECIMAL(12,2),
                shopping_budget DECIMAL(12,2),
                monthly_savings DECIMAL(12,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_user_created (user_id, created_at)
            )
        """)

        c.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                action VARCHAR(255) NOT NULL,
                entity_type VARCHAR(100),
                entity_id INT,
                old_value JSON,
                new_value JSON,
                ip_address VARCHAR(45),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                INDEX idx_user_action (user_id, action),
                INDEX idx_created_at (created_at)
            )
        """)

        # Seed data
        c.execute("""
            INSERT IGNORE INTO bet_types (type_name, description) VALUES
            ('Moneyline','Pick the winner'),
            ('Spread','Pick a team to win by a margin'),
            ('Total','Over/Under total score'),
            ('Parlay','Multiple bets combined'),
            ('Prop Bet','Specific events'),
            ('Futures','Future outcome bets')
        """)

        c.execute("""
            INSERT IGNORE INTO sports (sport_name) VALUES
            ('NBA'),('NFL'),('NHL'),('MLB'),('Soccer')
        """)

    conn.commit()
    return conn
