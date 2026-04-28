import sys
from rich.console import Console
from config.schema_manager import SchemaManager
from ui.interactive_menu import InteractiveMenu

console = Console()

def setup_infrastructure():
    """Run startup checks and schema generation."""
    with console.status("[bold green]Checking Database Schema...") as status:
        schema_manager = SchemaManager()
        schema_manager.initialize_schema()
    console.print("[bold green]✔ Database Ready![/bold green]\n")

def main():
    # 1. Boot up DB
    try:
        setup_infrastructure()
    except Exception as e:
        console.print(f"[bold red]Failed to start application: {e}[/bold red]")
        sys.exit(1)

    # 2. Hand off control to the UI Layer (UC7)
    app_menu = InteractiveMenu()
    app_menu.run()

if __name__ == "__main__":
    main()