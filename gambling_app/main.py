import sys
from rich.console import Console
from rich.prompt import Prompt, FloatPrompt
from rich.panel import Panel
from rich.table import Table
from config.schema_manager import SchemaManager
from controllers.gambler_controller import GamblerController

console = Console()

def setup_infrastructure():
    """Run startup checks and schema generation."""
    with console.status("[bold green]Initializing Database Schema...") as status:
        schema_manager = SchemaManager()
        schema_manager.initialize_schema()
    console.print("[bold green]✔ Database Ready![/bold green]\n")

def display_menu():
    console.print(Panel.fit("[bold cyan]Gambling App - Main Menu (UC1)[/bold cyan]", border_style="cyan"))
    console.print("1. Create New Gambler Profile")
    console.print("2. Check Profile Eligibility (By ID)")
    console.print("3. Reset Profile for New Session (By ID)")
    console.print("4. Exit")
    return Prompt.ask("Select an option", choices=["1", "2", "3", "4"])

def main():
    # 1. Boot up DB
    try:
        setup_infrastructure()
    except Exception as e:
        console.print(f"[bold red]Failed to start application: {e}[/bold red]")
        sys.exit(1)

    controller = GamblerController()

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
                result = controller.register_new_gambler(
                    username=username, email=email, 
                    stake=stake, win_thresh=win_thresh, loss_thresh=loss_thresh
                )
            
            if result["status"] == "success":
                profile = result["data"]
                console.print(f"\n[bold green]✔ Profile Created Successfully! Gambler ID: {profile.gambler.gambler_id}[/bold green]\n")
            else:
                console.print(f"\n[bold red]✖ Error:[/bold red] {result['message']}\n")

        elif choice == "2":
            gid = Prompt.ask("Enter Gambler ID")
            try:
                is_eligible = controller.service.validate_eligibility(int(gid))
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
                    reset_profile = controller.service.reset_profile_for_new_session(int(gid))
                g = reset_profile.gambler
                console.print(f"\n[bold green]✔ Profile Reset Complete![/bold green]")
                
                # Show new limits using Rich Table
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
            console.print("[bold cyan]Exiting application. Goodbye![/bold cyan]")
            break

if __name__ == "__main__":
    main()