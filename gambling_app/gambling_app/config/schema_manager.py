import mysql.connector
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class SchemaManager:
    def __init__(self):
        # Connect without DB first to ensure the DB itself exists
        self.base_conn = mysql.connector.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )

    def initialize_schema(self):
        cursor = self.base_conn.cursor()
        try:
            logger.info(f"Rebuilding database '{settings.DB_NAME}'...")
            cursor.execute(f"DROP DATABASE IF EXISTS {settings.DB_NAME}")
            cursor.execute(f"CREATE DATABASE {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE {settings.DB_NAME}")

            # 1. GAMBLERS
            cursor.execute("""
                CREATE TABLE GAMBLERS (
                    gambler_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL, full_name VARCHAR(100), email VARCHAR(100) UNIQUE,
                    is_active BOOLEAN DEFAULT TRUE, initial_stake DECIMAL(15,2) NOT NULL, current_stake DECIMAL(15,2) NOT NULL,
                    win_threshold DECIMAL(15,2) NOT NULL, loss_threshold DECIMAL(15,2) NOT NULL, min_required_stake DECIMAL(15,2) DEFAULT 0.00,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # 2. BETTING_PREFERENCES
            cursor.execute("""
                CREATE TABLE BETTING_PREFERENCES (
                    preference_id BIGINT AUTO_INCREMENT PRIMARY KEY, gambler_id BIGINT UNIQUE NOT NULL,
                    min_bet DECIMAL(15,2) NOT NULL, max_bet DECIMAL(15,2) NOT NULL, preferred_game_type VARCHAR(50) DEFAULT 'DEFAULT',
                    auto_play_enabled BOOLEAN DEFAULT FALSE, auto_play_max_games INT DEFAULT 10,
                    session_loss_limit DECIMAL(15,2) DEFAULT 0.00, session_win_target DECIMAL(15,2) DEFAULT 0.00,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (gambler_id) REFERENCES GAMBLERS(gambler_id) ON DELETE CASCADE
                )
            """)

            # 3. SESSIONS (NEW)
            cursor.execute("""
                CREATE TABLE SESSIONS (
                    session_id BIGINT AUTO_INCREMENT PRIMARY KEY, gambler_id BIGINT NOT NULL,
                    status VARCHAR(20) NOT NULL, end_reason VARCHAR(50) NULL, starting_stake DECIMAL(15,2) NOT NULL,
                    ending_stake DECIMAL(15,2) NULL, peak_stake DECIMAL(15,2) NOT NULL, lowest_stake DECIMAL(15,2) NOT NULL,
                    max_games INT DEFAULT 100, games_played INT DEFAULT 0, total_pause_seconds INT DEFAULT 0,
                    started_at DATETIME DEFAULT CURRENT_TIMESTAMP, ended_at DATETIME NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (gambler_id) REFERENCES GAMBLERS(gambler_id) ON DELETE CASCADE
                )
            """)

            # 4. SESSION_PARAMETERS (NEW)
            cursor.execute("""
                CREATE TABLE SESSION_PARAMETERS (
                    parameter_id BIGINT AUTO_INCREMENT PRIMARY KEY, session_id BIGINT UNIQUE NOT NULL,
                    lower_limit DECIMAL(15,2) NOT NULL, upper_limit DECIMAL(15,2) NOT NULL, min_bet DECIMAL(15,2) NOT NULL,
                    max_bet DECIMAL(15,2) NOT NULL, default_win_probability DECIMAL(5,4) DEFAULT 0.4500,
                    max_session_minutes INT DEFAULT 120, strict_mode BOOLEAN DEFAULT TRUE, created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES SESSIONS(session_id) ON DELETE CASCADE
                )
            """)

            # 5. PAUSE_RECORDS (NEW)
            cursor.execute("""
                CREATE TABLE PAUSE_RECORDS (
                    pause_id BIGINT AUTO_INCREMENT PRIMARY KEY, session_id BIGINT NOT NULL,
                    pause_reason VARCHAR(100) NOT NULL, paused_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resumed_at DATETIME NULL, pause_seconds INT DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES SESSIONS(session_id) ON DELETE CASCADE
                )
            """)

            # 6. STAKE_TRANSACTIONS (UPDATED FK)
            cursor.execute("""
                CREATE TABLE STAKE_TRANSACTIONS (
                    transaction_id BIGINT AUTO_INCREMENT PRIMARY KEY, session_id BIGINT NULL, gambler_id BIGINT NOT NULL,
                    bet_id BIGINT NULL, game_id BIGINT NULL, transaction_type VARCHAR(50) NOT NULL, amount DECIMAL(15,2) NOT NULL,
                    balance_before DECIMAL(15,2) NOT NULL, balance_after DECIMAL(15,2) NOT NULL, transaction_ref VARCHAR(100), created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (gambler_id) REFERENCES GAMBLERS(gambler_id) ON DELETE CASCADE,
                    FOREIGN KEY (session_id) REFERENCES SESSIONS(session_id) ON DELETE SET NULL
                )
            """)

            # 7. BETTING_STRATEGIES
            cursor.execute("""
                CREATE TABLE BETTING_STRATEGIES (
                    strategy_id TINYINT AUTO_INCREMENT PRIMARY KEY, strategy_code VARCHAR(50) UNIQUE NOT NULL, strategy_name VARCHAR(100) NOT NULL,
                    strategy_type VARCHAR(50) NOT NULL, is_progressive BOOLEAN DEFAULT FALSE, is_active BOOLEAN DEFAULT TRUE, created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("INSERT IGNORE INTO BETTING_STRATEGIES (strategy_code, strategy_name, strategy_type, is_progressive) VALUES ('FIXED', 'Fixed', 'FLAT', FALSE), ('PERCENTAGE', 'Percentage', 'PROPORTIONAL', FALSE), ('MARTINGALE', 'Martingale', 'PROGRESSIVE', TRUE), ('REVERSE_MARTINGALE', 'Reverse Martingale', 'PROGRESSIVE', TRUE)")

            # 8. BETS & GAME_RECORDS (UPDATED FK)
            cursor.execute("""
                CREATE TABLE BETS (
                    bet_id BIGINT AUTO_INCREMENT PRIMARY KEY, session_id BIGINT NULL, gambler_id BIGINT NOT NULL, strategy_id TINYINT NULL,
                    game_index INT DEFAULT 1, bet_amount DECIMAL(15,2) NOT NULL, win_probability DECIMAL(5,4) NOT NULL, odds_type VARCHAR(50) DEFAULT 'FIXED',
                    odds_value DECIMAL(10,2) DEFAULT 2.0, potential_win DECIMAL(15,2) NOT NULL, stake_before DECIMAL(15,2) NOT NULL, stake_after DECIMAL(15,2) NULL,
                    is_settled BOOLEAN DEFAULT FALSE, placed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (gambler_id) REFERENCES GAMBLERS(gambler_id) ON DELETE CASCADE,
                    FOREIGN KEY (strategy_id) REFERENCES BETTING_STRATEGIES(strategy_id), FOREIGN KEY (session_id) REFERENCES SESSIONS(session_id) ON DELETE SET NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE GAME_RECORDS (
                    game_id BIGINT AUTO_INCREMENT PRIMARY KEY, session_id BIGINT NULL, bet_id BIGINT UNIQUE NOT NULL,
                    outcome VARCHAR(20) NOT NULL, payout_amount DECIMAL(15,2) DEFAULT 0.00, loss_amount DECIMAL(15,2) DEFAULT 0.00,
                    net_change DECIMAL(15,2) NOT NULL, stake_before DECIMAL(15,2) NOT NULL, stake_after DECIMAL(15,2) NOT NULL, resolved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bet_id) REFERENCES BETS(bet_id) ON DELETE CASCADE, FOREIGN KEY (session_id) REFERENCES SESSIONS(session_id) ON DELETE SET NULL
                )
            """)

            self.base_conn.commit()
            logger.info("Schema fully rebuilt for UC4.")
        except mysql.connector.Error as err:
            logger.error(f"Schema generation failed: {err}")
            raise
        finally:
            cursor.close()
            self.base_conn.close()