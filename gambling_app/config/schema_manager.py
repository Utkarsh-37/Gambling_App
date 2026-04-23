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

            self.base_conn.commit()
            logger.info("Schema initialization complete for UC1.")
        except mysql.connector.Error as err:
            logger.error(f"Schema generation failed: {err}")
            raise
        finally:
            cursor.close()
            self.base_conn.close()