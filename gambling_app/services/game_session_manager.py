from models.session_models import GameSession, SessionParameters, SessionStatus, SessionEndReason
from repositories.session_repository import SessionRepository
from services.gambler_profile_service import GamblerProfileService
from utils.exceptions import ValidationException
from utils.decorators import service_logger
from datetime import datetime

class GameSessionManager:
    def __init__(self):
        self.repo = SessionRepository()
        self.profile_service = GamblerProfileService()

    @service_logger
    def start_session(self, gambler_id: int) -> GameSession:
        active = self.repo.get_active_session(gambler_id)
        if active:
            raise ValidationException(f"Gambler already has a session in {active.status} state.")
            
        profile = self.profile_service.repo.get_gambler_profile_by_id(gambler_id)
        if not self.profile_service.validate_eligibility(gambler_id):
            raise ValidationException("Gambler is not eligible to start a session.")
            
        g = profile.gambler
        p = profile.preferences
        
        params = SessionParameters(
            lower_limit=g.loss_threshold,
            upper_limit=g.win_threshold,
            min_bet=p.min_bet,
            max_bet=p.max_bet
        )
        
        session = GameSession(
            gambler_id=gambler_id,
            starting_stake=g.current_stake,
            peak_stake=g.current_stake,
            lowest_stake=g.current_stake,
            parameters=params
        )
        
        return self.repo.create_session(session)

    @service_logger
    def pause_session(self, gambler_id: int, reason: str = "Manual"):
        session = self.repo.get_active_session(gambler_id)
        if not session or session.status != SessionStatus.ACTIVE.value:
            raise ValidationException("No active session to pause.")
            
        session.status = SessionStatus.PAUSED.value
        self.repo.update_session(session)
        self.repo.insert_pause(session.session_id, reason)
        return session

    @service_logger
    def resume_session(self, gambler_id: int):
        session = self.repo.get_active_session(gambler_id)
        if not session or session.status != SessionStatus.PAUSED.value:
            raise ValidationException("No paused session to resume.")
            
        session.status = SessionStatus.ACTIVE.value
        self.repo.resolve_pause(session.session_id)
        self.repo.update_session(session)
        return session

    @service_logger
    def end_session(self, gambler_id: int, reason: SessionEndReason = SessionEndReason.MANUAL) -> GameSession:
        session = self.repo.get_active_session(gambler_id)
        if not session:
            raise ValidationException("No active or paused session to end.")
            
        profile = self.profile_service.repo.get_gambler_profile_by_id(gambler_id)
        
        if session.status == SessionStatus.PAUSED.value:
            self.repo.resolve_pause(session.session_id)
            
        session.status = SessionStatus.ENDED.value
        session.end_reason = reason.value
        session.ending_stake = profile.gambler.current_stake
        session.ended_at = datetime.now()
        
        self.repo.update_session(session)
        return session