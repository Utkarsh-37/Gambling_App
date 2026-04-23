import os
import logging
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = os.getenv("APP_NAME", "GamblingApp")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_NAME = os.getenv("DB_NAME", "gambling_db")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    MIN_INITIAL_STAKE = float(os.getenv("MIN_INITIAL_STAKE", 10.0))
    VALIDATION_STRICT_MODE = os.getenv("VALIDATION_STRICT_MODE", "true").lower() == "true"

settings = Settings()

# Setup basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)