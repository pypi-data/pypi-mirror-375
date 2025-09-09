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
from .analyzers.business_analyzer import BusinessAnalyzer
from .generators.postman import PostmanCollectionGenerator
from .generators.business_report import BusinessReportGenerator
import json

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


class GenerateProductOwnerOverviewInput(BaseModel):
    """Input model for generate_product_owner_overview tool."""
    repo_url: str = Field(
        description="The Git repository URL (e.g., https://github.com/org/repo.git or https://bitbucket.org/org/repo.git)"
    )


class GenerateProductOwnerOverviewOutput(BaseModel):
    """Output model for generate_product_owner_overview tool."""
    success: bool
    report_path: str = Field(description="Path to the generated Product Owner report (Markdown)")
    json_path: str = Field(description="Path to the structured business analysis data (JSON)")
    message: str
    features_count: int = 0
    completion_score: float = Field(description="Overall feature completion percentage (0.0 to 1.0)")
    risk_level: str = Field(description="Overall risk assessment level")
    errors: list[str] = Field(default_factory=list)


class AnalyzeRepositoryForLLMInput(BaseModel):
    """Input model for analyze_repository_for_llm tool."""
    repo_url: str = Field(
        description="The Git repository URL (e.g., https://github.com/org/repo.git or https://bitbucket.org/org/repo.git)"
    )
    max_files: int = Field(
        default=50,
        description="Maximum number of files to return for analysis (to avoid token limits)"
    )
    file_extensions: list[str] = Field(
        default_factory=lambda: [".py", ".java", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".rb", ".php", ".cs", ".cpp", ".c", ".h", ".yaml", ".yml", ".json", ".xml", ".md"],
        description="File extensions to include in analysis"
    )


class AnalyzeRepositoryForLLMOutput(BaseModel):
    """Output model for analyze_repository_for_llm tool."""
    success: bool
    repo_name: str
    repo_structure: dict = Field(description="Repository structure and file tree")
    code_files: dict = Field(description="Dictionary of file paths to file contents")
    total_files: int
    analyzed_files: int
    message: str
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


@mcp.tool(name="generate_product_owner_overview", description="Generate a Product Owner business analysis report from a Git repository")
def generate_product_owner_overview(input: GenerateProductOwnerOverviewInput) -> GenerateProductOwnerOverviewOutput:
    """
    Generate a comprehensive Product Owner report from a Git repository.
    
    This tool will:
    1. Clone the specified Git repository
    2. Analyze the codebase for business features and functionality
    3. Generate a comprehensive Product Owner report in Markdown format
    4. Save both the report and structured JSON data
    """
    
    try:
        repo_url = input.repo_url
        
        # Initialize clients
        console.print(f"[blue]Starting Product Owner analysis for: {repo_url}[/blue]")
        
        git_client = GitClient()
        
        # Clone repository
        try:
            repo_path = git_client.clone_repository(repo_url)
            repo_name = git_client.get_repo_name(repo_url)
        except GitClientError as e:
            return GenerateProductOwnerOverviewOutput(
                success=False,
                report_path="",
                json_path="",
                message=f"Failed to clone repository: {str(e)}",
                errors=[str(e)]
            )
        
        # Analyze repository for business insights
        try:
            business_analyzer = BusinessAnalyzer(repo_path)
            business_report = business_analyzer.analyze()
        except Exception as e:
            console.print_exception()
            return GenerateProductOwnerOverviewOutput(
                success=False,
                report_path="",
                json_path="",
                message=f"Failed to analyze repository: {str(e)}",
                errors=[str(e)]
            )
        
        # Generate Product Owner report
        try:
            report_generator = BusinessReportGenerator()
            report_path = report_generator.generate(business_report, repo_name)
            
            # JSON path is generated alongside the markdown report
            json_path = report_path.parent / f"{repo_name}_business_analysis.json"
            
        except Exception as e:
            console.print_exception()
            return GenerateProductOwnerOverviewOutput(
                success=False,
                report_path="",
                json_path="",
                message=f"Failed to generate Product Owner report: {str(e)}",
                errors=[str(e)]
            )
        
        # Determine overall risk level
        risk_levels = [r.risk_level.value for r in business_report.risk_assessments]
        if "critical" in risk_levels:
            overall_risk = "Critical"
        elif "high" in risk_levels:
            overall_risk = "High"
        elif "medium" in risk_levels:
            overall_risk = "Medium"
        else:
            overall_risk = "Low"
        
        # Success
        return GenerateProductOwnerOverviewOutput(
            success=True,
            report_path=str(report_path.absolute()),
            json_path=str(json_path.absolute()),
            message=f"Successfully generated Product Owner report with {len(business_report.identified_features)} features analyzed",
            features_count=len(business_report.identified_features),
            completion_score=business_report.completion_score,
            risk_level=overall_risk,
            errors=[]
        )
        
    except Exception as e:
        console.print_exception()
        return GenerateProductOwnerOverviewOutput(
            success=False,
            report_path="",
            json_path="",
            message=f"Unexpected error: {str(e)}",
            errors=[str(e)]
        )


