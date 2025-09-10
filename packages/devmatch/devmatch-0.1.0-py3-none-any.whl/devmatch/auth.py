import requests
import webbrowser
import time
import json
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

console = Console()

class AuthManager:
    def __init__(self):
        self.github_client_id = "Ov23ligqDInQBJ4J3fxh"
        self.github_client_secret = "ee20f77464f6ba75d32ffa4a827e1d90cadf657f"
        self.firebase_api_key = "AIzaSyBjMbeVpVbAhfaL1_X2i2agNm9C5NxL0CY"
        self.redirect_uri = "https://devmatch-fda15.firebaseapp.com/__/auth/handler"

        self.config_dir = Path.home() / ".devmatch"
        self.token_file = self.config_dir / "tokens.json"
        self.config_dir.mkdir(exist_ok=True)

    def get_cached_tokens(self):
        if not self.token_file.exists():
            return None
        try:
            with open(self.token_file, "r") as f:
                tokens = json.load(f)
            if tokens.get("expires_at", 0) <= time.time():
                return None
            return tokens
        except Exception:
            return None

    def cache_tokens(self, tokens):
        tokens["expires_at"] = time.time() + 3600
        with open(self.token_file, "w") as f:
            json.dump(tokens, f, indent=2)

    def github_login(self):
        console.print("[blue]Starting GitHub OAuth login...[/blue]")

        # Step 1: Ask user to visit GitHub OAuth page
        auth_url = (
            f"https://github.com/login/oauth/authorize"
            f"?client_id={self.github_client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope=read:user user:email"
        )
        console.print(f"[yellow]Opening browser for GitHub login...[/yellow]")
        console.print(f"[dim]If it doesn’t open, paste this into your browser: {auth_url}[/dim]")
        webbrowser.open(auth_url)

        # Step 2: Get code manually
        code = Prompt.ask("[green]Paste the 'code' parameter from the redirected URL[/green]")

        # Step 3: Exchange code for GitHub access token
        try:
            token_res = requests.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": self.github_client_id,
                    "client_secret": self.github_client_secret,
                    "code": code,
                    "redirect_uri": self.redirect_uri,
                },
                timeout=30,
            )
            token_res.raise_for_status()
            github_data = token_res.json()
            github_token = github_data.get("access_token")
            if not github_token:
                console.print(f"[red]Failed to get GitHub token: {github_data}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]Error exchanging code for GitHub token: {e}[/red]")
            return False

        # Step 4: Sign in with Firebase
        try:
            fb_res = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={self.firebase_api_key}",
                headers={"Content-Type": "application/json"},
                json={
                    "postBody": f"providerId=github.com&access_token={github_token}",
                    "requestUri": self.redirect_uri,
                    "returnSecureToken": True,
                    "returnIdpCredential": True,
                },
                timeout=30,
            )
            fb_res.raise_for_status()
            fb_data = fb_res.json()

            tokens = {
                "firebase_token": fb_data.get("idToken"),
                "refresh_token": fb_data.get("refreshToken"),
                "github_token": github_token,
                "uid": fb_data.get("localId"),
            }
            self.cache_tokens(tokens)
            console.print("[green]✓ Authentication successful![/green]")
            return True
        except Exception as e:
            console.print(f"[red]Firebase sign-in failed: {e}[/red]")
            return False

    def is_authenticated(self):
        tokens = self.get_cached_tokens()
        return tokens is not None and tokens.get("firebase_token") is not None

    def get_auth_headers(self):
        tokens = self.get_cached_tokens()
        if not tokens or not tokens.get("firebase_token"):
            return {}
        return {
            "Authorization": f"Bearer {tokens['firebase_token']}",
            "Content-Type": "application/json",
        }

    def get_github_token(self):
        tokens = self.get_cached_tokens()
        return tokens.get("github_token") if tokens else None

    def logout(self):
        if self.token_file.exists():
            self.token_file.unlink()
        console.print("[green]Logged out successfully[/green]")
