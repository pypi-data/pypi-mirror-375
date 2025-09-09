"""
Input validation utilities.
"""
import re
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional


def validate_bitbucket_url(url: str) -> bool:
    """
    Validate that a URL is a valid Bitbucket repository URL.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if parsed.scheme not in ["http", "https"]:
            return False
        
        # Check host (support both cloud and server)
        if "bitbucket" not in parsed.hostname.lower():
            return False
        
        # Check path has at least org/repo
        path_parts = parsed.path.strip("/").split("/")
        if len(path_parts) < 2:
            return False
        
        return True
    except Exception:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to be safe for all filesystems.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    safe_chars = re.sub(r'[^\w\-_.]', '_', filename)
    
    # Remove multiple underscores
    safe_chars = re.sub(r'_+', '_', safe_chars)
    
    # Trim underscores from ends
    safe_chars = safe_chars.strip('_')
    
    return safe_chars or "output"


def validate_output_path(path: str) -> Path:
    """
    Validate and prepare output path.
    
    Args:
        path: Output directory path
        
    Returns:
        Validated Path object
        
    Raises:
        ValueError: If path is invalid
    """
    try:
        output_path = Path(path).resolve()
        
        # Create directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Check if writable
        test_file = output_path / ".write_test"
        try:
            test_file.touch()
            test_file.unlink()
        except Exception:
            raise ValueError(f"Output directory is not writable: {output_path}")
        
        return output_path
    except Exception as e:
        raise ValueError(f"Invalid output path: {str(e)}")