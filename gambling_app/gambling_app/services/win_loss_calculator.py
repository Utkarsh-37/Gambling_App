import random
from decimal import Decimal, ROUND_HALF_UP
from models.win_loss_models import OddsConfiguration, RunningTotalsSnapshot
from models.betting_models import GameRecord
from config.database import get_connection

class WinLossCalculator:
    
    def calculate_potential_winnings(self, bet_amount: Decimal, win_prob: float, config: OddsConfiguration) -> Decimal:
        """Calculates exact payout based on different odds systems."""
        payout = Decimal('0.0')
        
        if config.odds_type == 'FIXED' and config.fixed_multiplier:
            payout = bet_amount * config.fixed_multiplier
            
        elif config.odds_type in ['AMERICAN_FAV', 'AMERICAN_DOG'] and config.american_odds:
            if config.american_odds > 0: # Underdog (+200 means bet 100 to win 200)
                profit = bet_amount * (Decimal(str(config.american_odds)) / Decimal('100.0'))
            else: # Favorite (-150 means bet 150 to win 100)
                profit = bet_amount * (Decimal('100.0') / Decimal(str(abs(config.american_odds))))
            payout = bet_amount + profit
            
        elif config.odds_type == 'DECIMAL' and config.decimal_odds:
            payout = bet_amount * config.decimal_odds
            
        elif config.odds_type == 'PROBABILITY_BASED':
            # E.g., 25% chance -> 4.0 multiplier. Minus 2% house edge -> 3.92
            true_mult = Decimal('1.0') / Decimal(str(win_prob))
            adjusted_mult = true_mult * (Decimal('1.0') - config.house_edge)
            payout = bet_amount * adjusted_mult

        # Standard casino rounding (nearest penny)
        return payout.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def determine_outcome(self, win_prob: float, house_edge: Decimal = Decimal('0.0')) -> str:
        """Determines WIN or LOSS factoring in the house edge against the true probability."""
        adjusted_prob = win_prob * float(Decimal('1.0') - house_edge)
        return "WIN" if random.random() < adjusted_prob else "LOSS"

    def generate_snapshot(self, session_id: int, game_rec: GameRecord, starting_stake: Decimal) -> RunningTotalsSnapshot:
        """Calculates deep statistics cumulatively."""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Get previous snapshot
            cursor.execute("""
                SELECT * FROM RUNNING_TOTALS_SNAPSHOTS 
                WHERE session_id = %s ORDER BY snapshot_id DESC LIMIT 1
            """, (session_id,))
            prev = cursor.fetchone()

            snap = RunningTotalsSnapshot(session_id=session_id, game_id=game_rec.game_id)
            is_win = game_rec.outcome == "WIN"
            
            if prev:
                # Inherit previous stats
                snap.total_games = prev['total_games'] + 1
                snap.total_wins = prev['total_wins'] + (1 if is_win else 0)
                snap.total_losses = prev['total_losses'] + (1 if not is_win else 0)
                snap.total_winnings = Decimal(str(prev['total_winnings'])) + game_rec.payout_amount
                snap.total_losses_amount = Decimal(str(prev['total_losses_amount'])) + game_rec.loss_amount
                
                # Streaks
                snap.current_win_streak = prev['current_win_streak'] + 1 if is_win else 0
                snap.current_loss_streak = prev['current_loss_streak'] + 1 if not is_win else 0
                snap.longest_win_streak = max(prev['longest_win_streak'], snap.current_win_streak)
                snap.longest_loss_streak = max(prev['longest_loss_streak'], snap.current_loss_streak)
            else:
                # First game
                snap.total_games = 1
                snap.total_wins = 1 if is_win else 0
                snap.total_losses = 1 if not is_win else 0
                snap.total_winnings = game_rec.payout_amount
                snap.total_losses_amount = game_rec.loss_amount
                snap.current_win_streak = 1 if is_win else 0
                snap.current_loss_streak = 1 if not is_win else 0
                snap.longest_win_streak = snap.current_win_streak
                snap.longest_loss_streak = snap.current_loss_streak

            # Advanced Math
            snap.net_profit = snap.total_winnings - snap.total_losses_amount
            snap.win_rate = float(snap.total_wins) / snap.total_games
            
            # Profit Factor = Gross Win / Gross Loss. Handle Div by Zero.
            if snap.total_losses_amount > 0:
                snap.profit_factor = float(snap.total_winnings / snap.total_losses_amount)
            else:
                snap.profit_factor = float(snap.total_winnings) # Infinity essentially
                
            # ROI = Net Profit / Starting Session Stake
            snap.roi = float(snap.net_profit / starting_stake)

            # Save Snapshot
            sql = """
                INSERT INTO RUNNING_TOTALS_SNAPSHOTS 
                (session_id, game_id, total_games, total_wins, total_losses, total_winnings, total_losses_amount,
                net_profit, win_rate, profit_factor, roi, longest_win_streak, longest_loss_streak, 
                current_win_streak, current_loss_streak)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                snap.session_id, snap.game_id, snap.total_games, snap.total_wins, snap.total_losses,
                snap.total_winnings, snap.total_losses_amount, snap.net_profit, snap.win_rate,
                snap.profit_factor, snap.roi, snap.longest_win_streak, snap.longest_loss_streak,
                snap.current_win_streak, snap.current_loss_streak
            ))
            conn.commit()
            return snap
        finally:
            cursor.close()
            conn.close()