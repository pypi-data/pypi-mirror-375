"""Main CLI interface for DevMatch."""

import sys
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .auth import AuthManager
from .config import ConfigManager
from .firebase_client import FirebaseClient

console = Console()
app = typer.Typer(
    name="devmatch",
    help="DevMatch CLI - A minimal developer collaborative platform client",
    add_completion=False
)

# Global instances
auth_manager = AuthManager()
config_manager = ConfigManager()
firebase_client = FirebaseClient()

def check_auth_requirements(command: str, subcommand: Optional[str] = None) -> bool:
    """Check if authentication requirements are met for a command."""
    if config_manager.requires_auth(command, subcommand):
        if not auth_manager.is_authenticated():
            console.print("[red]This command requires authentication. Please run 'devmatch login' first.[/red]")
            return False
    
    if config_manager.requires_github_auth(command, subcommand):
        github_token = auth_manager.get_github_token()
        if not github_token:
            console.print("[red]This command requires GitHub authentication. Please run 'devmatch login' first.[/red]")
            return False
    
    return True

@app.command()
def help(
    command: Optional[str] = typer.Argument(None, help="Get help for a specific command")
):
    """Show help information."""
    if command:
        # Show help for specific command
        commands = config_manager.get_commands()
        for cmd in commands:
            cmd_name = cmd.get('name', '')
            if cmd_name == command or cmd_name.startswith(f"{command} "):
                console.print(f"\n[bold blue]Command:[/bold blue] {cmd_name}")
                
                if cmd.get('requires_app_auth'):
                    console.print("[yellow]Requires authentication[/yellow]")
                
                if cmd.get('requires_github_auth'):
                    console.print("[yellow]Requires GitHub authentication[/yellow]")
                    scopes = cmd.get('scopes', [])
                    if scopes:
                        console.print(f"[dim]Required scopes: {', '.join(scopes)}[/dim]")
                
                console.print()
                return
        
        console.print(f"[red]Command '{command}' not found[/red]")
    else:
        # Show general help
        show_help()

@app.command()
def login():
    """Login with GitHub via Firebase authentication."""
    console.print("[blue]DevMatch Login[/blue]\n")
    
    if auth_manager.is_authenticated():
        console.print("[green]Already logged in![/green]")
        console.print("Run 'devmatch logout' to logout and login with a different account.")
        return
    
    success = auth_manager.github_login()
    if success:
        console.print("[green]Welcome to DevMatch! 🎉[/green]")
        console.print("You can now use all DevMatch commands.")
    else:
        console.print("[red]Login failed. Please try again.[/red]")

@app.command()
def logout():
    """Logout and clear authentication."""
    if not auth_manager.is_authenticated():
        console.print("[yellow]Not currently logged in[/yellow]")
        return
    
    auth_manager.logout()

@app.command()
def whoami():
    """Show current user information."""
    if not check_auth_requirements("whoami"):
        return
    
    console.print("[blue]Fetching user information...[/blue]")
    
    auth_headers = auth_manager.get_auth_headers()
    response = firebase_client.command_handler("whoami", [], auth_headers)
    firebase_client.format_response(response, "whoami")

@app.command()
def coffee():
    """Get your daily dose of developer coffee ☕"""
    console.print("[blue]Brewing your developer coffee...[/blue]")
    
    # Coffee command doesn't require auth according to config
    response = firebase_client.command_handler("coffee", [])
    firebase_client.format_response(response, "coffee")

@app.command()
def whatcanibuild():
    """Get project suggestions based on your skills."""
    if not check_auth_requirements("whatcanibuild"):
        return
    
    console.print("[blue]Analyzing your skills for project suggestions...[/blue]")
    
    auth_headers = auth_manager.get_auth_headers()
    response = firebase_client.command_handler("whatcanibuild", [], auth_headers)
    firebase_client.format_response(response, "whatcanibuild")

@app.command()
def setvibe(
    vibe: str = typer.Argument(..., help="Your current vibe/mood")
):
    """Set your current vibe."""
    if not check_auth_requirements("setvibe"):
        return
    
    console.print(f"[blue]Setting your vibe to: {vibe}[/blue]")
    
    auth_headers = auth_manager.get_auth_headers()
    response = firebase_client.command_handler("setvibe", [vibe], auth_headers)
    firebase_client.format_response(response, "setvibe")

@app.command()
def getmymatch():
    """Find your developer match."""
    if not check_auth_requirements("getmymatch"):
        return
    
    console.print("[blue]Finding your perfect developer match...[/blue]")
    
    auth_headers = auth_manager.get_auth_headers()
    response = firebase_client.command_handler("getmymatch", [], auth_headers)
    firebase_client.format_response(response, "getmymatch")

