from models.gambler_profile import GamblerProfile
from repositories.gambler_repository import GamblerRepository
from utils.exceptions import ValidationException
from utils.decorators import service_logger
from config.settings import settings
from decimal import Decimal

class GamblerProfileService:
    def __init__(self):
        self.repo = GamblerRepository()

    @service_logger
    def create_profile(self, profile: GamblerProfile) -> GamblerProfile:
        # Validate Initial Stake
        if profile.gambler.initial_stake < settings.MIN_INITIAL_STAKE:
            raise ValidationException("Initial stake below minimum required.", "initial_stake", profile.gambler.initial_stake)
        
        # Validate Thresholds
        if profile.gambler.win_threshold <= profile.gambler.initial_stake:
            raise ValidationException("Win threshold must be > initial stake.", "win_threshold", profile.gambler.win_threshold)
        if profile.gambler.loss_threshold >= profile.gambler.initial_stake:
            raise ValidationException("Loss threshold must be < initial stake.", "loss_threshold", profile.gambler.loss_threshold)
        
        # Validate Betting Preferences
        if profile.preferences.max_bet < profile.preferences.min_bet:
            raise ValidationException("Max bet cannot be less than min bet.", "max_bet", profile.preferences.max_bet)

        # Set initial current_stake
        profile.gambler.current_stake = profile.gambler.initial_stake
        
        return self.repo.create_gambler_profile(profile)

    @service_logger
    def validate_eligibility(self, gambler_id: int) -> bool:
        profile = self.repo.get_gambler_profile_by_id(gambler_id)
        if not profile:
            raise ValidationException("Gambler not found.", "gambler_id", gambler_id)
        
        g = profile.gambler
        if not g.is_active:
            return False
        if g.current_stake <= g.min_required_stake:
            return False
        if g.current_stake >= g.win_threshold or g.current_stake <= g.loss_threshold:
            return False
            
        return True

    @service_logger
    def reset_profile_for_new_session(self, gambler_id: int) -> GamblerProfile:
        profile = self.repo.get_gambler_profile_by_id(gambler_id)
        if not profile:
            raise ValidationException("Gambler not found.", "gambler_id", gambler_id)

        g = profile.gambler
        # Proportional Threshold Calculation based on original ratios
        win_ratio = g.win_threshold / g.initial_stake
        loss_ratio = g.loss_threshold / g.initial_stake

        g.initial_stake = g.current_stake  # Reset baseline
        g.win_threshold = g.initial_stake * win_ratio
        g.loss_threshold = g.initial_stake * loss_ratio
        
        self.repo.update_gambler(g)
        return self.repo.get_gambler_profile_by_id(gambler_id)
    
    @service_logger
    def update_betting_limits(self, gambler_id: int, min_bet: Decimal, max_bet: Decimal):
        if max_bet < min_bet:
            raise ValidationException("Max bet cannot be less than min bet.", "max_bet", max_bet)
            
        profile = self.repo.get_gambler_profile_by_id(gambler_id)
        if not profile:
            raise ValidationException("Gambler not found.", "gambler_id", gambler_id)
            
        profile.preferences.min_bet = min_bet
        profile.preferences.max_bet = max_bet
        self.repo.update_preferences(profile.preferences)
        return profile