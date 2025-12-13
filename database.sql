USE ClutchCall;

CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(255) UNIQUE NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE bankrolls (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  current_balance DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
  initial_bankroll DECIMAL(12, 2) NOT NULL,
  peak_balance DECIMAL(12, 2),
  lowest_balance DECIMAL(12, 2),
  total_wagered DECIMAL(12, 2) DEFAULT 0.00,
  total_won DECIMAL(12, 2) DEFAULT 0.00,
  total_lost DECIMAL(12, 2) DEFAULT 0.00,
  roi DECIMAL(5, 2) DEFAULT 0.00,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY unique_user_bankroll (user_id)
);

CREATE TABLE sports (
  id INT PRIMARY KEY AUTO_INCREMENT,
  sport_name VARCHAR(100) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE games (
  id INT PRIMARY KEY AUTO_INCREMENT,
  sport_id INT NOT NULL,
  game_name VARCHAR(255) NOT NULL,
  team_a VARCHAR(100) NOT NULL,
  team_b VARCHAR(100) NOT NULL,
  game_date DATETIME NOT NULL,
  status ENUM('scheduled', 'live', 'completed', 'cancelled') DEFAULT 'scheduled',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (sport_id) REFERENCES sports(id) ON DELETE CASCADE,
  INDEX idx_sport_date (sport_id, game_date),
  INDEX idx_status (status)
);

CREATE TABLE bet_types (
  id INT PRIMARY KEY AUTO_INCREMENT,
  type_name VARCHAR(50) UNIQUE NOT NULL,
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO bet_types (type_name, description) VALUES
('Moneyline', 'Pick the winner of the game'),
('Spread', 'Pick a team to win by or within a certain point margin'),
('Total', 'Pick if the total combined score will be over or under a certain number'),
('Parlay', 'Combine multiple bets into one'),
('Prop Bet', 'Bet on specific player or game events'),
('Futures', 'Bet on outcomes that will be decided in the future');

CREATE TABLE bet_legs (
  id INT PRIMARY KEY AUTO_INCREMENT,
  game_id INT NOT NULL,
  bet_type_id INT NOT NULL,
  selection VARCHAR(255) NOT NULL,
  odds DECIMAL(8, 2) NOT NULL,
  odds_format ENUM('american', 'decimal', 'fractional') DEFAULT 'american',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
  FOREIGN KEY (bet_type_id) REFERENCES bet_types(id) ON DELETE CASCADE,
  INDEX idx_game (game_id)
);

CREATE TABLE bets (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  bankroll_id INT NOT NULL,
  parlay_id INT,
  total_stake DECIMAL(12, 2) NOT NULL,
  total_odds DECIMAL(10, 2),
  potential_win DECIMAL(12, 2),
  actual_payout DECIMAL(12, 2),
  status ENUM('pending', 'won', 'lost', 'cancelled', 'push') DEFAULT 'pending',
  bet_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  settled_date DATETIME,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (bankroll_id) REFERENCES bankrolls(id) ON DELETE CASCADE,
  FOREIGN KEY (parlay_id) REFERENCES bets(id) ON DELETE SET NULL,
  INDEX idx_user_status (user_id, status),
  INDEX idx_bet_date (bet_date),
  INDEX idx_settled_date (settled_date)
);

CREATE TABLE bet_slip_items (
  id INT PRIMARY KEY AUTO_INCREMENT,
  bet_id INT NOT NULL,
  bet_leg_id INT NOT NULL,
  leg_order INT NOT NULL,
  stake DECIMAL(12, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (bet_id) REFERENCES bets(id) ON DELETE CASCADE,
  FOREIGN KEY (bet_leg_id) REFERENCES bet_legs(id) ON DELETE CASCADE,
  INDEX idx_bet (bet_id),
  UNIQUE KEY unique_bet_leg (bet_id, bet_leg_id)
);

CREATE TABLE ai_recommendations (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  game_id INT,
  bet_leg_id INT,
  sport_id INT NOT NULL,
  game_name VARCHAR(255) NOT NULL,
  selection VARCHAR(255) NOT NULL,
  odds DECIMAL(8, 2) NOT NULL,
  confidence_score DECIMAL(5, 2) NOT NULL,
  recommended_stake DECIMAL(5, 2),
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
);

CREATE TABLE bet_statistics (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  total_bets INT DEFAULT 0,
  winning_bets INT DEFAULT 0,
  losing_bets INT DEFAULT 0,
  cancelled_bets INT DEFAULT 0,
  win_rate DECIMAL(5, 2) DEFAULT 0.00,
  average_odds DECIMAL(8, 2),
  total_wagered DECIMAL(12, 2) DEFAULT 0.00,
  total_returned DECIMAL(12, 2) DEFAULT 0.00,
  gross_profit DECIMAL(12, 2) DEFAULT 0.00,
  roi DECIMAL(5, 2) DEFAULT 0.00,
  longest_win_streak INT DEFAULT 0,
  longest_loss_streak INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  UNIQUE KEY unique_user_stats (user_id)
);

CREATE TABLE bet_analysis (
  id INT PRIMARY KEY AUTO_INCREMENT,
  bet_id INT NOT NULL,
  quality_score DECIMAL(5, 2),
  ai_analysis TEXT,
  user_notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (bet_id) REFERENCES bets(id) ON DELETE CASCADE,
  UNIQUE KEY unique_bet_analysis (bet_id)
);

CREATE TABLE budget_recommendations (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  income DECIMAL(12, 2) NOT NULL,
  fixed_expenses DECIMAL(12, 2) NOT NULL,
  savings_goal DECIMAL(12, 2) NOT NULL,
  months_to_goal INT NOT NULL,
  food_budget DECIMAL(12, 2),
  entertainment_budget DECIMAL(12, 2),
  shopping_budget DECIMAL(12, 2),
  monthly_savings DECIMAL(12, 2),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_created (user_id, created_at)
);

CREATE TABLE audit_logs (
  id INT PRIMARY KEY AUTO_INCREMENT,
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
);

CREATE INDEX idx_bankroll_user ON bankrolls(user_id);
CREATE INDEX idx_bets_user_date ON bets(user_id, bet_date);
CREATE INDEX idx_recommendations_user ON ai_recommendations(user_id);
CREATE INDEX idx_statistics_user ON bet_statistics(user_id);
CREATE INDEX idx_games_sport ON games(sport_id);


INSERT INTO sports (sport_name) VALUES
('NBA'),
('NFL'),
('NHL'),
('MLB'),
('Soccer');

INSERT INTO users (username, email, password_hash, is_active) VALUES
('demo_user', 'demo@clutchcall.com', '$2b$12$demo_hash_example', TRUE);

INSERT INTO bankrolls (user_id, current_balance, initial_bankroll, peak_balance, lowest_balance)
VALUES (1, 5000.00, 5000.00, 5000.00, 5000.00);

INSERT INTO games (sport_id, game_name, team_a, team_b, game_date, status)
VALUES (1, 'Lakers vs Celtics', 'Lakers', 'Celtics', DATE_ADD(NOW(), INTERVAL 3 DAY), 'scheduled');

INSERT INTO bet_statistics (user_id, total_bets, winning_bets, losing_bets, win_rate)
VALUES (1, 0, 0, 0, 0.00);
