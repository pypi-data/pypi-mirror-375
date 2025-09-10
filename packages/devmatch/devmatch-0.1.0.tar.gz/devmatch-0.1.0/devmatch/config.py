"""Configuration module for Firebase Remote Config."""

import json
from typing import Dict, List, Any, Optional
import requests
from rich.console import Console

from google.oauth2 import service_account
import google.auth.transport.requests

console = Console()


from pathlib import Path

class ConfigManager:
    """Manages Firebase Remote Config for dynamic command fetching."""

    def __init__(self, project_id: str = "devmatch-fda15", credentials_path: str = "service-key.json"):
        self.project_id = project_id
        self.remote_config_url = f"https://firebaseremoteconfig.googleapis.com/v1/projects/{project_id}/remoteConfig"
        
        # Resolve path relative to this file’s directory
        base_dir = Path(__file__).resolve().parent
        self.credentials_path = str((base_dir / credentials_path).resolve())

        self._cached_commands = None


    def _get_access_token(self) -> str:
        """Get an OAuth2 access token using the service account key."""
        scopes = ["https://www.googleapis.com/auth/firebase.remoteconfig"]
        creds = service_account.Credentials.from_service_account_file(
            self.credentials_path, scopes=scopes
        )
        auth_req = google.auth.transport.requests.Request()
        creds.refresh(auth_req)
        return creds.token

    def fetch_commands(self) -> Optional[Dict[str, Any]]:
        """Fetch command configuration from Firebase Remote Config with auth."""
        try:
            token = self._get_access_token()
            headers = {"Authorization": f"Bearer {token}"}

            response = requests.get(self.remote_config_url, headers=headers, timeout=10)

            if response.status_code == 200:
                config_data = response.json()
                parameters = config_data.get("parameters", {})
                commands_list_param = parameters.get("commands_list", {})
                default_value = commands_list_param.get("defaultValue", {})
                commands_json = default_value.get("value", "{}")

                try:
                    commands_config = json.loads(commands_json)
                    self._cached_commands = commands_config
                    return commands_config
                except json.JSONDecodeError:
                    console.print("[red]Failed to parse commands configuration from Remote Config[/red]")
                    return self._get_fallback_commands()
            else:
                console.print(f"[yellow]Failed to fetch Remote Config (status: {response.status_code}), using fallback[/yellow]")
                return self._get_fallback_commands()

        except Exception as e:
            console.print(f"[yellow]Error fetching Remote Config: {e}, using fallback[/yellow]")
            return self._get_fallback_commands()

    def _get_fallback_commands(self) -> Dict[str, Any]:
        """Get fallback command configuration when Remote Config is unavailable."""
        return {
            "defaults": {
                "requires_app_auth": True
            },
            "commands": [
                {"name": "help", "requires_app_auth": False},
                {"name": "debug", "requires_app_auth": False},
                {"name": "login", "requires_app_auth": False},
                {"name": "coffee", "requires_app_auth": False},
                {"name": "whoami"},
                {"name": "setvibe"},
                {"name": "getmymatch"},
                {
                    "name": "follow",
                    "requires_github_auth": True,
                    "scopes": ["user:follow"],
                },
            ],
        }

    def get_commands(self) -> List[Dict[str, Any]]:
        """Get list of available commands."""
        if not self._cached_commands:
            self.fetch_commands()

        if self._cached_commands:
            return self._cached_commands.get("commands", [])
        return []

    def get_defaults(self) -> Dict[str, Any]:
        """Get default command configuration."""
        if not self._cached_commands:
            self.fetch_commands()

        if self._cached_commands:
            return self._cached_commands.get("defaults", {})
        return {}

    def validate_command(self, command_name: str, subcommand: Optional[str] = None) -> Dict[str, Any]:
        """Validate a command and return its configuration."""
        commands = self.get_commands()
        defaults = self.get_defaults()

        # Build full command name
        full_command = command_name
        if subcommand:
            full_command = f"{command_name} {subcommand}"

        # Find matching command
        for cmd in commands:
            if cmd.get("name") == full_command or cmd.get("name") == command_name:
                # Merge with defaults
                config = defaults.copy()
                config.update(cmd)
                return config

        # Command not found
        return {
            "valid": False,
            "error": f"Command '{full_command}' not found",
        }

    def requires_auth(self, command_name: str, subcommand: Optional[str] = None) -> bool:
        """Check if a command requires authentication."""
        config = self.validate_command(command_name, subcommand)
        return config.get("requires_app_auth", False)

    def requires_github_auth(self, command_name: str, subcommand: Optional[str] = None) -> bool:
        """Check if a command requires GitHub authentication."""
        config = self.validate_command(command_name, subcommand)
        return config.get("requires_github_auth", False)

    def get_required_scopes(self, command_name: str, subcommand: Optional[str] = None) -> List[str]:
        """Get required GitHub scopes for a command."""
        config = self.validate_command(command_name, subcommand)
        return config.get("scopes", [])
