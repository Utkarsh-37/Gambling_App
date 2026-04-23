from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from ui.safe_input_handler import SafeInputHandler
from ui.game_status_display import GameStatusDisplay
from ui.session_summary import SessionSummary

# Import Controllers
from controllers.gambler_controller import GamblerController
from controllers.stake_controller import StakeController
from controllers.betting_controller import BettingController
from controllers.session_controller import SessionController
from controllers.win_loss_controller import WinLossController

console = Console()

class InteractiveMenu:
    def __init__(self):
        self.input_handler = SafeInputHandler()
        self.gambler_ctrl = GamblerController()
        self.stake_ctrl = StakeController()
        self.betting_ctrl = BettingController()
        self.session_ctrl = SessionController()
        self.win_loss_ctrl = WinLossController()

    def display_main_menu(self):
        console.print(Panel.fit("[bold cyan]Gambling App - Main Menu[/bold cyan]", border_style="cyan"))
        console.print("[dim]-- Gambler Profile --[/dim]")
        console.print("1. Create Profile  | 2. View Status  | 3. Reset Limits")
        console.print("[dim]-- Banking --[/dim]")
        console.print("4. Deposit Funds   | 5. Stake History")
        console.print("[dim]-- Game Session --[/dim]")
        console.print("6. Start Session   | 7. Pause/Resume | 8. End Session")
        console.print("9. View Past Session Summary")
        console.print("[dim]-- Betting Room --[/dim]")
        console.print("10. Manual Bet     | 11. Auto-Play (Strategy)")
        console.print("[dim]----------------------------[/dim]")
        console.print("12. Exit")
        return Prompt.ask("Select an option", choices=[str(i) for i in range(1, 13)])

    def run(self):
        while True:
            choice = self.display_main_menu()

            try:
                if choice == "1":
                    console.print("\n[bold yellow]--- Create Gambler ---[/bold yellow]")
                    username = Prompt.ask("Username")
                    email = Prompt.ask("Email")
                    stake = self.input_handler.ask_float("Initial Stake ($)", "initial_stake")
                    w_thresh = self.input_handler.ask_float("Win Threshold ($)", "win_threshold")
                    l_thresh = self.input_handler.ask_float("Loss Threshold ($)", "loss_threshold")
                    
                    res = self.gambler_ctrl.register_new_gambler(username, email, stake, w_thresh, l_thresh)
                    if res["status"] == "success":
                        console.print(f"[bold green]✔ Profile Created! ID: {res['data'].gambler.gambler_id}[/bold green]\n")
                    else:
                        console.print(f"[bold red]✖ Error:[/bold red] {res['message']}\n")

                elif choice == "2":
                    console.print("\n[bold yellow]--- View Status ---[/bold yellow]")
                    gid = int(self.input_handler.ask_float("Enter Gambler ID", "gambler_id"))
                    res = self.gambler_ctrl.get_profile(gid)
                    if res["status"] == "success":
                        GameStatusDisplay.display_current_status(res["data"])
                    else:
                        console.print(f"[bold red]✖ Error:[/bold red] {res['message']}\n")

                elif choice == "3":
                    console.print("\n[bold yellow]--- Reset Limits ---[/bold yellow]")
                    gid = int(self.input_handler.ask_float("Enter Gambler ID", "gambler_id"))
                    try:
                        res = self.gambler_ctrl.service.reset_profile_for_new_session(gid)
                        console.print("[bold green]✔ Profile Limits Reset![/bold green]")
                        GameStatusDisplay.display_current_status(res)
                    except Exception as e:
                        console.print(f"[bold red]✖ Error:[/bold red] {str(e)}\n")

                elif choice == "4":
                    console.print("\n[bold yellow]--- Deposit Funds ---[/bold yellow]")
                    gid = int(self.input_handler.ask_float("Enter Gambler ID", "gambler_id"))
                    amount = self.input_handler.ask_float("Amount to Deposit ($)", "amount")
                    res = self.stake_ctrl.process_deposit(gid, amount)
                    if res["status"] == "success":
                        console.print(f"[bold green]✔ Deposited ${amount}. New Balance: ${res['transaction'].balance_after}[/bold green]\n")
                    else:
                        console.print(f"[bold red]✖ Error:[/bold red] {res['message']}\n")

                elif choice == "5":
                    console.print("\n[bold yellow]--- Stake History ---[/bold yellow]")
                    gid = int(self.input_handler.ask_float("Enter Gambler ID", "gambler_id"))
                    res = self.stake_ctrl.get_history_report(gid)
                    if res["status"] == "success":
                        r = res["report"]
                        console.print(f"[bold cyan]Net Profit/Loss:[/bold cyan] ${r.net_profit_loss}")
                        console.print(f"[bold cyan]Total Transactions:[/bold cyan] {r.total_transactions}\n")
                    else:
                        console.print(f"[bold red]✖ Error:[/bold red] {res['message']}\n")

                elif choice == "6":
                    console.print("\n[bold yellow]--- Start Session ---[/bold yellow]")
                    gid = int(self.input_handler.ask_float("Enter Gambler ID", "gambler_id"))
                    res = self.session_ctrl.start_session(gid)
                    if res["status"] == "success":
                        console.print(f"[bold green]✔ Session {res['data'].session_id} Started! Good luck![/bold green]\n")
                    else:
                        console.print(f"[bold red]✖ Error:[/bold red] {res['message']}\n")

                elif choice == "7":
                    console.print("\n[bold yellow]--- Pause/Resume Session ---[/bold yellow]")
                    gid = int(self.input_handler.ask_float("Enter Gambler ID", "gambler_id"))
                    action = Prompt.ask("Action", choices=["PAUSE", "RESUME"])
                    res = self.session_ctrl.manage_pause_resume(gid, action)
                    if res["status"] == "success":
                        console.print(f"[bold green]✔ Session is now {res['data'].status}[/bold green]\n")
                    else:
                        console.print(f"[bold red]✖ Error:[/bold red] {res['message']}\n")

                elif choice == "8":
                    console.print("\n[bold yellow]--- End Session ---[/bold yellow]")
                    gid = int(self.input_handler.ask_float("Enter Gambler ID", "gambler_id"))
                    
                    end_res = self.session_ctrl.end_session(gid)
                    if end_res["status"] == "success":
                        s_data = self.session_ctrl.get_session_info(end_res["data"].session_id)["data"]
                        stats_res = self.win_loss_ctrl.get_latest_statistics(s_data['session_id'])
                        advanced_stats = stats_res["data"] if stats_res["status"] == "success" else None
                        
                        SessionSummary.display_session_summary(s_data, advanced_stats)
                    else:
                        console.print(f"[bold red]✖ Error:[/bold red] {end_res['message']}\n")

                # --- NEW OPTION ADDED HERE ---
                elif choice == "9":
                    console.print("\n[bold yellow]--- View Past Session Summary ---[/bold yellow]")
                    sid = int(self.input_handler.ask_float("Enter Session ID", "session_id"))
                    
                    s_res = self.session_ctrl.get_session_info(sid)
                    if s_res["status"] == "success":
                        s_data = s_res["data"]
                        stats_res = self.win_loss_ctrl.get_latest_statistics(sid)
                        advanced_stats = stats_res["data"] if stats_res["status"] == "success" else None
                        
                        SessionSummary.display_session_summary(s_data, advanced_stats)
                    else:
                        console.print(f"[bold red]✖ Error:[/bold red] {s_res['message']}\n")

                elif choice == "10":
                    console.print("\n[bold yellow]--- Place Manual Bet ---[/bold yellow]")
                    gid = int(self.input_handler.ask_float("Enter Gambler ID", "gambler_id"))
                    amount = self.input_handler.ask_float("Bet Amount ($)", "bet_amount")
                    
                    with console.status("Rolling..."):
                        res = self.betting_ctrl.play_single_game(gid, amount)
                        
                    if res["status"] == "success":
                        GameStatusDisplay.display_game_outcome(res["data"]["game"])
                    else:
                        console.print(f"[bold red]✖ Error:[/bold red] {res['message']}\n")
                
                elif choice == "11":
                    console.print("\n[bold yellow]--- Auto-Play Strategy ---[/bold yellow]")
                    gid = int(self.input_handler.ask_float("Enter Gambler ID", "gambler_id"))
                    strategy_choices = ["FIXED", "PERCENTAGE", "MARTINGALE", "REVERSE_MARTINGALE"]
                    strategy_code = Prompt.ask("Select Strategy", choices=strategy_choices, default="MARTINGALE")
                    
                    if strategy_code == "PERCENTAGE":
                        base = self.input_handler.ask_float("Bet Percentage of Stake (%)", "base_bet")
                    else:
                        base = self.input_handler.ask_float("Base Bet Amount ($)", "base_bet")
                        
                    rounds = int(self.input_handler.ask_float("Max Rounds to Play", "rounds"))
                    
                    with console.status(f"Playing {strategy_code}..."):
                        res = self.betting_ctrl.play_auto_strategy(gid, base, rounds, strategy_code)
                        
                    if res["status"] == "success":
                        console.print(f"[bold green]✔ Auto-Play Complete. Played {res['rounds_played']} rounds.[/bold green]\n")
                    else:
                        console.print(f"[bold red]✖ Error:[/bold red] {res['message']}\n")

                elif choice == "12":
                    console.print("[bold cyan]Exiting Gambling Simulation. Goodbye![/bold cyan]")
                    break

            except Exception as e:
                console.print(f"[bold red]✖ System Error:[/bold red] {str(e)}\n")