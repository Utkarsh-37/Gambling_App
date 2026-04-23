from services.stake_management_service import StakeManagementService
from models.stake_models import TransactionType
from utils.exceptions import ValidationException
from decimal import Decimal

class StakeController:
    def __init__(self):
        self.service = StakeManagementService()

    def process_deposit(self, gambler_id: int, amount: float):
        try:
            tx = self.service.adjust_stake(gambler_id, TransactionType.DEPOSIT, Decimal(str(amount)))
            boundary = self.service.check_boundaries(gambler_id)
            return {"status": "success", "transaction": tx, "boundary": boundary}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_history_report(self, gambler_id: int):
        try:
            report = self.service.generate_report(gambler_id)
            return {"status": "success", "report": report}
        except Exception as e:
            return {"status": "error", "message": str(e)}