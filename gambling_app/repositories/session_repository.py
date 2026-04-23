from config.database import get_connection
from models.session_models import GameSession, SessionParameters, PauseRecord
import logging

logger = logging.getLogger(__name__)

class SessionRepository:
    def create_session(self, session: GameSession) -> GameSession:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            conn.start_transaction()
            # Insert Session
            s_sql = """
                INSERT INTO SESSIONS (gambler_id, status, starting_stake, peak_stake, lowest_stake)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(s_sql, (session.gambler_id, session.status, session.starting_stake, 
                                   session.starting_stake, session.starting_stake))
            session.session_id = cursor.lastrowid
            
            # Insert Parameters
            p = session.parameters
            p_sql = """
                INSERT INTO SESSION_PARAMETERS (session_id, lower_limit, upper_limit, min_bet, max_bet)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(p_sql, (session.session_id, p.lower_limit, p.upper_limit, p.min_bet, p.max_bet))
            p.parameter_id = cursor.lastrowid
            
            conn.commit()
            return session
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def get_active_session(self, gambler_id: int) -> Optional[GameSession]:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM SESSIONS WHERE gambler_id = %s AND status IN ('ACTIVE', 'PAUSED')", (gambler_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return GameSession(**{k: v for k, v in row.items() if k in GameSession.__annotations__})
        finally:
            cursor.close()
            conn.close()

    def update_session(self, session: GameSession):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = """
                UPDATE SESSIONS SET status=%s, end_reason=%s, ending_stake=%s, peak_stake=%s, 
                lowest_stake=%s, games_played=%s, ended_at=%s 
                WHERE session_id=%s
            """
            cursor.execute(sql, (session.status, session.end_reason, session.ending_stake, 
                                 session.peak_stake, session.lowest_stake, session.games_played, 
                                 session.ended_at, session.session_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
            
    def insert_pause(self, session_id: int, reason: str):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO PAUSE_RECORDS (session_id, pause_reason) VALUES (%s, %s)", (session_id, reason))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def resolve_pause(self, session_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            # Find the unresumed pause and calculate seconds
            cursor.execute("""
                UPDATE PAUSE_RECORDS 
                SET resumed_at = NOW(), pause_seconds = TIMESTAMPDIFF(SECOND, paused_at, NOW()) 
                WHERE session_id = %s AND resumed_at IS NULL
            """, (session_id,))
            
            # Add to total session pause seconds
            cursor.execute("""
                UPDATE SESSIONS 
                SET total_pause_seconds = (SELECT SUM(pause_seconds) FROM PAUSE_RECORDS WHERE session_id = %s)
                WHERE session_id = %s
            """, (session_id, session_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()