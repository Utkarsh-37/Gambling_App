from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class OddsConfiguration:
    odds_type: str
    odds_config_id: Optional[int] = None
    fixed_multiplier: Optional[Decimal] = None
    american_odds: Optional[int] = None
    decimal_odds: Optional[Decimal] = None
    house_edge: Decimal = Decimal('0.0')

@dataclass
class RunningTotalsSnapshot:
    session_id: int
    game_id: int
    total_games: int = 0
    total_wins: int = 0
    total_losses: int = 0
    total_winnings: Decimal = Decimal('0.0')
    total_losses_amount: Decimal = Decimal('0.0')
    net_profit: Decimal = Decimal('0.0')
    win_rate: float = 0.0
    profit_factor: float = 0.0
    roi: float = 0.0
    longest_win_streak: int = 0
    longest_loss_streak: int = 0
    current_win_streak: int = 0
    current_loss_streak: int = 0
    snapshot_id: Optional[int] = None