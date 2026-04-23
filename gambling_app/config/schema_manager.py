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
        """Creates the database and UC1 tables if they do not exist."""
        cursor = self.base_conn.cursor()
        try:
            logger.info(f"Ensuring database '{settings.DB_NAME}' exists...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.execute(f"USE {settings.DB_NAME}")

            # 1. GAMBLERS
            logger.info("Ensuring table GAMBLERS exists...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS GAMBLERS (
                    gambler_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    full_name VARCHAR(100),
                    email VARCHAR(100) UNIQUE,
                    is_active BOOLEAN DEFAULT TRUE,
                    initial_stake DECIMAL(15,2) NOT NULL,
                    current_stake DECIMAL(15,2) NOT NULL,
                    win_threshold DECIMAL(15,2) NOT NULL,
                    loss_threshold DECIMAL(15,2) NOT NULL,
                    min_required_stake DECIMAL(15,2) DEFAULT 0.00,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            """)

            # 2. BETTING_PREFERENCES
            logger.info("Ensuring table BETTING_PREFERENCES exists...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS BETTING_PREFERENCES (
                    preference_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    gambler_id BIGINT UNIQUE NOT NULL,
                    min_bet DECIMAL(15,2) NOT NULL,
                    max_bet DECIMAL(15,2) NOT NULL,
                    preferred_game_type VARCHAR(50) DEFAULT 'DEFAULT',
                    auto_play_enabled BOOLEAN DEFAULT FALSE,
                    auto_play_max_games INT DEFAULT 10,
                    session_loss_limit DECIMAL(15,2) DEFAULT 0.00,
                    session_win_target DECIMAL(15,2) DEFAULT 0.00,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (gambler_id) REFERENCES GAMBLERS(gambler_id) ON DELETE CASCADE
                )
            """)

            # 3. STAKE_TRANSACTIONS
            logger.info("Ensuring table STAKE_TRANSACTIONS exists...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS STAKE_TRANSACTIONS (
                    transaction_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    session_id BIGINT NULL,
                    gambler_id BIGINT NOT NULL,
                    bet_id BIGINT NULL,
                    game_id BIGINT NULL,
                    transaction_type VARCHAR(50) NOT NULL,
                    amount DECIMAL(15,2) NOT NULL,
                    balance_before DECIMAL(15,2) NOT NULL,
                    balance_after DECIMAL(15,2) NOT NULL,
                    transaction_ref VARCHAR(100),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (gambler_id) REFERENCES GAMBLERS(gambler_id) ON DELETE CASCADE
                )
            """)

            # 4. BETTING_STRATEGIES
            logger.info("Ensuring table BETTING_STRATEGIES exists...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS BETTING_STRATEGIES (
                    strategy_id TINYINT AUTO_INCREMENT PRIMARY KEY,
                    strategy_code VARCHAR(50) UNIQUE NOT NULL,
                    strategy_name VARCHAR(100) NOT NULL,
                    strategy_type VARCHAR(50) NOT NULL,
                    is_progressive BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Seed Strategies
            cursor.execute("""
                INSERT IGNORE INTO BETTING_STRATEGIES (strategy_code, strategy_name, strategy_type, is_progressive) VALUES 
                ('FIXED', 'Fixed Amount Strategy', 'FLAT', FALSE),
                ('PERCENTAGE', 'Percentage of Stake', 'PROPORTIONAL', FALSE),
                ('MARTINGALE', 'Martingale (Double on Loss)', 'PROGRESSIVE', TRUE),
                ('REVERSE_MARTINGALE', 'Reverse Martingale (Double on Win)', 'PROGRESSIVE', TRUE),
                ('FIBONACCI', 'Fibonacci Sequence', 'PROGRESSIVE', TRUE)
            """)

            # 5. BETS
            logger.info("Ensuring table BETS exists...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS BETS (
                    bet_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    session_id BIGINT NULL,
                    gambler_id BIGINT NOT NULL,
                    strategy_id TINYINT NULL,
                    game_index INT DEFAULT 1,
                    bet_amount DECIMAL(15,2) NOT NULL,
                    win_probability DECIMAL(5,4) NOT NULL,
                    odds_type VARCHAR(50) DEFAULT 'FIXED',
                    odds_value DECIMAL(10,2) DEFAULT 2.0,
                    potential_win DECIMAL(15,2) NOT NULL,
                    stake_before DECIMAL(15,2) NOT NULL,
                    stake_after DECIMAL(15,2) NULL,
                    is_settled BOOLEAN DEFAULT FALSE,
                    placed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (gambler_id) REFERENCES GAMBLERS(gambler_id) ON DELETE CASCADE,
                    FOREIGN KEY (strategy_id) REFERENCES BETTING_STRATEGIES(strategy_id)
                )
            """)

            # 6. GAME_RECORDS
            logger.info("Ensuring table GAME_RECORDS exists...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS GAME_RECORDS (
                    game_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    session_id BIGINT NULL,
                    bet_id BIGINT UNIQUE NOT NULL,
                    outcome VARCHAR(20) NOT NULL,
                    payout_amount DECIMAL(15,2) DEFAULT 0.00,
                    loss_amount DECIMAL(15,2) DEFAULT 0.00,
                    net_change DECIMAL(15,2) NOT NULL,
                    stake_before DECIMAL(15,2) NOT NULL,
                    stake_after DECIMAL(15,2) NOT NULL,
                    resolved_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (bet_id) REFERENCES BETS(bet_id) ON DELETE CASCADE
                )
            """)

            self.base_conn.commit()
            logger.info("Schema initialization complete for UC1.")
        except mysql.connector.Error as err:
            logger.error(f"Schema generation failed: {err}")
            raise
        finally:
            cursor.close()
            self.base_conn.close()