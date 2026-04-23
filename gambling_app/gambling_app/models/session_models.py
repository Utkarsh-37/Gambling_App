from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime
from enum import Enum

class SessionStatus(Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ENDED = "ENDED"

class SessionEndReason(Enum):
    MANUAL = "MANUAL"
    WIN_LIMIT_REACHED = "WIN_LIMIT_REACHED"
    LOSS_LIMIT_REACHED = "LOSS_LIMIT_REACHED"
    MAX_GAMES_REACHED = "MAX_GAMES_REACHED"

@dataclass
class SessionParameters:
    lower_limit: Decimal
    upper_limit: Decimal
    min_bet: Decimal
    max_bet: Decimal
    session_id: Optional[int] = None
    parameter_id: Optional[int] = None

@dataclass
class GameSession:
    gambler_id: int
    starting_stake: Decimal
    status: str = SessionStatus.ACTIVE.value
    peak_stake: Decimal = Decimal('0.0')
    lowest_stake: Decimal = Decimal('0.0')
    games_played: int = 0
    total_pause_seconds: int = 0
    ending_stake: Optional[Decimal] = None
    end_reason: Optional[str] = None
    session_id: Optional[int] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    parameters: Optional[SessionParameters] = None

@dataclass
class PauseRecord:
    session_id: int
    pause_reason: str = "USER_REQUEST"
    pause_id: Optional[int] = None
    paused_at: Optional[datetime] = None
    resumed_at: Optional[datetime] = None
    pause_seconds: int = 0