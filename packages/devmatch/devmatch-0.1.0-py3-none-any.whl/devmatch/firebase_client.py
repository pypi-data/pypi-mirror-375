"""Firebase client for calling Firebase Cloud Functions."""

from pathlib import Path
import requests
from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
import json

console = Console()

class FirebaseClient:
    """Client for Firebase Cloud Functions."""
    
    def __init__(self, project_id: str = "devmatch-fda15", region: str = "us-central1"):
        self.project_id = project_id
        self.region = region
        self.base_url = f"https://{region}-{project_id}.cloudfunctions.net"
    
    def call_function(self, function_name: str, data: Dict[str, Any], auth_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Call a Firebase Cloud Function."""
        url = f"{self.base_url}/{function_name}"
        headers = {"Content-Type": "application/json"}
        
        if auth_headers:
            headers.update(auth_headers)
        
        # Wrap data in the format expected by Firebase callable functions
        payload = {"data": data}
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                # Firebase callable functions return data in 'result' field
                return {
                    'success': True,
                    'data': response_data.get('result', response_data)
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'status_code': response.status_code
                }
                
        except requests.RequestException as e:
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
    
    def github_login(self, command: str, uid: Optional[str] = None, args: Optional[List[str]] = None) -> Dict[str, Any]:
        """Call the onGithubLogin function."""
        data = {
            "command": command,
            "uid": uid,
            "args": args or []
        }
        
        return self.call_function("onGithubLogin", data)
    

    def command_handler(self, command: str, args: Optional[List[str]] = None, auth_headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Call the commandHandler function."""
        
        # Load UID from token cache
        token_file = Path.home() / ".devmatch" / "tokens.json"
        uid = None
        if token_file.exists():
            try:
                with open(token_file, "r") as f:
                    tokens = json.load(f)
                uid = tokens.get("uid")
            except Exception:
                uid = None

        data = {
            "command": command,
            "args": args or []
        }
        if uid:
            data["uid"] = uid   # ✅ include uid for backend
       
        return self.call_function("commandHandler", data, auth_headers) 
    def format_response(self, response: Dict[str, Any], command: str = "") -> None:
        """Format and display the response from a Firebase function, with interactive options executed sequentially."""
        if not response.get('success', False):
            # Error response
            error_msg = response.get('error', 'Unknown error')
            console.print(f"\n[red]✗ Error executing command '{command}'[/red]")
            console.print(f"[red]{error_msg}[/red]\n")
            return

        data = response.get('data', {})

        # Print main output if exists
        output = data.get('output')
        if output:
            console.print(Panel(output, title="Output", border_style="green"))

        # Handle interactive options
        options = data.get('options', [])
        for option in options:
            label = option.get('label', 'Do you want to proceed?')
            cmd = option.get('command')
            if not cmd:
                continue

            # Ask the user
            console.print(f"[yellow]{label}[/yellow] (y/n): ", end="")
            choice = input().strip().lower()
            if choice in ('y', 'yes'):
                console.print(f"\n[blue]Executing command:[/blue] {cmd}\n")
                
                # Execute the option command using command_handler
                option_response = self.command_handler(cmd)
                
                # Recursively format and display the option's response
                self.format_response(option_response, cmd)
            else:
                console.print("[dim]Skipped.[/dim]\n")

     
    def _format_dict_response(self, data: Dict[str, Any], command: str) -> None:
        """Format dictionary responses in a readable way."""
        if not data:
            console.print(f"\n[green]✓ Command '{command}' executed successfully[/green]\n")
            return
        
        # Create a nice table for structured data
        if len(data) <= 5 and all(isinstance(v, (str, int, float, bool)) for v in data.values()):
            table = Table(title=f"Results for '{command}'", show_header=True, header_style="bold blue")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            
            for key, value in data.items():
                table.add_row(str(key).title(), str(value))
            
            console.print("\n")
            console.print(table)
            console.print("\n")
        else:
            # For complex data, use JSON formatting
            console.print(f"\n[green]✓ Results for '{command}':[/green]")
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)
            console.print(Panel(syntax, title="Response Data", border_style="blue"))
            console.print("\n")
    
    def _format_list_response(self, data: List[Any], command: str) -> None:
        """Format list responses in a readable way."""
        if not data:
            console.print(f"\n[green]✓ Command '{command}' executed successfully (no results)[/green]\n")
            return
        
        console.print(f"\n[green]✓ Results for '{command}' ({len(data)} items):[/green]\n")
        
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                console.print(f"[cyan]{i}.[/cyan]")
                for key, value in item.items():
                    console.print(f"  [dim]{key}:[/dim] {value}")
                console.print()
            elif isinstance(item, str):
                console.print(f"[cyan]{i}.[/cyan] {item}")
            else:
                console.print(f"[cyan]{i}.[/cyan] {str(item)}")
        
        console.print()