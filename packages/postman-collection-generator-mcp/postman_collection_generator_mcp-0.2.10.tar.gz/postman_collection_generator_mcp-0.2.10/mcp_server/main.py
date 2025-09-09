"""
Main MCP server implementation for Postman collection generation.
"""
import os
import sys
from pathlib import Path
from fastmcp import FastMCP
from pydantic import BaseModel, Field
from rich.console import Console
from rich.traceback import install
from .clients.git import GitClient, GitClientError
from .analyzers.factory import AnalyzerFactory
from .generators.postman import PostmanCollectionGenerator

# Install rich traceback handler
install(show_locals=True)
# Ensure console output goes to stderr to avoid interfering with MCP protocol
console = Console(stderr=True)

# Create FastMCP server instance
mcp = FastMCP("postman-collection-generator")


class GenerateCollectionInput(BaseModel):
    """Input model for generate_collection tool."""
    repo_url: str = Field(
        description="The Git repository URL (e.g., https://github.com/org/repo.git or https://bitbucket.org/org/repo.git)"
    )


class GenerateCollectionOutput(BaseModel):
    """Output model for generate_collection tool."""
    success: bool
    collection_path: str = Field(description="Path to the generated Postman collection file")
    message: str
    endpoints_count: int = 0
    errors: list[str] = Field(default_factory=list)


@mcp.tool(name="generate_collection", description="Generate a Postman collection from a Git repository")
def generate_collection(input: GenerateCollectionInput) -> GenerateCollectionOutput:
    """
    Generate a Postman collection from a Git repository.
    
    This tool will:
    1. Clone the specified Git repository
    2. Analyze the codebase to discover API endpoints
    3. Generate a Postman v2.1 collection file
    4. Save the collection to the output directory
    """
    
    try:
        repo_url = input.repo_url
        
        # Initialize clients
        console.print(f"[blue]Starting Postman collection generation for: {repo_url}[/blue]")
        
        git_client = GitClient()
        generator = PostmanCollectionGenerator()
        
        # Clone repository
        try:
            repo_path = git_client.clone_repository(repo_url)
            repo_name = git_client.get_repo_name(repo_url)
        except GitClientError as e:
            return GenerateCollectionOutput(
                success=False,
                collection_path="",
                message=f"Failed to clone repository: {str(e)}",
                errors=[str(e)]
            )
        
        # Analyze repository
        try:
            api_collection = AnalyzerFactory.analyze_repository(repo_path)
        except ValueError as e:
            return GenerateCollectionOutput(
                success=False,
                collection_path="",
                message=f"Failed to analyze repository: {str(e)}",
                errors=[str(e)]
            )
        except Exception as e:
            console.print_exception()
            return GenerateCollectionOutput(
                success=False,
                collection_path="",
                message=f"Unexpected error during analysis: {str(e)}",
                errors=[str(e)]
            )
        
        # Generate Postman collection
        try:
            output_path = generator.generate(api_collection, repo_name)
        except Exception as e:
            console.print_exception()
            return GenerateCollectionOutput(
                success=False,
                collection_path="",
                message=f"Failed to generate Postman collection: {str(e)}",
                errors=[str(e)]
            )
        
        # Success
        return GenerateCollectionOutput(
            success=True,
            collection_path=str(output_path.absolute()),
            message=f"Successfully generated Postman collection with {len(api_collection.endpoints)} endpoints",
            endpoints_count=len(api_collection.endpoints),
            errors=[]
        )
        
    except Exception as e:
        console.print_exception()
        return GenerateCollectionOutput(
            success=False,
            collection_path="",
            message=f"Unexpected error: {str(e)}",
            errors=[str(e)]
        )


@mcp.tool()
def get_server_info() -> dict:
    """Get information about the Postman Collection Generator MCP server."""
    return {
        "name": "postman-collection-generator",
        "version": "0.2.0",
        "description": "MCP server for generating Postman collections from API codebases with accurate DTO parsing and parameter extraction",
        "capabilities": {
            "supported_frameworks": [
                "FastAPI",
                "Spring Boot", 
                "Flask (coming soon)",
                "Django (coming soon)",
                "Express (coming soon)",
                "NestJS (coming soon)"
            ],
            "supported_specs": [
                "OpenAPI 3.x",
                "Swagger 2.0"
            ],
            "output_format": "Postman Collection v2.1"
        },
        "environment_variables": {
            "BITBUCKET_API_TOKEN": "Token for Bitbucket authentication (required)",
            "BITBUCKET_EMAIL": "Email for Bitbucket authentication (optional)",
            "output_directory": "Directory for generated collections (default: current directory)"
        }
    }


def run():
    """Run the MCP server."""
    # Show authentication status with debugging
    github_token = os.environ.get("GITHUB_TOKEN")
    bitbucket_token = os.environ.get("BITBUCKET_API_TOKEN") or os.environ.get("bitbucket_token")
    bitbucket_email = os.environ.get("BITBUCKET_EMAIL", "")
    
    console.print("[blue]--- Environment Variables Debug ---[/blue]")
    console.print(f"[blue]BITBUCKET_EMAIL: '{bitbucket_email}'[/blue]")
    console.print(f"[blue]BITBUCKET_API_TOKEN: '{bitbucket_token[:20] if bitbucket_token else None}...' (truncated)[/blue]")
    console.print(f"[blue]GITHUB_TOKEN: {'SET' if github_token else 'NOT SET'}[/blue]")
    console.print(f"[blue]output_directory: '{os.environ.get('output_directory', 'NOT SET')}'[/blue]")
    console.print("[blue]--- End Debug ---[/blue]")
    
    if github_token:
        console.print("[green]✓ GitHub token configured[/green]")
    else:
        console.print("[yellow]⚠ GitHub token not set (GITHUB_TOKEN) - private repos will not be accessible[/yellow]")
    
    if bitbucket_token:
        console.print("[green]✓ Bitbucket token configured[/green]")
    else:
        console.print("[yellow]⚠ Bitbucket token not set (BITBUCKET_API_TOKEN) - private repos will not be accessible[/yellow]")
    
    if bitbucket_email:
        console.print("[green]✓ Bitbucket email configured[/green]")
    else:
        console.print("[yellow]⚠ Bitbucket email not set (BITBUCKET_EMAIL)[/yellow]")
    
    output_dir = os.environ.get("output_directory", ".")
    console.print(f"[green]Output directory: {Path(output_dir).absolute()}[/green]")
    
    # Check for command-line arguments to determine transport
    transport = "stdio"
    host = "127.0.0.1"
    port = 8000
    
    # Simple argument parsing
    if "--transport" in sys.argv:
        transport_idx = sys.argv.index("--transport")
        if transport_idx + 1 < len(sys.argv):
            transport = sys.argv[transport_idx + 1]
    
    if "--port" in sys.argv:
        port_idx = sys.argv.index("--port")
        if port_idx + 1 < len(sys.argv):
            port = int(sys.argv[port_idx + 1])
    
    if "--host" in sys.argv:
        host_idx = sys.argv.index("--host")
        if host_idx + 1 < len(sys.argv):
            host = sys.argv[host_idx + 1]
    
    # Run the server with appropriate transport
    if transport == "http":
        mcp.run(transport="http", host=host, port=port, path="/mcp")
    else:
        mcp.run()


if __name__ == "__main__":
    run()