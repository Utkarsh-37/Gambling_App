from rich.console import Console
from rich.panel import Panel
from models.betting_models import GameRecord
from models.gambler_profile import GamblerProfile

console = Console()

class GameStatusDisplay:
    @staticmethod
    def display_current_status(profile: GamblerProfile):
        g = profile.gambler
        p = profile.preferences
        status_text = (
            f"[bold cyan]Username:[/bold cyan] {g.username}\n"
            f"[bold cyan]Current Stake:[/bold cyan] ₹{g.current_stake:.2f}\n"
            f"[dim]Limits - Win: ₹{g.win_threshold:.2f} | Loss: ₹{g.loss_threshold:.2f}[/dim]\n"
            f"[dim]Bet Range: ₹{p.min_bet:.2f} - ₹{p.max_bet:.2f}[/dim]"
        )
        console.print(Panel(status_text, title="Current Status", border_style="blue", expand=False))

    @staticmethod
    def display_game_outcome(game_rec: GameRecord):
        color = "green" if game_rec.outcome == "WIN" else "red"
        symbol = "+" if game_rec.outcome == "WIN" else ""
        console.print(f"\n[bold {color}]Outcome: {game_rec.outcome}![/bold {color}]")
        console.print(f"Net Change: {symbol}₹{game_rec.net_change:.2f}")
        console.print(f"New Balance: [bold]₹{game_rec.stake_after:.2f}[/bold]\n")