from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from datetime import datetime

@dataclass
class Gambler:
    username: str
    full_name: str
    email: str
    initial_stake: Decimal
    current_stake: Decimal
    win_threshold: Decimal
    loss_threshold: Decimal
    min_required_stake: Decimal = Decimal('0.0')
    is_active: bool = True
    gambler_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class BettingPreferences:
    min_bet: Decimal
    max_bet: Decimal
    preferred_game_type: str = "DEFAULT"
    auto_play_enabled: bool = False
    auto_play_max_games: int = 10
    session_loss_limit: Decimal = Decimal('0.0')
    session_win_target: Decimal = Decimal('0.0')
    gambler_id: Optional[int] = None
    preference_id: Optional[int] = None

@dataclass
class GamblerProfile:
    gambler: Gambler
    preferences: BettingPreferences