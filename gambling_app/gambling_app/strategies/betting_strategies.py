from abc import ABC, abstractmethod
from decimal import Decimal

class BettingStrategy(ABC):
    @abstractmethod
    def calculate_next_bet(self, current_stake: Decimal, base_bet: Decimal, 
                           previous_bet: Decimal = None, previous_outcome: str = None, 
                           streak_count: int = 0) -> Decimal:
        pass

class FixedAmountStrategy(BettingStrategy):
    def calculate_next_bet(self, current_stake: Decimal, base_bet: Decimal, **kwargs) -> Decimal:
        return base_bet

class PercentageStrategy(BettingStrategy):
    def calculate_next_bet(self, current_stake: Decimal, base_bet: Decimal, **kwargs) -> Decimal:
        # If base_bet is entered as 5 (for 5%), convert to 0.05
        percentage = base_bet / Decimal("100.0")
        return current_stake * percentage

class MartingaleStrategy(BettingStrategy):
    def calculate_next_bet(self, current_stake: Decimal, base_bet: Decimal, 
                           previous_bet: Decimal = None, previous_outcome: str = None, **kwargs) -> Decimal:
        if previous_outcome == "LOSS" and previous_bet:
            return previous_bet * Decimal("2.0")
        return base_bet # Reset on win or first play

class ReverseMartingaleStrategy(BettingStrategy):
    def calculate_next_bet(self, current_stake: Decimal, base_bet: Decimal, 
                           previous_bet: Decimal = None, previous_outcome: str = None, **kwargs) -> Decimal:
        if previous_outcome == "WIN" and previous_bet:
            return previous_bet * Decimal("2.0") # Double up on a winning streak
        return base_bet # Reset to base amount on a loss