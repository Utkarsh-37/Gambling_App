import random
from decimal import Decimal
from models.betting_models import Bet, GameRecord
from models.stake_models import TransactionType
from models.session_models import SessionEndReason, SessionStatus
from repositories.betting_repository import BettingRepository
from services.gambler_profile_service import GamblerProfileService
from services.stake_management_service import StakeManagementService
from services.game_session_manager import GameSessionManager
from utils.exceptions import ValidationException
from utils.decorators import service_logger

class BettingService:
    def __init__(self):
        self.repo = BettingRepository()
        self.profile_service = GamblerProfileService()
        self.stake_service = StakeManagementService()
        self.session_manager = GameSessionManager()

    @service_logger
    def place_and_settle_bet(self, gambler_id: int, amount: Decimal, win_probability: float, strategy_id: int = 1):
        # 1. Check Session State FIRST
        active_session = self.session_manager.repo.get_active_session(gambler_id)
        if active_session and active_session.status == SessionStatus.PAUSED.value:
            raise ValidationException("Session is paused. Please resume before placing bets.")

        # 2. Validation
        profile = self.profile_service.repo.get_gambler_profile_by_id(gambler_id)
        if not profile:
            raise ValidationException("Gambler not found.")
        
        stake = profile.gambler.current_stake
        prefs = profile.preferences

        if amount <= 0:
            raise ValidationException("Bet must be > 0.")
        if amount > stake:
            raise ValidationException("Insufficient stake for bet.", "bet_amount", amount)
        if amount < prefs.min_bet or amount > prefs.max_bet:
            raise ValidationException(f"Bet outside preferences limits (${prefs.min_bet:.2f} - ${prefs.max_bet:.2f}).")

        # 3. Record Bet Placement
        potential_win = amount * Decimal("2.0")
        bet = Bet(
            gambler_id=gambler_id, bet_amount=amount, win_probability=win_probability,
            stake_before=stake, potential_win=potential_win, strategy_id=strategy_id,
            session_id=active_session.session_id if active_session else None
        )
        bet = self.repo.create_bet(bet)

        # 4. Determine Outcome
        is_win = random.random() < win_probability
        outcome_str = "WIN" if is_win else "LOSS"

        # 5. Financial Transaction
        trans_type = TransactionType.BET_WIN if is_win else TransactionType.BET_LOSS
        tx_amount = amount 
        tx = self.stake_service.adjust_stake(gambler_id, trans_type, tx_amount)

        # 6. Record Game & Settle
        game_rec = GameRecord(
            bet_id=bet.bet_id, outcome=outcome_str, net_change=tx_amount if is_win else -tx_amount,
            stake_before=tx.balance_before, stake_after=tx.balance_after,
            payout_amount=amount * 2 if is_win else Decimal("0.0"),
            loss_amount=Decimal("0.0") if is_win else amount,
            session_id=active_session.session_id if active_session else None
        )
        self.repo.settle_bet_and_record_game(bet.bet_id, game_rec)

        # 7. Check Boundaries & UPDATE SESSION
        boundary = self.stake_service.check_boundaries(gambler_id)
        
        if active_session:
            # Update Session Counters
            active_session.games_played += 1
            if game_rec.stake_after > active_session.peak_stake:
                active_session.peak_stake = game_rec.stake_after
            if game_rec.stake_after < active_session.lowest_stake:
                active_session.lowest_stake = game_rec.stake_after
            
            self.session_manager.repo.update_session(active_session)

            # Auto-End Logic
            if boundary.is_breached:
                reason = SessionEndReason.WIN_LIMIT_REACHED if boundary.breach_type == "UPPER" else SessionEndReason.LOSS_LIMIT_REACHED
                self.session_manager.end_session(gambler_id, reason)

        return {"bet": bet, "game": game_rec, "boundary": boundary}