from config.database import get_connection
from models.betting_models import Bet, GameRecord
from utils.exceptions import DatabaseOperationException
import logging

logger = logging.getLogger(__name__)

class BettingRepository:
    def create_bet(self, bet: Bet) -> Bet:
        conn = get_connection()
        cursor = conn.cursor()
        try:
            sql = """
                INSERT INTO BETS (gambler_id, bet_amount, win_probability, potential_win, stake_before, strategy_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (bet.gambler_id, bet.bet_amount, bet.win_probability, 
                                 bet.potential_win, bet.stake_before, bet.strategy_id))
            bet.bet_id = cursor.lastrowid
            conn.commit()
            return bet
        except Exception as e:
            conn.rollback()
            raise DatabaseOperationException(f"Failed to create bet: {e}")
        finally:
            cursor.close()
            conn.close()

    def settle_bet_and_record_game(self, bet_id: int, game_rec: GameRecord):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            conn.start_transaction()
            # Mark bet settled
            cursor.execute("UPDATE BETS SET is_settled = TRUE, stake_after = %s WHERE bet_id = %s", 
                           (game_rec.stake_after, bet_id))
            
            # Insert Game Record
            sql = """
                INSERT INTO GAME_RECORDS (bet_id, outcome, payout_amount, loss_amount, net_change, stake_before, stake_after)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (bet_id, game_rec.outcome, game_rec.payout_amount, game_rec.loss_amount, 
                                 game_rec.net_change, game_rec.stake_before, game_rec.stake_after))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise DatabaseOperationException(f"Failed to settle bet: {e}")
        finally:
            cursor.close()
            conn.close()