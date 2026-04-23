from models.stake_models import TransactionType, BoundaryStatus, StakeHistoryReport, StakeTransaction
from repositories.stake_repository import StakeRepository
from repositories.gambler_repository import GamblerRepository
from utils.exceptions import ValidationException
from utils.decorators import service_logger
from decimal import Decimal

class StakeManagementService:
    def __init__(self):
        self.repo = StakeRepository()
        self.gambler_repo = GamblerRepository()

    @service_logger
    def adjust_stake(self, gambler_id: int, trans_type: TransactionType, amount: Decimal) -> StakeTransaction:
        if amount <= 0:
            raise ValidationException("Transaction amount must be greater than 0.", "amount", amount)

        is_deduction = trans_type in [TransactionType.BET_PLACED, TransactionType.WITHDRAWAL, TransactionType.BET_LOSS]
        
        return self.repo.process_transaction(gambler_id, trans_type.value, amount, is_deduction)

    @service_logger
    def check_boundaries(self, gambler_id: int) -> BoundaryStatus:
        profile = self.gambler_repo.get_gambler_profile_by_id(gambler_id)
        if not profile:
            raise ValidationException("Gambler not found.", "gambler_id", gambler_id)
            
        g = profile.gambler
        stake = g.current_stake

        # Check Breaches
        if stake >= g.win_threshold:
            return BoundaryStatus(is_breached=True, breach_type="UPPER")
        if stake <= g.loss_threshold:
            return BoundaryStatus(is_breached=True, breach_type="LOWER")

        # Check Warnings (20% above loss limit, 80% of win limit)
        win_warning_line = g.initial_stake + (g.win_threshold - g.initial_stake) * Decimal('0.8')
        loss_warning_line = g.loss_threshold + (g.initial_stake - g.loss_threshold) * Decimal('0.2')

        if stake >= win_warning_line:
            return BoundaryStatus(is_breached=False, warning_message="Approaching Win Target!")
        if stake <= loss_warning_line:
            return BoundaryStatus(is_breached=False, warning_message="Approaching Loss Limit!")

        return BoundaryStatus(is_breached=False)

    @service_logger
    def generate_report(self, gambler_id: int) -> StakeHistoryReport:
        rows = self.repo.get_transactions_by_gambler(gambler_id)
        if not rows:
            raise ValidationException("No transactions found.", "gambler_id", gambler_id)

        txs = [StakeTransaction(**{k: v for k, v in r.items() if k in StakeTransaction.__annotations__}) for r in rows]
        
        starting_balance = txs[0].balance_before
        current_balance = txs[-1].balance_after
        peak = max([tx.balance_after for tx in txs] + [starting_balance])
        lowest = min([tx.balance_after for tx in txs] + [starting_balance])
        
        return StakeHistoryReport(
            gambler_id=gambler_id,
            starting_balance=starting_balance,
            current_balance=current_balance,
            peak_balance=peak,
            lowest_balance=lowest,
            total_transactions=len(txs),
            net_profit_loss=current_balance - starting_balance,
            transactions=txs
        )