from rich.console import Console
from rich.table import Table

console = Console()

class SessionSummary:
    @staticmethod
    def display_session_summary(session_data: dict, advanced_stats: dict = None):
        sid = session_data['session_id']
        
        table = Table(title=f"Session {sid} Final Report", border_style="yellow")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        # Basic Session Info
        table.add_row("End Reason", str(session_data['end_reason']))
        table.add_row("Games Played", str(session_data['games_played']))
        table.add_row("Starting Stake", f"₹{session_data['starting_stake']}")
        table.add_row("Ending Stake", f"₹{session_data['ending_stake']}")
        table.add_row("Peak Stake", f"₹{session_data['peak_stake']}")
        table.add_row("Lowest Stake", f"₹{session_data['lowest_stake']}")
        table.add_row("Time Paused", f"{session_data['total_pause_seconds']}s")
        
        # Advanced Stats (If UC5 data is available)
        if advanced_stats:
            table.add_section()
            win_rate = float(advanced_stats['win_rate']) * 100
            table.add_row("Net Profit", f"₹{advanced_stats['net_profit']}")
            table.add_row("Win Rate", f"{win_rate:.1f}%")
            table.add_row("Profit Factor", f"{advanced_stats['profit_factor']:.2f}x")
            table.add_row("Longest Win Streak", str(advanced_stats['longest_win_streak']))
            
        console.print(table)