import mysql.connector
from mysql.connector import pooling
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

db_pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="gambling_pool",
    pool_size=5,
    pool_reset_session=True,
    host=settings.DB_HOST,
    port=settings.DB_PORT,
    database=settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD
)

def get_connection():
    try:
        return db_pool.get_connection()
    except mysql.connector.Error as err:
        logger.error(f"Database connection failed: {err}")
        raise