@app.command()
def follow(
    username: str = typer.Argument(..., help="GitHub username to follow")
):
    """Follow a developer on GitHub."""
    if not check_auth_requirements("follow"):
        return
    
    console.print(f"[blue]Following {username} on GitHub...[/blue]")
    
    auth_headers = auth_manager.get_auth_headers()
    github_token = auth_manager.get_github_token()
    
    # Pass both the username and GitHub token to the backend
    args = [username]
    if github_token:
        args.append(github_token)
    response = firebase_client.command_handler("follow", args, auth_headers)
    firebase_client.format_response(response, "follow")

@app.command()
def debug():
    """Show debug information."""
    console.print("[blue]DevMatch Debug Information[/blue]\n")
    
    table = Table(title="Debug Info", show_header=True, header_style="bold blue")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    # Authentication status
    is_auth = auth_manager.is_authenticated()
    table.add_row("Authenticated", "✓" if is_auth else "✗")
    
    if is_auth:
        tokens = auth_manager.get_cached_tokens()
        if tokens:
            table.add_row("User ID", tokens.get('uid', 'Unknown'))
            table.add_row("GitHub Token", "✓" if tokens.get('github_token') else "✗")
    
    # Commands status
    commands = config_manager.get_commands()
    table.add_row("Available Commands", str(len(commands)))
    
    # Firebase connection
    table.add_row("Firebase Project", config_manager.project_id)
    table.add_row("Firebase Region", firebase_client.region)
    
    console.print(table)
    console.print()
    
    # List available commands
    if commands:
        console.print("[bold blue]Available Commands:[/bold blue]")
        for cmd in commands:
            name = cmd.get('name', 'Unknown')
            auth_req = "🔒" if cmd.get('requires_app_auth') else "🔓"
            github_req = "🐙" if cmd.get('requires_github_auth') else ""
            console.print(f"  {auth_req}{github_req} {name}")
        console.print()

def show_help():
    """Show general help information."""
    console.print(Panel.fit(
        "[bold blue]DevMatch CLI[/bold blue]\n"
        "A minimal developer collaborative platform client\n\n"
        "Get started by running: [bold green]devmatch login[/bold green]",
        border_style="blue"
    ))
    
    console.print("\n[bold blue]Available Commands:[/bold blue]")
    
    # Fetch and display commands from config
    commands = config_manager.get_commands()
    
    if commands:
        for cmd in commands:
            name = cmd.get('name', 'Unknown')
            auth_indicator = "🔒" if cmd.get('requires_app_auth') else "🔓"
            github_indicator = "🐙" if cmd.get('requires_github_auth') else ""
            
            console.print(f"  {auth_indicator}{github_indicator} [green]{name}[/green]")
    else:
        console.print("  [yellow]No commands available (check your internet connection)[/yellow]")
    
    console.print("\n[dim]Legend: 🔒 = Requires login, 🐙 = Requires GitHub permissions[/dim]")
    console.print("\n[bold]Usage:[/bold] devmatch [command] [options]")
    console.print("[bold]Example:[/bold] devmatch coffee")

# Handle unknown commands by forwarding to Firebase
def handle_unknown_command(command_parts: List[str]):
    """Handle commands not explicitly defined in the CLI."""
    if not command_parts:
        show_help()
        return
    
    command = command_parts[0]
    args = command_parts[1:] if len(command_parts) > 1 else []
    
    # Check if it's a valid command from config
    config = config_manager.validate_command(command)
    if not config.get('valid', True):
        console.print(f"[red]Unknown command: {command}[/red]")
        console.print("Run 'devmatch help' to see available commands.")
        return
    
    # Check authentication requirements
    if not check_auth_requirements(command):
        return
    
    console.print(f"[blue]Executing: {' '.join(command_parts)}[/blue]")
    
    auth_headers = auth_manager.get_auth_headers() if config_manager.requires_auth(command) else None
    response = firebase_client.command_handler(' '.join(command_parts), args, auth_headers)
    firebase_client.format_response(response, ' '.join(command_parts))

def main():
    """Main entry point for the CLI."""
    try:
        # If no arguments provided, show help
        if len(sys.argv) == 1:
            show_help()
            return
        
        # Check if it's a known typer command
        known_commands = ['help', 'login', 'logout', 'whoami', 'coffee', 'whatcanibuild', 'setvibe', 'getmymatch', 'follow', 'debug']
        
        if len(sys.argv) > 1 and sys.argv[1] in known_commands:
            app()
        else:
            # Handle as unknown command (forward to Firebase)
            handle_unknown_command(sys.argv[1:])
    
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()