from config.database import get_connection
from models.stake_models import StakeTransaction
from utils.exceptions import DatabaseOperationException
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class StakeRepository:
    def process_transaction(self, gambler_id: int, trans_type: str, amount: Decimal, is_deduction: bool) -> StakeTransaction:
        """Atomically updates balance and creates audit record."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            conn.start_transaction()
            
            # 1. Lock the row and get current balance
            cursor.execute("SELECT current_stake FROM GAMBLERS WHERE gambler_id = %s FOR UPDATE", (gambler_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError("Gambler not found.")
            
            balance_before = Decimal(str(row['current_stake']))
            
            # 2. Calculate new balance
            balance_after = balance_before - amount if is_deduction else balance_before + amount
            if balance_after < 0:
                raise ValueError("Insufficient funds.")

            # 3. Update Gambler Table
            cursor.execute("UPDATE GAMBLERS SET current_stake = %s WHERE gambler_id = %s", (balance_after, gambler_id))

            # 4. Insert Audit Trail
            sql = """
                INSERT INTO STAKE_TRANSACTIONS 
                (gambler_id, transaction_type, amount, balance_before, balance_after)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (gambler_id, trans_type, amount, balance_before, balance_after))
            transaction_id = cursor.lastrowid
            
            conn.commit()
            
            return StakeTransaction(
                gambler_id=gambler_id, transaction_type=trans_type, amount=amount,
                balance_before=balance_before, balance_after=balance_after, transaction_id=transaction_id
            )
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction failed: {e}")
            raise DatabaseOperationException(f"Transaction Error: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    def get_transactions_by_gambler(self, gambler_id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM STAKE_TRANSACTIONS WHERE gambler_id = %s ORDER BY created_at ASC", (gambler_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()