from services.game_session_manager import GameSessionManager
from models.session_models import SessionEndReason

class SessionController:
    def __init__(self):
        self.manager = GameSessionManager()

    def start_session(self, gambler_id: int):
        try:
            s = self.manager.start_session(gambler_id)
            return {"status": "success", "data": s}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def manage_pause_resume(self, gambler_id: int, action: str):
        try:
            if action == "PAUSE":
                s = self.manager.pause_session(gambler_id)
            else:
                s = self.manager.resume_session(gambler_id)
            return {"status": "success", "data": s}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def end_session(self, gambler_id: int):
        try:
            s = self.manager.end_session(gambler_id, SessionEndReason.MANUAL)
            return {"status": "success", "data": s}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_session_info(self, session_id: int):
        conn = self.manager.repo.get_active_session.__globals__['get_connection']()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM SESSIONS WHERE session_id = %s", (session_id,))
            row = cursor.fetchone()
            if not row:
                return {"status": "error", "message": "Session not found."}
            return {"status": "success", "data": row}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()