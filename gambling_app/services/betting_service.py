import random
from decimal import Decimal
from models.betting_models import Bet, GameRecord
from models.stake_models import TransactionType
from repositories.betting_repository import BettingRepository
from services.gambler_profile_service import GamblerProfileService
from services.stake_management_service import StakeManagementService
from utils.exceptions import ValidationException
from utils.decorators import service_logger

class BettingService:
    def __init__(self):
        self.repo = BettingRepository()
        self.profile_service = GamblerProfileService()
        self.stake_service = StakeManagementService()

    @service_logger
    def place_and_settle_bet(self, gambler_id: int, amount: Decimal, win_probability: float, strategy_id: int = 1):
        # 1. Validation
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
            raise ValidationException(f"Bet outside preferences limits (${prefs.min_bet} - ${prefs.max_bet}).")

        # 2. Record Bet Placement
        potential_win = amount * Decimal("2.0") # Assuming 1:1 odds payout
        bet = Bet(
            gambler_id=gambler_id, bet_amount=amount, win_probability=win_probability,
            stake_before=stake, potential_win=potential_win, strategy_id=strategy_id
        )
        bet = self.repo.create_bet(bet)

        # 3. Determine Outcome (Random Probability)
        is_win = random.random() < win_probability
        outcome_str = "WIN" if is_win else "LOSS"

        # 4. Financial Transaction (Calls UC2)
        trans_type = TransactionType.BET_WIN if is_win else TransactionType.BET_LOSS
        tx_amount = amount if is_win else amount # In 1:1, you win your bet amount (net profit)
        
        tx = self.stake_service.adjust_stake(gambler_id, trans_type, tx_amount)

        # 5. Record Game & Settle Bet
        game_rec = GameRecord(
            bet_id=bet.bet_id,
            outcome=outcome_str,
            net_change=tx_amount if is_win else -tx_amount,
            stake_before=tx.balance_before,
            stake_after=tx.balance_after,
            payout_amount=amount * 2 if is_win else Decimal("0.0"),
            loss_amount=Decimal("0.0") if is_win else amount
        )
        self.repo.settle_bet_and_record_game(bet.bet_id, game_rec)

        # 6. Check Boundaries (Calls UC2)
        boundary = self.stake_service.check_boundaries(gambler_id)

        return {"bet": bet, "game": game_rec, "boundary": boundary}