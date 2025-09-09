"""
Factory for creating appropriate analyzers based on repository content.
"""
from pathlib import Path
from typing import Optional, List
from .base import BaseAnalyzer
from .openapi import OpenApiAnalyzer
from .fastapi import FastAPIAnalyzer
from .spring_boot import SpringBootAnalyzer
from ..models.api import ApiCollection
from rich.console import Console

console = Console(stderr=True)


class AnalyzerFactory:
    """Factory for creating and running appropriate analyzers."""
    
    # Analyzers in priority order
    ANALYZERS = [
        OpenApiAnalyzer,      # Prefer OpenAPI spec if available
        SpringBootAnalyzer,   # Spring Boot Java applications
        FastAPIAnalyzer,      # Python FastAPI applications
        # Add more analyzers here: FlaskAnalyzer, ExpressAnalyzer, etc.
    ]
    
    @classmethod
    def analyze_repository(cls, repo_path: Path) -> ApiCollection:
        """
        Analyze a repository and extract API endpoints.
        
        Args:
            repo_path: Path to the repository
            
        Returns:
            Collection of discovered API endpoints
            
        Raises:
            ValueError: If no suitable analyzer is found
        """
        # Try each analyzer in order
        for analyzer_class in cls.ANALYZERS:
            analyzer = analyzer_class(repo_path)
            
            if analyzer.can_analyze():
                console.print(f"[blue]Using {analyzer_class.__name__} to analyze repository[/blue]")
                return analyzer.analyze()
        
        # If no analyzer matches, try to provide helpful information
        raise ValueError(
            f"No suitable analyzer found for repository at {repo_path}. "
            "Supported frameworks: FastAPI, Flask, Django, Express, NestJS, Spring Boot. "
            "Ensure the repository contains recognizable framework files or an OpenAPI spec."
        )