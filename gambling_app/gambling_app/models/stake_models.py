from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TransactionType(Enum):
    INITIAL_STAKE = "INITIAL_STAKE"
    BET_PLACED = "BET_PLACED"
    BET_WIN = "BET_WIN"
    BET_LOSS = "BET_LOSS"
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"
    ADJUSTMENT = "ADJUSTMENT"
    RESET = "RESET"

@dataclass
class StakeTransaction:
    gambler_id: int
    transaction_type: str
    amount: Decimal
    balance_before: Decimal
    balance_after: Decimal
    session_id: Optional[int] = None
    bet_id: Optional[int] = None
    game_id: Optional[int] = None
    transaction_ref: Optional[str] = None
    transaction_id: Optional[int] = None
    created_at: Optional[datetime] = None

@dataclass
class BoundaryStatus:
    is_breached: bool
    breach_type: Optional[str] = None # "UPPER" or "LOWER"
    warning_message: Optional[str] = None

@dataclass
class StakeHistoryReport:
    gambler_id: int
    starting_balance: Decimal
    current_balance: Decimal
    peak_balance: Decimal
    lowest_balance: Decimal
    total_transactions: int
    net_profit_loss: Decimal
    transactions: List[StakeTransaction] = field(default_factory=list)