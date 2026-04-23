import sys
from rich.console import Console
from rich.prompt import Prompt, FloatPrompt
from rich.panel import Panel
from rich.table import Table

from config.schema_manager import SchemaManager
from controllers.gambler_controller import GamblerController
from controllers.stake_controller import StakeController  # Added for UC2
from controllers.betting_controller import BettingController
from controllers.session_controller import SessionController
from controllers.win_loss_controller import WinLossController

console = Console()

def setup_infrastructure():
    """Run startup checks and schema generation."""
    with console.status("[bold green]Initializing Database Schema...") as status:
        schema_manager = SchemaManager()
        schema_manager.initialize_schema()
    console.print("[bold green]✔ Database Ready![/bold green]\n")

def display_menu():
    console.print(Panel.fit("[bold cyan]Gambling App - Main Menu[/bold cyan]", border_style="cyan"))
    console.print("[dim]-- UC1: Gambler Profile --[/dim]")
    console.print("1. Create New Gambler Profile")
    console.print("  1a. View Gambler Profile")
    console.print("  1b. Edit Betting Preferences")
    console.print("2. Check Profile Eligibility (By ID)")
    console.print("3. Reset Profile for New Session (By ID)")
    console.print("[dim]-- UC2: Stake Management --[/dim]")
    console.print("4. Deposit Funds (By ID)")
    console.print("5. View Stake History Report (By ID)")
    console.print("[dim]-- UC3: Betting Mechanism --[/dim]")
    console.print("6. Place Manual Bet")
    console.print("7. Auto-Play (Choose Strategy)")
    console.print("[dim]----------------------------[/dim]")
    console.print("[dim]-- UC4: Game Session --[/dim]")
    console.print("8. Start Game Session")
    console.print("9. Pause/Resume Session")
    console.print("10. End Session")
    console.print("  10a. View Session Summary(Basic)")
    console.print("11. View Advanced Session Stats (UC5)")
    console.print("12. Exit")
    return Prompt.ask("Select an option", choices=["1", "1a", "1b", "2", "3", "4", "5", "6", "7", "8", "9", "10", "10a", "11", "12"])

