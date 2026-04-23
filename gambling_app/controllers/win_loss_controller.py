from config.database import get_connection

class WinLossController:
    def get_latest_statistics(self, session_id: int):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            # Fetch the most recent snapshot for this session
            cursor.execute("""
                SELECT * FROM RUNNING_TOTALS_SNAPSHOTS 
                WHERE session_id = %s 
                ORDER BY snapshot_id DESC LIMIT 1
            """, (session_id,))
            snap = cursor.fetchone()
            
            if not snap:
                return {"status": "error", "message": "No statistics found. Have you played any games in this session yet?"}
            
            return {"status": "success", "data": snap}
        except Exception as e:
            return {"status": "error", "message": str(e)}
        finally:
            cursor.close()
            conn.close()