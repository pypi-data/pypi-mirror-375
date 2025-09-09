"""
Bitbucket client for repository access.
Implements singleton pattern to avoid excessive API calls.
"""
import os
import tempfile
from typing import Optional, Dict, Any
from pathlib import Path
import git
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class BitbucketClientError(Exception):
    """Base exception for Bitbucket client errors."""
    pass


class BitbucketClient:
    """Singleton client for Bitbucket repository access."""
    
    _instance: Optional["BitbucketClient"] = None
    _repositories_cache: Dict[str, Path] = {}
    
    def __new__(cls) -> "BitbucketClient":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self.token = os.environ.get("BITBUCKET_API_TOKEN", os.environ.get("bitbucket_token"))
            if not self.token:
                raise BitbucketClientError("BITBUCKET_API_TOKEN or bitbucket_token environment variable not set")
            
            self.email = os.environ.get("BITBUCKET_EMAIL", "")
            self._temp_dir = tempfile.mkdtemp(prefix="bitbucket_repos_")
    
    def clone_repository(self, repo_url: str) -> Path:
        """
        Clone or fetch a Bitbucket repository.
        
        Args:
            repo_url: The Bitbucket repository URL
            
        Returns:
            Path to the cloned repository
            
        Raises:
            BitbucketClientError: If cloning fails
        """
        if repo_url in self._repositories_cache:
            console.print(f"[green]Using cached repository: {repo_url}[/green]")
            return self._repositories_cache[repo_url]
        
        # Extract repo name from URL
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        
        repo_path = Path(self._temp_dir) / repo_name
        
        # Build authenticated URL
        if "bitbucket.org" in repo_url:
            # For Bitbucket Cloud
            if self.email:
                auth_url = repo_url.replace("https://", f"https://{self.email}:{self.token}@")
            else:
                auth_url = repo_url.replace("https://", f"https://x-token-auth:{self.token}@")
        else:
            # For Bitbucket Server/Data Center
            auth_url = repo_url.replace("https://", f"https://token:{self.token}@")
        
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
                    # Clone new repository
                    git.Repo.clone_from(
                        auth_url,
                        repo_path,
                        depth=1  # Shallow clone for efficiency
                    )
                    console.print(f"[green]Cloned repository: {repo_name}[/green]")
                
                progress.update(task, completed=True)
            
            self._repositories_cache[repo_url] = repo_path
            return repo_path
            
        except Exception as e:
            raise BitbucketClientError(f"Failed to clone repository {repo_url}: {str(e)}")
    
    def get_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL."""
        repo_name = repo_url.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        return repo_name