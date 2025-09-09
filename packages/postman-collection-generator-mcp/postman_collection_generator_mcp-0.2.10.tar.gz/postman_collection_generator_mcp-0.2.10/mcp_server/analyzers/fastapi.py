"""
FastAPI framework analyzer using AST parsing.
"""
import ast
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from ..models.api import ApiCollection, ApiEndpoint, ApiParameter, HttpMethod, ParameterLocation
from .base import BaseAnalyzer
from rich.console import Console

console = Console()


class FastAPIAnalyzer(BaseAnalyzer):
    """Analyzer for FastAPI applications."""
    
    def can_analyze(self) -> bool:
        """Check if this is a FastAPI project."""
        # Check for FastAPI in requirements or imports
        patterns = ["requirements*.txt", "pyproject.toml", "setup.py", "**/*.py"]
        
        for pattern in patterns:
            for file in self.find_files(pattern):
                content = self.read_file(file)
                if "fastapi" in content.lower():
                    return True
        return False
    
    def analyze(self) -> ApiCollection:
        """Extract endpoints from FastAPI application."""
        collection = ApiCollection(
            name=self.repo_path.name,
            description="FastAPI Application"
        )
        
        # Find all Python files
        py_files = self.find_files("*.py")
        
        for py_file in py_files:
            try:
                endpoints = self._analyze_file(py_file)
                collection.endpoints.extend(endpoints)
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to analyze {py_file}: {e}[/yellow]")
        
        console.print(f"[green]Extracted {len(collection.endpoints)} endpoints from FastAPI app[/green]")
        return collection
    
    def _analyze_file(self, file_path: Path) -> List[ApiEndpoint]:
        """Analyze a single Python file for FastAPI routes."""
        content = self.read_file(file_path)
        if not content:
            return []
        
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return []
        
        endpoints = []
        
        # Find FastAPI app instance
        app_name = self._find_app_instance(tree)
        if not app_name:
            return []
        
        # Find route decorators
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                endpoint = self._extract_endpoint(node, app_name, file_path)
                if endpoint:
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _find_app_instance(self, tree: ast.AST) -> Optional[str]:
        """Find FastAPI app instance name."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if isinstance(node.value, ast.Call):
                    if hasattr(node.value.func, "id") and node.value.func.id == "FastAPI":
                        if node.targets and hasattr(node.targets[0], "id"):
                            return node.targets[0].id
                    elif hasattr(node.value.func, "attr") and node.value.func.attr == "FastAPI":
                        if node.targets and hasattr(node.targets[0], "id"):
                            return node.targets[0].id
        return None
    
    def _extract_endpoint(self, func_node: ast.FunctionDef, app_name: str, 
                         file_path: Path) -> Optional[ApiEndpoint]:
        """Extract endpoint information from a function definition."""
        # Look for route decorators
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call):
                if self._is_route_decorator(decorator, app_name):
                    return self._parse_route_decorator(decorator, func_node, file_path)
        return None
    
    def _is_route_decorator(self, decorator: ast.Call, app_name: str) -> bool:
        """Check if decorator is a FastAPI route decorator."""
        if hasattr(decorator.func, "attr"):
            attr = decorator.func.attr
            if attr in ["get", "post", "put", "patch", "delete", "head", "options"]:
                if hasattr(decorator.func.value, "id") and decorator.func.value.id == app_name:
                    return True
        return False
    
    def _parse_route_decorator(self, decorator: ast.Call, func_node: ast.FunctionDef,
                              file_path: Path) -> ApiEndpoint:
        """Parse route decorator to extract endpoint details."""
        # Extract method
        method = decorator.func.attr.upper()
        
        # Extract path
        path = "/"
        if decorator.args and isinstance(decorator.args[0], ast.Constant):
            path = decorator.args[0].value
        
        # Extract description from docstring
        description = ast.get_docstring(func_node)
        
        endpoint = ApiEndpoint(
            path=path,
            method=HttpMethod(method),
            name=func_node.name,
            description=description,
            source_file=str(file_path.relative_to(self.repo_path)),
            line_number=func_node.lineno
        )
        
        # Extract parameters from function signature
        self._extract_parameters(func_node, endpoint)
        
        # Extract tags from decorator
        for keyword in decorator.keywords:
            if keyword.arg == "tags" and isinstance(keyword.value, ast.List):
                endpoint.tags = [elt.value for elt in keyword.value.elts 
                               if isinstance(elt, ast.Constant)]
        
        return endpoint
    
    def _extract_parameters(self, func_node: ast.FunctionDef, endpoint: ApiEndpoint):
        """Extract parameters from function signature."""
        # Skip 'self' parameter if present
        args = func_node.args.args
        if args and args[0].arg in ["self", "cls"]:
            args = args[1:]
        
        # Extract path parameters from the path
        path_params = re.findall(r"\{(\w+)\}", endpoint.path)
        
        for arg in args:
            param_name = arg.arg
            
            # Determine parameter location
            if param_name in path_params:
                location = ParameterLocation.PATH
                required = True
            elif param_name in ["request", "response", "db"]:
                continue  # Skip FastAPI special parameters
            else:
                location = ParameterLocation.QUERY
                required = arg.annotation is not None
            
            # Extract type from annotation
            param_type = None
            if arg.annotation:
                param_type = self._annotation_to_string(arg.annotation)
            
            param = ApiParameter(
                name=param_name,
                location=location,
                required=required,
                type=param_type
            )
            endpoint.parameters.append(param)
    
    def _annotation_to_string(self, annotation: ast.AST) -> str:
        """Convert AST annotation to string representation."""
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Constant):
            return str(annotation.value)
        else:
            return "string"  # Default fallback