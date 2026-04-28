from services.betting_service import BettingService
from strategies.betting_strategies import (
    MartingaleStrategy, FixedAmountStrategy, 
    PercentageStrategy, ReverseMartingaleStrategy
)
from decimal import Decimal

class BettingController:
    def __init__(self):
        self.service = BettingService()
        # The dictionary that links the text code to the actual logic!
        self.strategies = {
            "FIXED": FixedAmountStrategy(),
            "PERCENTAGE": PercentageStrategy(),
            "MARTINGALE": MartingaleStrategy(),
            "REVERSE_MARTINGALE": ReverseMartingaleStrategy()
        }

    def play_single_game(self, gambler_id: int, amount: float, probability: float = 0.45):
        try:
            res = self.service.place_and_settle_bet(gambler_id, Decimal(str(amount)), probability, strategy_id=1)
            return {"status": "success", "data": res}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def play_auto_strategy(self, gambler_id: int, base_amount: float, rounds: int, strategy_code: str):
        """Executes multiple bets automatically using a strategy."""
        results = []
        strategy = self.strategies.get(strategy_code, FixedAmountStrategy())
        
        profile = self.service.profile_service.repo.get_gambler_profile_by_id(gambler_id)
        if not profile:
            return {"status": "error", "message": "Gambler not found."}
            
        current_stake = profile.gambler.current_stake
        
        # Calculate Round 1 Bet
        if strategy_code == "PERCENTAGE":
            current_bet = current_stake * (Decimal(str(base_amount)) / Decimal("100.0"))
        else:
            current_bet = Decimal(str(base_amount))

        prev_outcome = None

        for i in range(rounds):
            try:
                res = self.service.place_and_settle_bet(gambler_id, current_bet, win_probability=0.45)
                results.append(res)
                
                game_rec = res["game"]
                prev_outcome = game_rec.outcome
                current_stake = game_rec.stake_after
                
                # Stop if boundaries hit (Win/Loss limits)
                if res["boundary"].is_breached:
                    break

                # Calculate next bet based on strategy
                current_bet = strategy.calculate_next_bet(
                    current_stake=current_stake, 
                    base_bet=Decimal(str(base_amount)), 
                    previous_bet=current_bet, 
                    previous_outcome=prev_outcome
                )

                # Cap bet to current stake to prevent immediate exception
                if current_bet > current_stake:
                    current_bet = current_stake

            except Exception as e:
                results.append({"status": "error", "message": str(e), "round": i+1})
                break

        return {"status": "success", "rounds_played": len(results), "history": results}