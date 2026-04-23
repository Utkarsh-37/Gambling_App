from config.database import get_connection
import logging

logger = logging.getLogger(__name__)

class ValidationRepository:
    def log_event(self, error_type: str, severity: str, message: str, 
                  field_name: str = None, attempted_value: str = None, 
                  gambler_id: int = None, session_id: int = None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO VALIDATION_EVENTS 
                (session_id, gambler_id, error_type, severity, field_name, attempted_value, message)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (session_id, gambler_id, error_type, severity, 
                                 field_name, str(attempted_value)[:250] if attempted_value else None, message))
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to log validation event: {e}")
        finally:
            cursor.close()
            conn.close()