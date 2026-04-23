from config.database import get_connection
from models.gambler_profile import Gambler, BettingPreferences, GamblerProfile
from utils.exceptions import DatabaseOperationException
import logging

logger = logging.getLogger(__name__)

class GamblerRepository:
    def create_gambler_profile(self, profile: GamblerProfile) -> GamblerProfile:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            conn.start_transaction()
            
            # Insert Gambler
            gambler_sql = """
                INSERT INTO GAMBLERS (username, full_name, email, is_active, initial_stake, 
                                      current_stake, win_threshold, loss_threshold, min_required_stake, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            g = profile.gambler
            cursor.execute(gambler_sql, (g.username, g.full_name, g.email, g.is_active, 
                                         g.initial_stake, g.current_stake, g.win_threshold, 
                                         g.loss_threshold, g.min_required_stake))
            gambler_id = cursor.lastrowid
            profile.gambler.gambler_id = gambler_id

            # Insert Preferences
            pref_sql = """
                INSERT INTO BETTING_PREFERENCES (gambler_id, min_bet, max_bet, preferred_game_type, 
                                                 auto_play_enabled, auto_play_max_games, 
                                                 session_loss_limit, session_win_target)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            p = profile.preferences
            cursor.execute(pref_sql, (gambler_id, p.min_bet, p.max_bet, p.preferred_game_type,
                                      p.auto_play_enabled, p.auto_play_max_games, 
                                      p.session_loss_limit, p.session_win_target))
            profile.preferences.preference_id = cursor.lastrowid
            profile.preferences.gambler_id = gambler_id

            conn.commit()
            return profile
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create gambler profile: {e}")
            raise DatabaseOperationException(f"DB Error: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def get_gambler_profile_by_id(self, gambler_id: int) -> GamblerProfile:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM GAMBLERS WHERE gambler_id = %s", (gambler_id,))
            g_row = cursor.fetchone()
            if not g_row:
                return None

            cursor.execute("SELECT * FROM BETTING_PREFERENCES WHERE gambler_id = %s", (gambler_id,))
            p_row = cursor.fetchone()

            gambler = Gambler(**{k: v for k, v in g_row.items() if k in Gambler.__annotations__})
            prefs = BettingPreferences(**{k: v for k, v in p_row.items() if k in BettingPreferences.__annotations__})
            return GamblerProfile(gambler, prefs)
        finally:
            cursor.close()
            conn.close()

    def update_gambler(self, gambler: Gambler):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = """
                UPDATE GAMBLERS 
                SET current_stake = %s, win_threshold = %s, loss_threshold = %s, 
                    is_active = %s, updated_at = NOW()
                WHERE gambler_id = %s
            """
            cursor.execute(sql, (gambler.current_stake, gambler.win_threshold, 
                                 gambler.loss_threshold, gambler.is_active, gambler.gambler_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()