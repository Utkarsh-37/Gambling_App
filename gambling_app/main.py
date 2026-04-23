import sys
from rich.console import Console
from rich.prompt import Prompt, FloatPrompt
from rich.panel import Panel
from rich.table import Table

from config.schema_manager import SchemaManager
from controllers.gambler_controller import GamblerController
from controllers.stake_controller import StakeController  # Added for UC2

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
    console.print("2. Check Profile Eligibility (By ID)")
    console.print("3. Reset Profile for New Session (By ID)")
    console.print("[dim]-- UC2: Stake Management --[/dim]")
    console.print("4. Deposit Funds (By ID)")
    console.print("5. View Stake History Report (By ID)")
    console.print("[dim]----------------------------[/dim]")
    console.print("6. Exit")
    return Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5", "6"])

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

            with console.status("Creating profile..."):
                result = gambler_controller.register_new_gambler(
                    username=username, email=email, 
                    stake=stake, win_thresh=win_thresh, loss_thresh=loss_thresh
                )
            
            if result["status"] == "success":
                profile = result["data"]
                console.print(f"\n[bold green]✔ Profile Created Successfully! Gambler ID: {profile.gambler.gambler_id}[/bold green]\n")
                
                # UC2 Extension: Automatically create the initial transaction when a user is made
                try:
                    # Log the INITIAL_STAKE
                    stake_controller.service.repo.process_transaction(
                        gambler_id=profile.gambler.gambler_id,
                        trans_type="INITIAL_STAKE",
                        amount=profile.gambler.initial_stake,
                        is_deduction=False
                    )
                except Exception as e:
                    console.print(f"[bold yellow]⚠ Profile created, but failed to log initial stake audit: {e}[/bold yellow]")
                    
            else:
                console.print(f"\n[bold red]✖ Error:[/bold red] {result['message']}\n")

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
                
                # UC2 Extension: Log the RESET transaction
                stake_controller.service.repo.process_transaction(
                    gambler_id=int(gid), trans_type="RESET", amount=g.initial_stake, is_deduction=False
                )
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
            console.print("[bold cyan]Exiting application. Goodbye![/bold cyan]")
            break

if __name__ == "__main__":
    main()