# console.py
import sys
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .api_client import FFCapchaAPI
from .logger import setup_logger, LOG_MESSAGES

try:
    import inquirer
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
except ImportError:
    print("Please install rich and inquirer: pip install rich inquirer")
    sys.exit(1)

class ConsoleManager:
    def __init__(self, api_token: str, language: str = "en", log_level: str = "INFO"):
        self.api = FFCapchaAPI(api_token)
        if not self.api.validate_token():
            print("Invalid API token")
            sys.exit(1)
        
        self.language = language
        self.console = Console()
        self.logger = setup_logger("ConsoleManager", log_level, language)
        self.running = False
        
        self.logger.info(LOG_MESSAGES[self.language]["console_started"])
    
    def start_log(self):
        """Start interactive console interface"""
        self.running = True
        self._show_welcome()
        
        while self.running:
            try:
                questions = [
                    inquirer.List(
                        'action',
                        message="Select action",
                        choices=[
                            'View recent requests',
                            'View banned users',
                            'View captcha statistics',
                            'View overall statistics',
                            'Manage user bans',
                            'Export data',
                            'Settings',
                            'Exit'
                        ]
                    )
                ]
                
                answers = inquirer.prompt(questions)
                action = answers['action']
                
                if action == 'View recent requests':
                    self._show_recent_requests()
                elif action == 'View banned users':
                    self._show_banned_users()
                elif action == 'View captcha statistics':
                    self._show_captcha_stats()
                elif action == 'View overall statistics':
                    self._show_overall_stats()
                elif action == 'Manage user bans':
                    self._manage_bans()
                elif action == 'Export data':
                    self._export_data()
                elif action == 'Settings':
                    self._settings_menu()
                elif action == 'Exit':
                    self.running = False
                    
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
    
    def _show_welcome(self):
        """Show welcome panel"""
        bot_info = self.api.get_bot_info()
        bot_name = bot_info.get('name', 'Unknown Bot')
        
        welcome_text = Text()
        welcome_text.append("FFcapcha Console Manager\n", style="bold green")
        welcome_text.append(f"Bot: {bot_name}\n")
        welcome_text.append(f"Version: 1.3.5\n")
        welcome_text.append(f"Language: {self.language.upper()}\n")
        welcome_text.append("Use arrow keys to navigate, Enter to select")
        
        panel = Panel(welcome_text, title="Welcome", border_style="blue")
        self.console.print(panel)
    
    def _show_recent_requests(self, limit: int = 20):
        """Show recent requests in a table"""
        with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
            task = progress.add_task("Loading recent requests...", total=1)
            requests = self.api.get_recent_requests(limit)
            progress.update(task, completed=1)
        
        if not requests:
            self.console.print("[yellow]No recent requests found[/yellow]")
            return
        
        table = Table(title=f"Recent Requests (Last {len(requests)})")
        table.add_column("User ID", style="cyan")
        table.add_column("Command", style="magenta")
        table.add_column("Success", style="green")
        table.add_column("Timestamp", style="yellow")
        
        for req in requests:
            success = "✅" if req.get('success') else "❌"
            timestamp = datetime.fromisoformat(req.get('timestamp', '')).strftime('%Y-%m-%d %H:%M:%S')
            table.add_row(
                str(req.get('user_id', 'N/A')),
                req.get('command', 'N/A'),
                success,
                timestamp
            )
        
        self.console.print(table)
    
    def _show_banned_users(self):
        """Show banned users"""
        with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
            task = progress.add_task("Loading banned users...", total=1)
            bans = self.api.get_banned_users()
            progress.update(task, completed=1)
        
        if not bans:
            self.console.print("[green]No banned users[/green]")
            return
        
        table = Table(title=f"Banned Users ({len(bans)})")
        table.add_column("User ID", style="cyan")
        table.add_column("Reason", style="red")
        table.add_column("Duration", style="yellow")
        table.add_column("Banned At", style="magenta")
        
        for ban in bans:
            duration = f"{ban.get('duration', 0)}s"
            banned_at = datetime.fromisoformat(ban.get('timestamp', '')).strftime('%Y-%m-%d %H:%M:%S')
            table.add_row(
                str(ban.get('user_id', 'N/A')),
                ban.get('reason', 'N/A'),
                duration,
                banned_at
            )
        
        self.console.print(table)
    
    def _show_captcha_stats(self):
        """Show captcha statistics"""
        with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
            task = progress.add_task("Loading captcha statistics...", total=1)
            stats = self.api.get_captcha_stats()
            progress.update(task, completed=1)
        
        if not stats:
            self.console.print("[yellow]No captcha statistics available[/yellow]")
            return
        
        table = Table(title="Captcha Statistics")
        table.add_column("Type", style="cyan")
        table.add_column("Total Attempts", style="magenta")
        table.add_column("Success Rate", style="green")
        table.add_column("Avg. Attempts", style="yellow")
        
        for captcha_type, data in stats.items():
            total = data.get('total_attempts', 0)
            successful = data.get('successful_attempts', 0)
            rate = (successful / total * 100) if total > 0 else 0
            avg_attempts = data.get('average_attempts', 0)
            
            table.add_row(
                captcha_type.capitalize(),
                str(total),
                f"{rate:.1f}%",
                f"{avg_attempts:.2f}"
            )
        
        self.console.print(table)
    
    def _show_overall_stats(self):
        """Show overall statistics"""
        with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
            task = progress.add_task("Loading statistics...", total=1)
            stats = self.api.get_stats()
            progress.update(task, completed=1)
        
        if not stats:
            self.console.print("[yellow]No statistics available[/yellow]")
            return
        
        table = Table(title="Overall Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for key, value in stats.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    table.add_row(f"{key}.{sub_key}", str(sub_value))
            else:
                table.add_row(key.replace('_', ' ').title(), str(value))
        
        self.console.print(table)
    
    def _manage_bans(self):
        """Manage user bans"""
        questions = [
            inquirer.List(
                'ban_action',
                message="Ban management",
                choices=[
                    'Unban user',
                    'View ban details',
                    'Back'
                ]
            )
        ]
        
        answers = inquirer.prompt(questions)
        action = answers['ban_action']
        
        if action == 'Unban user':
            user_id = inquirer.text(message="Enter user ID to unban:")
            if user_id and user_id.isdigit():
                # This would need API endpoint for unbanning
                self.console.print(f"[green]User {user_id} would be unbanned (API endpoint needed)[/green]")
            else:
                self.console.print("[red]Invalid user ID[/red]")
        
        elif action == 'View ban details':
            user_id = inquirer.text(message="Enter user ID:")
            if user_id and user_id.isdigit():
                bans = self.api.get_banned_users()
                user_bans = [ban for ban in bans if str(ban.get('user_id')) == user_id]
                
                if user_bans:
                    for ban in user_bans:
                        self.console.print(Panel(
                            f"User ID: {ban['user_id']}\n"
                            f"Reason: {ban['reason']}\n"
                            f"Duration: {ban['duration']}s\n"
                            f"Banned at: {ban['timestamp']}",
                            title="Ban Details"
                        ))
                else:
                    self.console.print("[green]No bans found for this user[/green]")
    
    def _export_data(self):
        """Export data to file"""
        questions = [
            inquirer.List(
                'export_type',
                message="Export type",
                choices=['JSON', 'CSV', 'Back']
            )
        ]
        
        answers = inquirer.prompt(questions)
        export_type = answers['export_type']
        
        if export_type == 'Back':
            return
        
        filename = inquirer.text(message="Enter filename:", default=f"ffcapcha_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if export_type == 'JSON':
            data = {
                'requests': self.api.get_recent_requests(1000),
                'bans': self.api.get_banned_users(),
                'stats': self.api.get_stats(),
                'captcha_stats': self.api.get_captcha_stats()
            }
            
            import json
            with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"[green]Data exported to {filename}.json[/green]")
        
        elif export_type == 'CSV':
            # CSV export implementation would go here
            self.console.print("[yellow]CSV export not implemented yet[/yellow]")
    
    def _settings_menu(self):
        """Settings menu"""
        questions = [
            inquirer.List(
                'setting',
                message="Settings",
                choices=['Change language', 'Refresh interval', 'Back']
            )
        ]
        
        answers = inquirer.prompt(questions)
        setting = answers['setting']
        
        if setting == 'Change language':
            new_lang = inquirer.list_input("Select language", choices=['en', 'ru', 'es', 'de', 'fr'])
            self.language = new_lang
            self.logger = setup_logger("ConsoleManager", "INFO", new_lang)
            self.console.print(f"[green]Language changed to {new_lang}[/green]")
        
        elif setting == 'Refresh interval':
            interval = inquirer.text(message="Refresh interval (seconds):", default="5")
            self.console.print(f"[green]Refresh interval set to {interval}s[/green]")

def main():
    """Main function for console entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="FFcapcha Console Manager")
    parser.add_argument("--token", required=True, help="API token")
    parser.add_argument("--lang", default="en", help="Language (en, ru, es, de, fr)")
    parser.add_argument("--log-level", default="INFO", help="Log level")
    
    args = parser.parse_args()
    
    try:
        console = ConsoleManager(args.token, args.lang, args.log_level)
        console.start_log()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()