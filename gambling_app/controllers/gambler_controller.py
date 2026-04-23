from services.gambler_profile_service import GamblerProfileService
from models.gambler_profile import Gambler, BettingPreferences, GamblerProfile
from utils.exceptions import ValidationException
from decimal import Decimal

class GamblerController:
    """Acts as the bridge between UI (Rich Console) and the Service Layer."""
    def __init__(self):
        self.service = GamblerProfileService()

    def register_new_gambler(self, username: str, email: str, stake: float, win_thresh: float, loss_thresh: float):
        try:
            g = Gambler(
                username=username, full_name=username, email=email,
                initial_stake=Decimal(str(stake)), current_stake=Decimal(str(stake)),
                win_threshold=Decimal(str(win_thresh)), loss_threshold=Decimal(str(loss_thresh))
            )
            p = BettingPreferences(min_bet=Decimal('5.0'), max_bet=Decimal('100.0'))
            profile = GamblerProfile(gambler=g, preferences=p)
            
            created_profile = self.service.create_profile(profile)
            return {"status": "success", "data": created_profile}
        except ValidationException as ve:
            return {"status": "error", "message": f"Validation Error on {ve.field}: {ve}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}