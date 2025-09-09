"""
Postman collection generator from API endpoints.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
from ..models.api import ApiCollection, ApiEndpoint, HttpMethod, ParameterLocation
from ..models.postman import (
    PostmanCollection, PostmanInfo, PostmanItem, PostmanRequest,
    PostmanUrl, PostmanHeader, PostmanQueryParam, PostmanBody,
    PostmanAuth, PostmanResponse
)
from rich.console import Console

console = Console(stderr=True)


class PostmanCollectionGenerator:
    """Generator for Postman collections from API endpoint data."""
    
    def __init__(self, output_directory: Optional[str] = None):
        self.output_directory = Path(output_directory or os.environ.get("output_directory", "."))
        self.output_directory.mkdir(parents=True, exist_ok=True)
    
    def generate(self, api_collection: ApiCollection, repo_name: str) -> Path:
        """
        Generate a Postman collection from API endpoints.
        
        Args:
            api_collection: Collection of API endpoints
            repo_name: Repository name for file naming
            
        Returns:
            Path to the generated collection file
        """
        console.print(f"[blue]Generating Postman collection for {repo_name}[/blue]")
        
        # Create Postman collection
        postman_collection = self._create_collection(api_collection, repo_name)
        
        # Group endpoints by tags or paths
        grouped_items = self._group_endpoints(api_collection.endpoints)
        
        # Convert endpoints to Postman items
        for group_name, endpoints in grouped_items.items():
            if len(grouped_items) > 1:  # Create folders only if multiple groups
                folder = PostmanItem(
                    name=group_name,
                    description=f"Endpoints for {group_name}",
                    item=[]
                )
                for endpoint in endpoints:
                    item = self._create_postman_item(endpoint, api_collection.base_url)
                    folder.item.append(item)
                postman_collection.item.append(folder)
            else:
                # Add items directly to collection
                for endpoint in endpoints:
                    item = self._create_postman_item(endpoint, api_collection.base_url)
                    postman_collection.item.append(item)
        
        # Add global auth if configured
        if api_collection.auth_config:
            postman_collection.auth = self._create_auth_config(api_collection.auth_config)
        
        # Save collection
        output_path = self._save_collection(postman_collection, repo_name)
        
        console.print(f"[green]✓ Generated Postman collection: {output_path}[/green]")
        console.print(f"[green]  - {len(api_collection.endpoints)} endpoints[/green]")
        console.print(f"[green]  - {len(grouped_items)} groups[/green]")
        
        return output_path
    
    def _create_collection(self, api_collection: ApiCollection, repo_name: str) -> PostmanCollection:
        """Create base Postman collection structure."""
        return PostmanCollection(
            info=PostmanInfo(
                name=api_collection.name or repo_name,
                description=api_collection.description or f"API collection for {repo_name}"
            ),
            variable=[
                {
                    "key": "baseUrl",
                    "value": api_collection.base_url or "http://localhost:8000",
                    "type": "string"
                }
            ]
        )
    
    def _group_endpoints(self, endpoints: List[ApiEndpoint]) -> Dict[str, List[ApiEndpoint]]:
        """Group all endpoints into a single collection folder."""
        # Put all endpoints in a single group - no sub-folders
        groups = {
            "endpoints": endpoints
        }
        return groups
    
    def _create_postman_item(self, endpoint: ApiEndpoint, base_url: Optional[str]) -> PostmanItem:
        """Convert an API endpoint to a Postman item."""
        # Create URL
        url = self._create_url(endpoint, base_url)
        
        # Create headers
        headers = self._create_headers(endpoint)
        
        # Create body if needed
        body = self._create_body(endpoint)
        
        # Create request
        request = PostmanRequest(
            method=endpoint.method.value,
            header=headers,
            body=body,
            url=url,
            description=endpoint.description
        )
        
        # Add auth if specified
        if endpoint.auth_required and endpoint.auth_type:
            request.auth = self._create_endpoint_auth(endpoint.auth_type)
        
        # Create item
        item = PostmanItem(
            name=endpoint.name or f"{endpoint.method.value} {endpoint.path}",
            request=request,
            response=self._create_responses(endpoint)
        )
        
        # Add source file info as description if available
        if endpoint.source_file:
            source_info = f"\n\nSource: {endpoint.source_file}"
            if endpoint.line_number:
                source_info += f":{endpoint.line_number}"
            item.description = (item.description or "") + source_info
        
        return item
    
    def _create_url(self, endpoint: ApiEndpoint, base_url: Optional[str]) -> PostmanUrl:
        """Create Postman URL structure."""
        # Use variable for base URL and replace path variables with examples
        raw_url = "{{baseUrl}}" + endpoint.path
        url_path = endpoint.path
        
        # Replace path variables with examples for better readability
        for param in endpoint.parameters:
            if param.location == ParameterLocation.PATH:
                placeholder = "{" + param.name + "}"
                example_value = param.example or "1" if param.name == "id" else f"example_{param.name}"
                # Keep the placeholder in raw URL for Postman variables
                # But we can add a comment or description
                pass
        
        # Extract query parameters
        query_params = []
        for param in endpoint.parameters:
            if param.location == ParameterLocation.QUERY:
                query_param = PostmanQueryParam(
                    key=param.name,
                    value=str(param.example) if param.example else "",
                    description=param.description,
                    disabled=not param.required  # Enable required params, disable optional ones
                )
                query_params.append(query_param)
        
        # Create path segments (keep placeholders for Postman)
        path_segments = url_path.strip("/").split("/") if url_path != "/" else []
        
        return PostmanUrl(
            raw=raw_url,
            host=["{{baseUrl}}"],
            path=path_segments,
            query=query_params if query_params else None
        )
    
    def _create_headers(self, endpoint: ApiEndpoint) -> List[PostmanHeader]:
        """Create headers for the request."""
        headers = []
        
        # Add common headers based on method
        if endpoint.method in [HttpMethod.POST, HttpMethod.PUT, HttpMethod.PATCH]:
            headers.append(PostmanHeader(
                key="Content-Type",
                value="application/json"
            ))
        
        # Add header parameters
        for param in endpoint.parameters:
            if param.location == ParameterLocation.HEADER:
                headers.append(PostmanHeader(
                    key=param.name,
                    value=str(param.example) if param.example else "",
                    disabled=not param.required
                ))
        
        return headers
    
    def _create_body(self, endpoint: ApiEndpoint) -> Optional[PostmanBody]:
        """Create request body if needed."""
        if endpoint.request_body:
            # Handle our Spring Boot analyzer format
            if isinstance(endpoint.request_body, dict) and "example" in endpoint.request_body:
                example = endpoint.request_body["example"]
                return PostmanBody(
                    mode="raw",
                    raw=json.dumps(example, indent=2),
                    options={"raw": {"language": "json"}}
                )
            
            # Handle OpenAPI format
            content = endpoint.request_body.get("content", {})
            json_content = content.get("application/json", {})
            
            example = json_content.get("example", {})
            if not example:
                schema = json_content.get("schema", {})
                example = self._generate_example_from_schema(schema)
            
            return PostmanBody(
                mode="raw",
                raw=json.dumps(example, indent=2),
                options={"raw": {"language": "json"}}
            )
        
        # Check for body parameters
        body_params = [p for p in endpoint.parameters if p.location == ParameterLocation.BODY]
        if body_params:
            example = {param.name: param.example or f"<{param.type or 'string'}>" 
                      for param in body_params}
            return PostmanBody(
                mode="raw",
                raw=json.dumps(example, indent=2),
                options={"raw": {"language": "json"}}
            )
        
        return None
    
    def _create_responses(self, endpoint: ApiEndpoint) -> List[PostmanResponse]:
        """Create example responses."""
        responses = []
        
        for example in endpoint.response_examples:
            response = PostmanResponse(
                name=f"Success {example.get('status', '200')}",
                status=example.get('description', 'OK'),
                code=int(example.get('status', 200)),
                header=[],
                body=json.dumps(example.get('content', {}), indent=2) if example.get('content') else None
            )
            responses.append(response)
        
        return responses
    
    def _create_auth_config(self, auth_config: Dict[str, Any]) -> Optional[PostmanAuth]:
        """Create authentication configuration."""
        # Handle common auth types
        for scheme_name, scheme_config in auth_config.items():
            auth_type = scheme_config.get("type", "").lower()
            
            if auth_type == "http":
                sub_scheme = scheme_config.get("scheme", "").lower()
                if sub_scheme == "bearer":
                    return PostmanAuth(
                        type="bearer",
                        bearer=[{"key": "token", "value": "{{bearerToken}}", "type": "string"}]
                    )
                elif sub_scheme == "basic":
                    return PostmanAuth(
                        type="basic",
                        basic=[
                            {"key": "username", "value": "{{username}}", "type": "string"},
                            {"key": "password", "value": "{{password}}", "type": "string"}
                        ]
                    )
            elif auth_type == "apikey":
                return PostmanAuth(
                    type="apikey",
                    apikey=[
                        {"key": "key", "value": scheme_config.get("name", "api_key"), "type": "string"},
                        {"key": "value", "value": "{{apiKey}}", "type": "string"},
                        {"key": "in", "value": scheme_config.get("in", "header"), "type": "string"}
                    ]
                )
        
        return None
    
    def _create_endpoint_auth(self, auth_type: str) -> PostmanAuth:
        """Create endpoint-specific auth configuration."""
        # Map auth type to Postman auth
        if "bearer" in auth_type.lower():
            return PostmanAuth(
                type="bearer",
                bearer=[{"key": "token", "value": "{{bearerToken}}", "type": "string"}]
            )
        elif "basic" in auth_type.lower():
            return PostmanAuth(
                type="basic",
                basic=[
                    {"key": "username", "value": "{{username}}", "type": "string"},
                    {"key": "password", "value": "{{password}}", "type": "string"}
                ]
            )
        else:
            # Default to API key
            return PostmanAuth(
                type="apikey",
                apikey=[
                    {"key": "key", "value": "api_key", "type": "string"},
                    {"key": "value", "value": "{{apiKey}}", "type": "string"},
                    {"key": "in", "value": "header", "type": "string"}
                ]
            )
    
    def _generate_example_from_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate example data from JSON schema."""
        if not schema or not isinstance(schema, dict):
            return {}
        
        schema_type = schema.get("type", "object")
        
        if schema_type == "object":
            example = {}
            properties = schema.get("properties", {})
            for prop_name, prop_schema in properties.items():
                example[prop_name] = self._generate_example_from_schema(prop_schema)
            return example
        elif schema_type == "array":
            item_schema = schema.get("items", {})
            return [self._generate_example_from_schema(item_schema)]
        elif schema_type == "string":
            return schema.get("example", "string")
        elif schema_type == "number":
            return schema.get("example", 0)
        elif schema_type == "integer":
            return schema.get("example", 0)
        elif schema_type == "boolean":
            return schema.get("example", True)
        else:
            return None
    
    def _save_collection(self, collection: PostmanCollection, repo_name: str) -> Path:
        """Save Postman collection to file."""
        # Sanitize filename
        safe_name = "".join(c for c in repo_name if c.isalnum() or c in "-_")
        filename = f"{safe_name}_postman_collection.json"
        output_path = self.output_directory / filename
        
        # Convert to dict and save
        collection_dict = collection.model_dump(by_alias=True, exclude_none=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(collection_dict, f, indent=2, ensure_ascii=False)
        
        return output_path