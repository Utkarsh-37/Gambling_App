from services.gambler_profile_service import GamblerProfileService
from models.gambler_profile import Gambler, BettingPreferences, GamblerProfile
from utils.exceptions import ValidationException
from decimal import Decimal

class GamblerController:
    """Acts as the bridge between UI (Rich Console) and the Service Layer."""
    def __init__(self):
        self.service = GamblerProfileService()

    # Update the method signature in gambler_controller.py
    def register_new_gambler(self, username: str, email: str, stake: float, win_thresh: float, loss_thresh: float, min_bet: float = 5.0, max_bet: float = 1000.0):
        try:
            g = Gambler(
                username=username, full_name=username, email=email,
                initial_stake=Decimal(str(stake)), current_stake=Decimal(str(stake)),
                win_threshold=Decimal(str(win_thresh)), loss_threshold=Decimal(str(loss_thresh))
            )
            # Update this line to use the variables
            p = BettingPreferences(min_bet=Decimal(str(min_bet)), max_bet=Decimal(str(max_bet)))
            profile = GamblerProfile(gambler=g, preferences=p)
            
            created_profile = self.service.create_profile(profile)
            return {"status": "success", "data": created_profile}
        except ValidationException as ve:
            return {"status": "error", "message": f"Validation Error on {ve.field}: {ve}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def get_profile(self, gambler_id: int):
        try:
            profile = self.service.repo.get_gambler_profile_by_id(gambler_id)
            if not profile:
                return {"status": "error", "message": "Gambler not found."}
            return {"status": "success", "data": profile}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def update_preferences(self, gambler_id: int, min_bet: float, max_bet: float):
        try:
            profile = self.service.update_betting_limits(gambler_id, Decimal(str(min_bet)), Decimal(str(max_bet)))
            return {"status": "success", "data": profile}
        except Exception as e:
            return {"status": "error", "message": str(e)}