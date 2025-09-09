"""
OpenAPI/Swagger specification analyzer.
"""
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..models.api import ApiCollection, ApiEndpoint, ApiParameter, HttpMethod, ParameterLocation
from .base import BaseAnalyzer
from rich.console import Console

console = Console()


class OpenApiAnalyzer(BaseAnalyzer):
    """Analyzer for OpenAPI/Swagger specifications."""
    
    def can_analyze(self) -> bool:
        """Check for OpenAPI/Swagger spec files."""
        spec_patterns = [
            "openapi*.json", "openapi*.yaml", "openapi*.yml",
            "swagger*.json", "swagger*.yaml", "swagger*.yml",
            "**/openapi*.json", "**/openapi*.yaml", "**/openapi*.yml",
            "**/swagger*.json", "**/swagger*.yaml", "**/swagger*.yml"
        ]
        
        for pattern in spec_patterns:
            if self.find_files(pattern):
                return True
        return False
    
    def analyze(self) -> ApiCollection:
        """Extract endpoints from OpenAPI specification."""
        spec_file = self._find_spec_file()
        if not spec_file:
            raise ValueError("No OpenAPI/Swagger specification found")
        
        console.print(f"[green]Found OpenAPI spec: {spec_file.relative_to(self.repo_path)}[/green]")
        
        spec = self._load_spec(spec_file)
        collection = self._parse_spec(spec)
        
        console.print(f"[green]Extracted {len(collection.endpoints)} endpoints from OpenAPI spec[/green]")
        return collection
    
    def _find_spec_file(self) -> Optional[Path]:
        """Find the most likely OpenAPI spec file."""
        spec_patterns = [
            ("openapi.json", "openapi.yaml", "openapi.yml"),
            ("swagger.json", "swagger.yaml", "swagger.yml"),
            ("**/openapi.json", "**/openapi.yaml", "**/openapi.yml"),
            ("**/swagger.json", "**/swagger.yaml", "**/swagger.yml"),
        ]
        
        for patterns in spec_patterns:
            for pattern in patterns:
                files = self.find_files(pattern)
                if files:
                    # Prefer root-level files
                    root_files = [f for f in files if f.parent == self.repo_path]
                    return root_files[0] if root_files else files[0]
        
        return None
    
    def _load_spec(self, spec_file: Path) -> Dict[str, Any]:
        """Load and parse OpenAPI specification."""
        content = self.read_file(spec_file)
        
        if spec_file.suffix == ".json":
            return json.loads(content)
        else:  # YAML
            return yaml.safe_load(content)
    
    def _parse_spec(self, spec: Dict[str, Any]) -> ApiCollection:
        """Parse OpenAPI specification into ApiCollection."""
        # Extract basic info
        info = spec.get("info", {})
        servers = spec.get("servers", [])
        base_url = servers[0]["url"] if servers else None
        
        collection = ApiCollection(
            name=info.get("title", "API"),
            description=info.get("description"),
            version=info.get("version"),
            base_url=base_url
        )
        
        # Extract global auth
        security_schemes = spec.get("components", {}).get("securitySchemes", {})
        if security_schemes:
            collection.auth_config = security_schemes
        
        # Parse paths
        paths = spec.get("paths", {})
        for path, path_item in paths.items():
            # Handle path-level parameters
            path_params = path_item.get("parameters", [])
            
            for method, operation in path_item.items():
                if method in ["get", "post", "put", "patch", "delete", "head", "options"]:
                    endpoint = self._parse_operation(path, method.upper(), operation, path_params)
                    collection.endpoints.append(endpoint)
        
        return collection
    
    def _parse_operation(self, path: str, method: str, operation: Dict[str, Any], 
                        path_params: List[Dict[str, Any]]) -> ApiEndpoint:
        """Parse an operation into ApiEndpoint."""
        endpoint = ApiEndpoint(
            path=path,
            method=HttpMethod(method),
            name=operation.get("operationId", operation.get("summary", f"{method} {path}")),
            description=operation.get("description", operation.get("summary")),
            tags=operation.get("tags", [])
        )
        
        # Parse parameters
        all_params = path_params + operation.get("parameters", [])
        for param in all_params:
            api_param = ApiParameter(
                name=param["name"],
                location=ParameterLocation(param["in"]),
                required=param.get("required", False),
                description=param.get("description"),
                type=param.get("schema", {}).get("type") if "schema" in param else param.get("type"),
                default=param.get("schema", {}).get("default") if "schema" in param else param.get("default"),
                example=param.get("example")
            )
            endpoint.parameters.append(api_param)
        
        # Parse request body
        if "requestBody" in operation:
            endpoint.request_body = operation["requestBody"]
        
        # Parse responses
        responses = operation.get("responses", {})
        for status_code, response in responses.items():
            if status_code.startswith("2"):  # Success responses
                example = {
                    "status": status_code,
                    "description": response.get("description", ""),
                    "content": response.get("content", {})
                }
                endpoint.response_examples.append(example)
        
        # Check for security requirements
        if "security" in operation:
            endpoint.auth_required = True
            if operation["security"]:
                endpoint.auth_type = list(operation["security"][0].keys())[0]
        
        return endpoint