def main():
    # 1. Boot up DB
    try:
        setup_infrastructure()
    except Exception as e:
        console.print(f"[bold red]Failed to start application: {e}[/bold red]")
        sys.exit(1)

    # Instantiate Controllers
    gambler_controller = GamblerController()
    stake_controller = StakeController()
    betting_controller = BettingController()  
    session_controller = SessionController()
    win_loss_controller = WinLossController()

    # 2. Main Event Loop
    while True:
        choice = display_menu()

        if choice == "1":
            console.print("\n[bold yellow]--- Create Gambler ---[/bold yellow]")
            username = Prompt.ask("Username")
            email = Prompt.ask("Email")
            stake = FloatPrompt.ask("Initial Stake ($)")
            win_thresh = FloatPrompt.ask("Win Threshold ($) [Must be > Stake]")
            loss_thresh = FloatPrompt.ask("Loss Threshold ($) [Must be < Stake]")
            min_bet = FloatPrompt.ask("Minimum Bet Limit ($)", default=5.0)
            max_bet = FloatPrompt.ask("Maximum Bet Limit ($)", default=5000.0)

            with console.status("Creating profile..."):
                result = gambler_controller.register_new_gambler(
                    username=username, email=email, 
                    stake=stake, win_thresh=win_thresh, loss_thresh=loss_thresh,
                    min_bet=min_bet, max_bet=max_bet
                )
            
            if result["status"] == "success":
                profile = result["data"]
                console.print(f"\n[bold green]✔ Profile Created Successfully! Gambler ID: {profile.gambler.gambler_id}[/bold green]\n")                    
            else:
                console.print(f"\n[bold red]✖ Error:[/bold red] {result['message']}\n")

        elif choice == "1a":
            console.print("\n[bold yellow]--- View Profile ---[/bold yellow]")
            gid = Prompt.ask("Enter Gambler ID")
            res = gambler_controller.get_profile(int(gid))
            
            if res["status"] == "success":
                p = res["data"]
                
                table = Table(title=f"Profile: {p.gambler.username}")
                table.add_column("Category", style="cyan")
                table.add_column("Detail", style="magenta")
                table.add_row("Status", "Active" if p.gambler.is_active else "Inactive")
                table.add_row("Current Stake", f"${p.gambler.current_stake}")
                table.add_row("Win/Loss Thresholds", f"Win: ${p.gambler.win_threshold} | Loss: ${p.gambler.loss_threshold}")
                table.add_row("Betting Limits", f"Min: ${p.preferences.min_bet} | Max: ${p.preferences.max_bet}")
                console.print(table)
            else:
                console.print(f"[bold red]✖ Error:[/bold red] {res['message']}")

        elif choice == "1b":
            console.print("\n[bold yellow]--- Edit Preferences ---[/bold yellow]")
            gid = Prompt.ask("Enter Gambler ID")
            min_bet = FloatPrompt.ask("New Min Bet ($)")
            max_bet = FloatPrompt.ask("New Max Bet ($)")
            
            with console.status("Updating..."):
                res = gambler_controller.update_preferences(int(gid), min_bet, max_bet)
                
            if res["status"] == "success":
                console.print("[bold green]✔ Preferences Updated![/bold green]")
            else:
                console.print(f"[bold red]✖ Error:[/bold red] {res['message']}")

        elif choice == "2":
            gid = Prompt.ask("Enter Gambler ID")
            try:
                is_eligible = gambler_controller.service.validate_eligibility(int(gid))
                if is_eligible:
                    console.print(f"[bold green]✔ Gambler {gid} is eligible to play.[/bold green]\n")
                else:
                    console.print(f"[bold yellow]⚠ Gambler {gid} is NOT eligible (Limits reached or inactive).[/bold yellow]\n")
            except Exception as e:
                 console.print(f"[bold red]✖ Error:[/bold red] {str(e)}\n")

        elif choice == "3":
            gid = Prompt.ask("Enter Gambler ID to reset")
            try:
                with console.status("Resetting profile..."):
                    reset_profile = gambler_controller.service.reset_profile_for_new_session(int(gid))
                g = reset_profile.gambler
                console.print(f"\n[bold green]✔ Profile Reset Complete![/bold green]")
                
                table = Table(title="New Session Limits")
                table.add_column("Property", style="cyan")
                table.add_column("Value", style="magenta")
                table.add_row("New Baseline Stake", f"${g.initial_stake}")
                table.add_row("New Win Threshold", f"${g.win_threshold}")
                table.add_row("New Loss Threshold", f"${g.loss_threshold}")
                console.print(table)
                console.print()
                
                
            except Exception as e:
                 console.print(f"[bold red]✖ Error:[/bold red] {str(e)}\n")

        elif choice == "4":
            console.print("\n[bold yellow]--- Deposit Funds ---[/bold yellow]")
            gid = Prompt.ask("Enter Gambler ID")
            amount = FloatPrompt.ask("Amount to Deposit ($)")
            
            with console.status("Processing transaction..."):
                res = stake_controller.process_deposit(gambler_id=int(gid), amount=amount)
                
            if res["status"] == "success":
                tx = res["transaction"]
                boundary = res["boundary"]
                console.print(f"\n[bold green]✔ Deposited ${tx.amount}! New Balance: ${tx.balance_after}[/bold green]")
                if boundary.warning_message:
                    console.print(f"[bold yellow]⚠ Warning: {boundary.warning_message}[/bold yellow]\n")
            else:
                console.print(f"\n[bold red]✖ Error:[/bold red] {res['message']}\n")

        elif choice == "5":
            console.print("\n[bold yellow]--- Stake History Report ---[/bold yellow]")
            gid = Prompt.ask("Enter Gambler ID")
            
            with console.status("Generating report..."):
                rep_res = stake_controller.get_history_report(gambler_id=int(gid))
                
            if rep_res["status"] == "success":
                r = rep_res["report"]
                
                # Render Summary Table
                summary_table = Table(title=f"Stake Summary (Gambler {gid})")
                summary_table.add_column("Metric", style="cyan")
                summary_table.add_column("Value", style="magenta")
                summary_table.add_row("Starting Balance", f"${r.starting_balance}")
                summary_table.add_row("Current Balance", f"${r.current_balance}")
                summary_table.add_row("Peak Balance", f"${r.peak_balance}")
                summary_table.add_row("Lowest Balance", f"${r.lowest_balance}")
                
                # Color code profit/loss
                net_str = f"+${r.net_profit_loss}" if r.net_profit_loss >= 0 else f"-${abs(r.net_profit_loss)}"
                color = "green" if r.net_profit_loss >= 0 else "red"
                summary_table.add_row("Net Profit/Loss", f"[{color}]{net_str}[/{color}]")
                summary_table.add_row("Total Transactions", str(r.total_transactions))
                console.print(summary_table)
                
                # Render Recent Transactions Table
                tx_table = Table(title="Transaction History (Last 10)")
                tx_table.add_column("ID", style="dim")
                tx_table.add_column("Type", style="blue")
                tx_table.add_column("Amount", justify="right", style="green")
                tx_table.add_column("Balance After", justify="right", style="magenta")
                
                for tx in r.transactions[-10:]:
                    tx_table.add_row(
                        str(tx.transaction_id), 
                        tx.transaction_type, 
                        f"${tx.amount}", 
                        f"${tx.balance_after}"
                    )
                console.print(tx_table)
                console.print()
            else:
                console.print(f"\n[bold red]✖ Error:[/bold red] {rep_res['message']}\n")
        elif choice == "6":
            console.print("\n[bold yellow]--- Place Single Bet ---[/bold yellow]")
            gid = Prompt.ask("Enter Gambler ID")
            amount = FloatPrompt.ask("Bet Amount ($)")
            
            with console.status("Rolling the dice..."):
                res = betting_controller.play_single_game(int(gid), amount)
                
            if res["status"] == "success":
                data = res["data"]
                outcome = data['game'].outcome
                color = "green" if outcome == "WIN" else "red"
                console.print(f"\n[bold {color}]Outcome: {outcome}![/bold {color}]")
                console.print(f"Net Change: {data['game'].net_change}")
                console.print(f"New Balance: ${data['game'].stake_after}\n")
            else:
                console.print(f"\n[bold red]✖ Error:[/bold red] {res['message']}\n")

        elif choice == "7":
            console.print("\n[bold yellow]--- Auto-Play Strategy ---[/bold yellow]")
            gid = Prompt.ask("Enter Gambler ID")
            
            # Show options and get strategy
            strategy_choices = ["FIXED", "PERCENTAGE", "MARTINGALE", "REVERSE_MARTINGALE"]
            console.print(f"Available Strategies: [cyan]{', '.join(strategy_choices)}[/cyan]")
            strategy_code = Prompt.ask("Select Strategy", choices=strategy_choices, default="MARTINGALE")
            
            # If percentage, we ask for % instead of $. Otherwise, standard base bet.
            if strategy_code == "PERCENTAGE":
                base = FloatPrompt.ask("Bet Percentage of Stake (%)", default=5.0)
            else:
                base = FloatPrompt.ask("Base Bet Amount ($)")
                
            rounds = int(Prompt.ask("Max Rounds to Play"))
            
            with console.status(f"Playing {strategy_code} strategy..."):
                # Pass their chosen strategy_code directly into the controller!
                res = betting_controller.play_auto_strategy(int(gid), base, rounds, strategy_code)
                
            if res["status"] == "success":
                console.print(f"\n[bold green]✔ Auto-Play Complete. Rounds Played: {res['rounds_played']}[/bold green]")
                
                # Print History Table
                table = Table(title=f"Betting History ({strategy_code})")
                table.add_column("Round", style="dim")
                table.add_column("Bet", style="cyan")
                table.add_column("Outcome", style="bold")
                table.add_column("Balance After", style="magenta")
                
                for i, r in enumerate(res["history"]):
                    if "status" in r and r["status"] == "error":
                        console.print(f"[bold red]Stopped at round {r['round']} due to error: {r['message']}[/bold red]")
                        break
                    
                    g = r["game"]
                    color = "green" if g.outcome == "WIN" else "red"
                    
                    # Ensure payout and loss are displayed nicely with two decimals
                    bet_val = g.payout_amount if g.outcome == 'WIN' else g.loss_amount
                    table.add_row(str(i+1), f"${bet_val:.2f}", f"[{color}]{g.outcome}[/{color}]", f"${g.stake_after:.2f}")
                console.print(table)

        elif choice == "8":
            console.print("\n[bold yellow]--- Start Session ---[/bold yellow]")
            gid = Prompt.ask("Enter Gambler ID")
            res = session_controller.start_session(int(gid))
            if res["status"] == "success":
                console.print(f"[bold green]✔ Session {res['data'].session_id} Started! Good luck![/bold green]")
            else:
                console.print(f"[bold red]✖ Error:[/bold red] {res['message']}")

        elif choice == "9":
            console.print("\n[bold yellow]--- Pause/Resume Session ---[/bold yellow]")
            gid = Prompt.ask("Enter Gambler ID")
            action = Prompt.ask("Action", choices=["PAUSE", "RESUME"])
            res = session_controller.manage_pause_resume(int(gid), action)
            if res["status"] == "success":
                console.print(f"[bold green]✔ Session is now {res['data'].status}[/bold green]")
            else:
                console.print(f"[bold red]✖ Error:[/bold red] {res['message']}")

        elif choice == "10":
            console.print("\n[bold yellow]--- End Session ---[/bold yellow]")
            gid = Prompt.ask("Enter Gambler ID")
            res = session_controller.end_session(int(gid))
            if res["status"] == "success":
                s = res['data']
                console.print(f"[bold green]✔ Session Ended ([/bold green]{s.end_reason}[bold green])[/bold green]")
                console.print(f"Ending Balance: ${s.ending_stake}")
                console.print(f"Total Pause Time: {s.total_pause_seconds} seconds")
            else:
                console.print(f"[bold red]✖ Error:[/bold red] {res['message']}")

        elif choice == "10a":
            console.print("\n[bold yellow]--- Session Summary ---[/bold yellow]")
            sid = Prompt.ask("Enter Session ID")
            res = session_controller.get_session_info(int(sid))
            
            if res["status"] == "success":
                s = res["data"]
                table = Table(title=f"Session {sid} Report")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="magenta")
                table.add_row("Status", s['status'])
                table.add_row("End Reason", str(s['end_reason']))
                table.add_row("Games Played", str(s['games_played']))
                table.add_row("Starting Stake", f"${s['starting_stake']}")
                table.add_row("Ending Stake", f"${s['ending_stake']}" if s['ending_stake'] else "Ongoing")
                table.add_row("Peak Stake", f"${s['peak_stake']}")
                table.add_row("Lowest Stake", f"${s['lowest_stake']}")
                table.add_row("Total Pause Time", f"{s['total_pause_seconds']} seconds")
                console.print(table)
            else:
                console.print(f"[bold red]✖ Error:[/bold red] {res['message']}")
        
        elif choice == "11":
            console.print("\n[bold yellow]--- Advanced Statistics (UC5) ---[/bold yellow]")
            sid = Prompt.ask("Enter Session ID")
            
            with console.status("Calculating deep statistics..."):
                res = win_loss_controller.get_latest_statistics(int(sid))
            
            if res["status"] == "success":
                snap = res["data"]
                table = Table(title=f"Deep Stats for Session {sid}")
                table.add_column("Metric", style="cyan")
                table.add_column("Value", style="magenta")
                
                # Format Decimals nicely
                winnings = float(snap['total_winnings'])
                losses = float(snap['total_losses_amount'])
                net = float(snap['net_profit'])
                win_rate = float(snap['win_rate']) * 100
                roi = float(snap['roi']) * 100
                
                table.add_row("Total Winnings / Losses", f"${winnings:.2f} / ${losses:.2f}")
                table.add_row("Net Profit", f"${net:.2f}")
                table.add_row("Win Rate", f"{win_rate:.1f}%")
                table.add_row("Profit Factor", f"{snap['profit_factor']:.2f}x")
                table.add_row("Session ROI", f"{roi:.2f}%")
                table.add_row("Longest Streaks", f"Wins: {snap['longest_win_streak']} | Losses: {snap['longest_loss_streak']}")
                table.add_row("Current Streaks", f"Wins: {snap['current_win_streak']} | Losses: {snap['current_loss_streak']}")
                console.print(table)
            else:
                console.print(f"\n[bold red]✖ Error:[/bold red] {res['message']}\n")

        elif choice == "12":
            console.print("[bold cyan]Exiting application. Goodbye![/bold cyan]")
            break

if __name__ == "__main__":
    main()