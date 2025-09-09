"""
Generic Git client for repository access.
Supports GitHub, Bitbucket, and other Git repositories.
"""
import os
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path
from urllib.parse import quote
import git
import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console(stderr=True)


class GitClientError(Exception):
    """Base exception for Git client errors."""
    pass


class GitClient:
    """Singleton client for Git repository access."""
    
    _instance: Optional["GitClient"] = None
    _repositories_cache: Dict[str, Path] = {}
    _bitbucket_username_cache: Optional[str] = None
    
    def __new__(cls) -> "GitClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._temp_dir = tempfile.mkdtemp(prefix="git_repos_")
    
    def clone_repository(self, repo_url: str) -> Path:
        """
        Clone or fetch a Git repository.
        
        Args:
            repo_url: The Git repository URL
            
        Returns:
            Path to the cloned repository
            
        Raises:
            GitClientError: If cloning fails
        """
        if repo_url in self._repositories_cache:
            console.print(f"[green]Using cached repository: {repo_url}[/green]")
            return self._repositories_cache[repo_url]
        
        # Extract repo name from URL
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        
        repo_path = Path(self._temp_dir) / repo_name
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(f"Cloning {repo_name}...", total=None)
                
                if repo_path.exists():
                    # Pull latest changes
                    repo = git.Repo(repo_path)
                    origin = repo.remote("origin")
                    origin.fetch()
                    origin.pull()
                    console.print(f"[green]Updated existing repository: {repo_name}[/green]")
                else:
                    # Try cloning without authentication first (for public repos)
                    clone_successful = False
                    
                    try:
                        git.Repo.clone_from(
                            repo_url,  # Use original URL without auth
                            repo_path,
                            depth=1
                        )
                        clone_successful = True
                        console.print(f"[green]Cloned public repository: {repo_name}[/green]")
                    except Exception:
                        # If public clone fails, try with authentication
                        auth_url = self._get_authenticated_url(repo_url)
                        if auth_url != repo_url:
                            try:
                                git.Repo.clone_from(
                                    auth_url,
                                    repo_path,
                                    depth=1
                                )
                                clone_successful = True
                                console.print(f"[green]Cloned private repository: {repo_name}[/green]")
                            except Exception as auth_error:
                                raise GitClientError(f"Authentication failed. Check your credentials. Error: {str(auth_error)}")
                        else:
                            # No authentication available and public clone failed
                            raise GitClientError("Repository access failed. Repository may be private and no authentication credentials provided.")
                    
                    if not clone_successful:
                        raise GitClientError("Failed to clone repository with both public and authenticated methods")
                
                progress.update(task, completed=True)
            
            self._repositories_cache[repo_url] = repo_path
            return repo_path
            
        except GitClientError:
            raise  # Re-raise our custom errors
        except Exception as e:
            raise GitClientError(f"Failed to clone repository {repo_url}: {str(e)}")
    
    def get_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL."""
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        return repo_name
    
    def _get_bitbucket_username(self) -> Optional[str]:
        """Get Bitbucket username via API using email and app password."""
        if self._bitbucket_username_cache is not None:
            return self._bitbucket_username_cache
        
        bitbucket_token = os.environ.get("BITBUCKET_API_TOKEN") or os.environ.get("bitbucket_token")
        bitbucket_email = os.environ.get("BITBUCKET_EMAIL", "")
        
        # Debug environment variables
        console.print(f"[blue]DEBUG: BITBUCKET_EMAIL = '{bitbucket_email}'[/blue]")
        console.print(f"[blue]DEBUG: BITBUCKET_API_TOKEN = '{bitbucket_token[:20] if bitbucket_token else None}...' (truncated)[/blue]")
        
        if not bitbucket_token or not bitbucket_email:
            console.print("[red]ERROR: Missing Bitbucket credentials![/red]")
            console.print(f"[red]  - BITBUCKET_EMAIL: {'✓' if bitbucket_email else '✗'}[/red]")
            console.print(f"[red]  - BITBUCKET_API_TOKEN: {'✓' if bitbucket_token else '✗'}[/red]")
            return None
        
        try:
            # Use email:app_password for API authentication
            response = requests.get(
                "https://api.bitbucket.org/2.0/user",
                auth=(bitbucket_email, bitbucket_token),
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                username = user_data.get("username")
                if username:
                    self._bitbucket_username_cache = username
                    console.print(f"[green]Retrieved Bitbucket username: {username}[/green]")
                    return username
            else:
                console.print(f"[yellow]Failed to get Bitbucket username: HTTP {response.status_code}[/yellow]")
                
        except Exception as e:
            console.print(f"[yellow]Error getting Bitbucket username: {str(e)}[/yellow]")
        
        return None
    
    def _get_authenticated_url(self, repo_url: str) -> str:
        """Get authenticated URL if credentials are available."""
        # For GitHub
        if "github.com" in repo_url:
            github_token = os.environ.get("GITHUB_TOKEN")
            if github_token:
                return repo_url.replace("https://", f"https://{github_token}@")
            # For public repos, no auth needed
            return repo_url
        
        # For Bitbucket - App passwords require username:app_password format for Git operations
        elif "bitbucket" in repo_url:
            bitbucket_token = os.environ.get("BITBUCKET_API_TOKEN") or os.environ.get("bitbucket_token")
            
            if bitbucket_token:
                # Get Bitbucket username via API (uses email:app_password)
                username = self._get_bitbucket_username()
                
                if username:
                    # Use username:app_password for Git operations
                    return repo_url.replace("https://", f"https://{username}:{bitbucket_token}@")
                else:
                    console.print("[yellow]Warning: Could not retrieve Bitbucket username, Git authentication may fail[/yellow]")
                    
            return repo_url
        
        # For other Git providers, return as-is
        return repo_url