@mcp.tool(name="analyze_repository_for_llm", description="Clone and return repository code for LLM analysis")
def analyze_repository_for_llm(input: AnalyzeRepositoryForLLMInput) -> AnalyzeRepositoryForLLMOutput:
    """
    Clone a repository and return its code for LLM analysis.
    
    This tool:
    1. Clones the specified Git repository
    2. Collects relevant code files based on extensions
    3. Returns the code content for the LLM to analyze
    4. The LLM can then generate Product Owner reports, technical analysis, etc.
    """
    
    try:
        repo_url = input.repo_url
        
        # Initialize clients
        console.print(f"[blue]Cloning repository for LLM analysis: {repo_url}[/blue]")
        
        git_client = GitClient()
        
        # Clone repository
        try:
            repo_path = git_client.clone_repository(repo_url)
            repo_name = git_client.get_repo_name(repo_url)
        except GitClientError as e:
            return AnalyzeRepositoryForLLMOutput(
                success=False,
                repo_name="",
                repo_structure={},
                code_files={},
                total_files=0,
                analyzed_files=0,
                message=f"Failed to clone repository: {str(e)}",
                errors=[str(e)]
            )
        
        # Build repository structure
        console.print(f"[blue]Analyzing repository structure...[/blue]")
        repo_structure = _build_repo_structure(repo_path)
        
        # Collect code files
        console.print(f"[blue]Collecting code files for analysis...[/blue]")
        code_files = {}
        total_files = 0
        
        # Find all files with specified extensions
        for ext in input.file_extensions:
            for file_path in repo_path.rglob(f"*{ext}"):
                # Skip hidden directories and common non-source directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if any(skip in file_path.parts for skip in ['node_modules', 'venv', '__pycache__', 'dist', 'build', 'target']):
                    continue
                    
                total_files += 1
                
                if len(code_files) >= input.max_files:
                    continue
                    
                try:
                    # Get relative path for cleaner output
                    relative_path = file_path.relative_to(repo_path)
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    
                    # Skip very large files (>100KB)
                    if len(content) > 100000:
                        console.print(f"[yellow]Skipping large file: {relative_path}[/yellow]")
                        continue
                        
                    code_files[str(relative_path)] = content
                except Exception as e:
                    console.print(f"[yellow]Could not read file {file_path}: {e}[/yellow]")
        
        console.print(f"[green]Collected {len(code_files)} files out of {total_files} total files[/green]")
        
        # Return repository data for LLM analysis
        return AnalyzeRepositoryForLLMOutput(
            success=True,
            repo_name=repo_name,
            repo_structure=repo_structure,
            code_files=code_files,
            total_files=total_files,
            analyzed_files=len(code_files),
            message=f"Successfully collected {len(code_files)} files from {repo_name} for LLM analysis",
            errors=[]
        )
        
    except Exception as e:
        console.print_exception()
        return AnalyzeRepositoryForLLMOutput(
            success=False,
            repo_name="",
            repo_structure={},
            code_files={},
            total_files=0,
            analyzed_files=0,
            message=f"Unexpected error: {str(e)}",
            errors=[str(e)]
        )


def _build_repo_structure(repo_path: Path, max_depth: int = 3) -> dict:
    """Build a dictionary representing the repository structure."""
    
    def build_tree(path: Path, current_depth: int = 0) -> dict:
        if current_depth >= max_depth:
            return {"...": "truncated"}
            
        tree = {}
        try:
            for item in sorted(path.iterdir()):
                # Skip hidden files/dirs and common non-source directories
                if item.name.startswith('.'):
                    continue
                if item.name in ['node_modules', 'venv', '__pycache__', 'dist', 'build', 'target', '.git']:
                    continue
                    
                if item.is_dir():
                    tree[item.name + "/"] = build_tree(item, current_depth + 1)
                else:
                    # Just include file name, not content
                    tree[item.name] = "file"
        except PermissionError:
            tree["error"] = "Permission denied"
            
        return tree
    
    return build_tree(repo_path)


@mcp.tool()
def get_server_info() -> dict:
    """Get information about the Postman Collection Generator MCP server."""
    return {
        "name": "postman-collection-generator",
        "version": "0.2.10",
        "description": "MCP server for generating Postman collections and Product Owner business analysis reports from API codebases",
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
            "output_formats": [
                "Postman Collection v2.1",
                "Product Owner Markdown Reports",
                "Business Analysis JSON Data"
            ]
        },
        "tools": {
            "generate_collection": "Generate Postman API collections from code repositories",
            "generate_product_owner_overview": "Generate comprehensive Product Owner business analysis reports (static analysis)",
            "analyze_repository_for_llm": "Clone repository and return code for LLM-powered analysis"
        },
        "environment_variables": {
            "BITBUCKET_API_TOKEN": "Token for Bitbucket authentication (required)",
            "BITBUCKET_EMAIL": "Email for Bitbucket authentication (optional)",
            "output_directory": "Directory for generated files (default: current directory)"
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