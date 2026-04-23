from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime

@dataclass
class Bet:
    gambler_id: int
    bet_amount: Decimal
    win_probability: float
    stake_before: Decimal
    potential_win: Decimal
    odds_type: str = "FIXED"
    odds_value: Decimal = Decimal("2.0")
    strategy_id: Optional[int] = None
    session_id: Optional[int] = None
    game_index: int = 1
    stake_after: Optional[Decimal] = None
    is_settled: bool = False
    bet_id: Optional[int] = None

@dataclass
class GameRecord:
    bet_id: int
    outcome: str  # "WIN" or "LOSS"
    net_change: Decimal
    stake_before: Decimal
    stake_after: Decimal
    payout_amount: Decimal = Decimal("0.0")
    loss_amount: Decimal = Decimal("0.0")
    session_id: Optional[int] = None
    game_id: Optional[int] = None