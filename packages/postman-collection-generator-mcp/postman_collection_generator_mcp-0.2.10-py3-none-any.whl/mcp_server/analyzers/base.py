"""
Base analyzer class for API endpoint discovery.
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional
from ..models.api import ApiCollection, ApiEndpoint


class BaseAnalyzer(ABC):
    """Abstract base class for framework-specific analyzers."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
    
    @abstractmethod
    def can_analyze(self) -> bool:
        """
        Check if this analyzer can handle the repository.
        
        Returns:
            True if the analyzer can handle this repository
        """
        pass
    
    @abstractmethod
    def analyze(self) -> ApiCollection:
        """
        Analyze the repository and extract API endpoints.
        
        Returns:
            Collection of discovered API endpoints
        """
        pass
    
    def find_files(self, pattern: str) -> List[Path]:
        """Find files matching a pattern in the repository."""
        return list(self.repo_path.rglob(pattern))
    
    def read_file(self, file_path: Path) -> str:
        """Safely read a file's contents."""
        try:
            return file_path.read_text(encoding="utf-8")
        except Exception:
            return ""