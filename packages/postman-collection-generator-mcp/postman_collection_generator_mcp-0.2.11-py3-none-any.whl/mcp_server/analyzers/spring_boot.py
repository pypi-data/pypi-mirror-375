"""
Spring Boot framework analyzer using pattern matching and simple parsing.
"""
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..models.api import ApiCollection, ApiEndpoint, ApiParameter, HttpMethod, ParameterLocation
from .base import BaseAnalyzer
from rich.console import Console

console = Console(stderr=True)


class SpringBootAnalyzer(BaseAnalyzer):
    """Analyzer for Spring Boot applications."""
    
    def can_analyze(self) -> bool:
        """Check if this is a Spring Boot project."""
        # Check for Spring Boot indicators
        indicators = [
            "pom.xml",
            "build.gradle",
            "src/main/java/**/*Application.java",
            "src/main/java/**/*Controller.java",
            "**/controller/*.java",
            "**/controllers/*.java"
        ]
        
        for pattern in indicators:
            if self.find_files(pattern):
                return True
                
        # Check for Spring Boot content in files
        for file in self.find_files("**/*.java"):
            content = self.read_file(file)
            if any(annotation in content for annotation in [
                "@SpringBootApplication", "@RestController", "@Controller",
                "@RequestMapping", "@GetMapping", "@PostMapping"
            ]):
                return True
        
        return False
    
    def analyze(self) -> ApiCollection:
        """Extract endpoints from Spring Boot application."""
        collection = ApiCollection(
            name=self.repo_path.name,
            description="Spring Boot Application"
        )
        
        # Find all Java controller files
        controller_patterns = [
            "**/controller/*.java",
            "**/controllers/*.java", 
            "**/*Controller.java"
        ]
        
        controller_files = []
        for pattern in controller_patterns:
            controller_files.extend(self.find_files(pattern))
        
        # Remove duplicates
        controller_files = list(set(controller_files))
        
        for controller_file in controller_files:
            try:
                endpoints = self._analyze_controller(controller_file)
                collection.endpoints.extend(endpoints)
            except Exception as e:
                console.print(f"[yellow]Warning: Failed to analyze {controller_file}: {e}[/yellow]")
        
        console.print(f"[green]Extracted {len(collection.endpoints)} endpoints from Spring Boot app[/green]")
        return collection
    
    def _analyze_controller(self, file_path: Path) -> List[ApiEndpoint]:
        """Analyze a single Java controller file."""
        content = self.read_file(file_path)
        if not content:
            return []
        
        endpoints = []
        
        # Extract class-level RequestMapping (handle both value= and direct string)
        class_path = ""
        class_mapping_patterns = [
            r'@RequestMapping\s*\(\s*(?:value\s*=\s*)?["\']([^"\']*)["\']',  # With or without value=
            r'@RequestMapping\s*\(\s*path\s*=\s*["\']([^"\']*)["\']',        # With path=
        ]
        
        for pattern in class_mapping_patterns:
            class_mapping_match = re.search(pattern, content)
            if class_mapping_match:
                class_path = class_mapping_match.group(1)
                break
        
        # Find all method mappings - non-overlapping patterns
        method_patterns = [
            # Single comprehensive pattern for each HTTP method
            (r'@GetMapping\s*(?:\(\s*(?:value\s*=\s*|path\s*=\s*)?["\']([^"\']*)["\'][^)]*\))?[\s\S]*?public\s+[\w<>.,\s]+\s+(\w+)\s*\(', 'GET'),
            (r'@PostMapping\s*(?:\(\s*(?:value\s*=\s*|path\s*=\s*)?["\']([^"\']*)["\'][^)]*\))?[\s\S]*?public\s+[\w<>.,\s]+\s+(\w+)\s*\(', 'POST'),
            (r'@PutMapping\s*(?:\(\s*(?:value\s*=\s*|path\s*=\s*)?["\']([^"\']*)["\'][^)]*\))?[\s\S]*?public\s+[\w<>.,\s]+\s+(\w+)\s*\(', 'PUT'),
            (r'@DeleteMapping\s*(?:\(\s*(?:value\s*=\s*|path\s*=\s*)?["\']([^"\']*)["\'][^)]*\))?[\s\S]*?public\s+[\w<>.,\s]+\s+(\w+)\s*\(', 'DELETE'),
            (r'@PatchMapping\s*(?:\(\s*(?:value\s*=\s*|path\s*=\s*)?["\']([^"\']*)["\'][^)]*\))?[\s\S]*?public\s+[\w<>.,\s]+\s+(\w+)\s*\(', 'PATCH'),
        ]
        
        # Track unique endpoints to avoid duplicates
        seen_endpoints = set()
        
        for pattern, http_method in method_patterns:
            matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
            for match in matches:
                # Extract path and method name
                if match.group(1) is not None:
                    # Pattern with path: @GetMapping("/path") or @GetMapping(path="/path")
                    path = match.group(1)
                    method_name = match.group(2)
                else:
                    # Pattern without path: @GetMapping (no parentheses)
                    path = ""
                    method_name = match.group(2)
                
                method = http_method
                
                # Combine class path and method path properly
                if path:
                    if path.startswith('/'):
                        full_path = path  # Absolute path, ignore class path
                    else:
                        # Relative path, combine with class path
                        full_path = (class_path.rstrip('/') + '/' + path.lstrip('/')).replace('//', '/')
                else:
                    full_path = class_path or "/"
                
                if not full_path.startswith('/'):
                    full_path = '/' + full_path
                
                # Create unique identifier for deduplication
                endpoint_key = (full_path, method, method_name)
                if endpoint_key in seen_endpoints:
                    continue  # Skip duplicate
                seen_endpoints.add(endpoint_key)
                
                endpoint = ApiEndpoint(
                    path=full_path,
                    method=HttpMethod(method),
                    name=method_name or f"{method} {full_path}",
                    source_file=str(file_path.relative_to(self.repo_path)),
                    line_number=content[:match.start()].count('\n') + 1
                )
                
                # Extract parameters
                self._extract_parameters(content, match, endpoint)
                
                endpoints.append(endpoint)
        
        # Also handle simple @RequestMapping without explicit method
        simple_mapping_patterns = [
            r'@RequestMapping\s*\(\s*(?:value\s*=\s*|path\s*=\s*)?["\']([^"\']*)["\'][\s\S]*?public\s+[\w<>.,\s]+\s+(\w+)\s*\([^)]*\)',
            r'@RequestMapping\s*\(\s*["\']([^"\']*)["\'][\s\S]*?public\s+[\w<>.,\s]+\s+(\w+)\s*\([^)]*\)'
        ]
        
        for simple_pattern in simple_mapping_patterns:
            for match in re.finditer(simple_pattern, content, re.MULTILINE | re.DOTALL):
                path = match.group(1)
                method_name = match.group(2)
                
                full_path = (class_path.rstrip('/') + '/' + path.lstrip('/')).replace('//', '/')
                if not full_path.startswith('/'):
                    full_path = '/' + full_path
                
                # Apply same deduplication logic
                endpoint_key = (full_path, "GET", method_name)
                if endpoint_key in seen_endpoints:
                    continue  # Skip duplicate
                seen_endpoints.add(endpoint_key)
                
                endpoint = ApiEndpoint(
                    path=full_path,
                    method=HttpMethod.GET,  # Default to GET
                    name=method_name,
                    source_file=str(file_path.relative_to(self.repo_path)),
                    line_number=content[:match.start()].count('\n') + 1
                )
                
                self._extract_parameters(content, match, endpoint)
                endpoints.append(endpoint)
        
        return endpoints
    
    def _extract_method_name_from_context(self, content: str, position: int) -> Optional[str]:
        """Extract method name from the context around a match."""
        # Look for method declaration after the annotation
        after_match = content[position:]
        method_match = re.search(r'public\s+\w+\s+(\w+)\s*\(', after_match)
        return method_match.group(1) if method_match else None
    
    def _extract_parameters(self, content: str, match: re.Match, endpoint: ApiEndpoint):
        """Extract parameters from method signature and annotations."""
        # Get the full method signature - look for more content
        method_start = match.start()
        method_end = self._find_method_end(content, match.end())
        method_content = content[method_start:method_end]
        
        # Debug output (commenting out to avoid MCP protocol interference)
        # console.print(f"[blue]Analyzing method: {endpoint.name}[/blue]")
        # console.print(f"[blue]Method content preview: {method_content[:200]}...[/blue]")
        
        # Extract path variables from URL and add them as parameters
        path_vars = re.findall(r'\{(\w+)\}', endpoint.path)
        for var in path_vars:
            param = ApiParameter(
                name=var,
                location=ParameterLocation.PATH,
                required=True,
                type="integer" if var == "id" else "string",
                example="1" if var == "id" else f"example_{var}"
            )
            endpoint.parameters.append(param)
        
        # Extract @RequestHeader parameters
        header_patterns = [
            r'@RequestHeader\s*\(\s*value\s*=\s*["\']([^"\']*)["\'][^)]*(?:required\s*=\s*(true|false))?[^)]*\)\s+(?:\w+\s+)*?(\w+)',
            r'@RequestHeader\s*\(\s*["\']([^"\']*)["\'][^)]*(?:required\s*=\s*(true|false))?[^)]*\)\s+(?:\w+\s+)*?(\w+)',
            r'@RequestHeader\s+(?:\w+\s+)*?(\w+)'  # Simple @RequestHeader without parentheses
        ]
        
        for pattern in header_patterns:
            matches = list(re.finditer(pattern, method_content, re.IGNORECASE))
            for match in matches:
                if len(match.groups()) >= 3:
                    header_name = match.group(1)
                    required_str = match.group(2) if len(match.groups()) > 2 and match.group(2) else None
                    param_name = match.group(3)
                    required = required_str != "false" if required_str else True
                elif len(match.groups()) == 1:
                    header_name = match.group(1)
                    param_name = match.group(1)
                    required = True
                else:
                    continue
                
                param = ApiParameter(
                    name=header_name,
                    location=ParameterLocation.HEADER,
                    required=required,
                    type="string",
                    example=self._generate_header_example(header_name)
                )
                endpoint.parameters.append(param)
        
        # More flexible parameter extraction patterns (excluding @RequestBody which is handled separately)
        param_patterns = [
            # @RequestParam patterns (look for any parameters after @RequestParam)
            r'@RequestParam\s*(?:\([^)]*\))?\s+(?:\w+\s+)*?(\w+)\s+(\w+)',
            # @PathVariable patterns  
            r'@PathVariable\s*(?:\([^)]*\))?\s+(?:\w+\s+)*?(\w+)\s+(\w+)',
            # @RequestHeader patterns
            r'@RequestHeader\s*(?:\([^)]*\))?\s+(?:\w+\s+)*?(\w+)\s+(\w+)',
        ]
        
        # Enhanced @RequestBody patterns to handle List<Type> and modifiers correctly
        request_body_patterns = [
            # @NotNull @RequestBody final List<Type> name - extract inner type from List
            r'@NotNull\s+@RequestBody\s+final\s+List<([A-Z]\w*(?:\.\w+)*)>\s+(\w+)',
            # @NotNull @RequestBody List<Type> name - extract inner type from List
            r'@NotNull\s+@RequestBody\s+List<([A-Z]\w*(?:\.\w+)*)>\s+(\w+)',
            # @RequestBody final List<Type> name - extract inner type from List
            r'@RequestBody\s+final\s+List<([A-Z]\w*(?:\.\w+)*)>\s+(\w+)',
            # @RequestBody List<Type> name - extract inner type from List
            r'@RequestBody\s+List<([A-Z]\w*(?:\.\w+)*)>\s+(\w+)',
            # @RequestBody @Valid List<Type> name
            r'@RequestBody\s+@Valid\s+List<([A-Z]\w*(?:\.\w+)*)>\s+(\w+)',
            # @Valid @RequestBody List<Type> name  
            r'@Valid\s+@RequestBody\s+List<([A-Z]\w*(?:\.\w+)*)>\s+(\w+)',
            # @NotNull @RequestBody final Type name - single object
            r'@NotNull\s+@RequestBody\s+final\s+([A-Z]\w*(?:\.\w+)*)\s+(\w+)',
            # @NotNull @RequestBody Type name - single object
            r'@NotNull\s+@RequestBody\s+([A-Z]\w*(?:\.\w+)*)\s+(\w+)',
            # @RequestBody final Type name - single object
            r'@RequestBody\s+final\s+([A-Z]\w*(?:\.\w+)*)\s+(\w+)',
            # @RequestBody @Valid Type name - single object
            r'@RequestBody\s+@Valid\s+([A-Z]\w*(?:\.\w+)*)\s+(\w+)',
            # @RequestBody @Validated Type name - single object
            r'@RequestBody\s+@Validated\s+([A-Z]\w*(?:\.\w+)*)\s+(\w+)',
            # @Valid @RequestBody Type name - single object
            r'@Valid\s+@RequestBody\s*(?:\([^)]*\))?\s+([A-Z]\w*(?:\.\w+)*)\s+(\w+)',
            # @Validated @RequestBody Type name - single object
            r'@Validated\s+@RequestBody\s*(?:\([^)]*\))?\s+([A-Z]\w*(?:\.\w+)*)\s+(\w+)',
            # @RequestBody Type name (no validation) - single object, skip modifiers
            r'@RequestBody\s*(?:\([^)]*\))?\s+(?:final\s+)?([A-Z]\w*(?:\.\w+)*)\s+(\w+)'
        ]
        
        request_body_matches = []
        for pattern_index, pattern in enumerate(request_body_patterns):
            matches = list(re.finditer(pattern, method_content, re.IGNORECASE))
            if matches:
                # Add pattern index to identify List vs single object patterns
                for match in matches:
                    request_body_matches.append((match, pattern_index))
                break  # Stop at first successful pattern
        
        for match, pattern_index in request_body_matches:
            param_type_raw = match.group(1)
            param_name = match.group(2)
            
            # Detect if this is a List<Type> pattern (first 6 patterns are List types)
            is_list_type = pattern_index < 6
            
            # Try to find and parse the actual DTO class
            dto_example = self._parse_dto_class(param_type_raw)
            
            if dto_example and isinstance(dto_example, dict) and dto_example:
                # Use parsed DTO structure
                if is_list_type:
                    example_data = [dto_example]  # Wrap in array for List<Type>
                    type_info = f"List<{param_type_raw}>"
                else:
                    example_data = dto_example  # Single object
                    type_info = param_type_raw
                console.print(f"[green]Successfully parsed DTO {param_type_raw} with {len(dto_example)} fields[/green]")
            else:
                # Fallback to generated example
                console.print(f"[yellow]DTO parsing failed for {param_type_raw}, using fallback[/yellow]")
                fallback_example = self._generate_example_for_type(param_type_raw)
                if is_list_type:
                    example_data = [fallback_example]  # Wrap in array for List<Type>
                    type_info = f"List<{param_type_raw}>"
                else:
                    example_data = fallback_example  # Single object
                    type_info = param_type_raw
            
            # Create request body schema
            endpoint.request_body = {
                "type": type_info,
                "example": example_data
            }
        
        # Look for @RequestParam
        query_param_pattern = r'@RequestParam\s*(?:\([^)]*\))?\s+(?:\w+\s+)*?(\w+)\s+(\w+)'
        query_matches = list(re.finditer(query_param_pattern, method_content, re.IGNORECASE))
        
        for match in query_matches:
            param_type_raw = match.group(1)
            param_name = match.group(2)
            # console.print(f"[green]Found query param: {param_type_raw} {param_name}[/green]")
            
            param_type = self._convert_java_type(param_type_raw)
            param = ApiParameter(
                name=param_name,
                location=ParameterLocation.QUERY,
                required=False,
                type=param_type,
                example=self._generate_simple_example(param_type)
            )
            endpoint.parameters.append(param)
    
    def _find_method_end(self, content: str, start_pos: int) -> int:
        """Find the end of a method by counting braces."""
        brace_count = 0
        pos = start_pos
        in_method_body = False
        
        while pos < len(content):
            char = content[pos]
            if char == '{':
                brace_count += 1
                in_method_body = True
            elif char == '}':
                brace_count -= 1
                if in_method_body and brace_count == 0:
                    return pos + 1
            pos += 1
        
        # Fallback to a reasonable limit
        return min(start_pos + 2000, len(content))
    
    def _convert_java_type(self, java_type: str) -> str:
        """Convert Java types to standard parameter types."""
        type_mapping = {
            "String": "string",
            "Integer": "integer", 
            "int": "integer",
            "Long": "integer",
            "long": "integer", 
            "Boolean": "boolean",
            "boolean": "boolean",
            "Double": "number",
            "double": "number",
            "Float": "number", 
            "float": "number",
            "List": "array",
            "ArrayList": "array",
            "Set": "array",
            "Map": "object"
        }
        
        # Handle generic types like List<String>
        base_type = java_type.split('<')[0].split('.')[-1]  # Get last part after dot
        return type_mapping.get(base_type, "string")
    
    def _generate_example_for_type(self, java_type: str) -> dict:
        """Generate example request body based on Java type."""
        # This is a simplified example generator
        # In a real implementation, you might want to parse the actual DTO classes
        
        type_name = java_type.split('.')[-1]  # Get class name
        
        # Common DTO patterns
        if "Request" in type_name or "Create" in type_name or "Update" in type_name:
            if "Login" in type_name:
                return {
                    "username": "example@email.com",
                    "password": "password123"
                }
            elif "User" in type_name:
                example = {
                    "name": "John Doe",
                    "email": "john@example.com"
                }
                if "Create" in type_name:
                    example["password"] = "password123"
                return example
            elif "Game" in type_name:
                return {
                    "name": "Poker Game",
                    "buyIn": 100.0,
                    "gameType": "CASH"
                }
            elif "CreditTransfer" in type_name:
                return {
                    "amount": 1000.00,
                    "payeeName": "John Doe",
                    "payeeAccountNumber": "1234567890",
                    "narrative": "Payment description"
                }
            elif "ProxyResolution" in type_name:
                return {
                    "proxyId": "example@email.com",
                    "proxyType": "EMAIL",
                    "bankCode": "001"
                }
            elif "Token" in type_name:
                return {
                    "tokenType": "OTP",
                    "purpose": "transaction_verification"
                }
            elif "Transaction" in type_name:
                return {
                    "profileId": "12345",
                    "startDate": "2024-01-01",
                    "endDate": "2024-01-31"
                }
            else:
                return {
                    "example": f"Replace with actual {type_name} structure"
                }
        
        return {"data": f"Example {type_name}"}
    
    def _generate_simple_example(self, param_type: str) -> str:
        """Generate simple examples for parameters."""
        examples = {
            "string": "example",
            "integer": "1",
            "number": "1.0", 
            "boolean": "true",
            "array": "value1,value2"
        }
        return examples.get(param_type, "example")
    
    def _generate_header_example(self, header_name: str) -> str:
        """Generate example values for common headers."""
        header_examples = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-API-Key": "your-api-key-here",
            "User-Agent": "PostmanRuntime/7.28.0",
            "Profile-Id": "12345",
            "Channel": "SMARTAPP",
            "Step-Up-Token": "token123",
            "msisdn": "+27821234567"
        }
        return header_examples.get(header_name, "example-value")
    
    def _parse_dto_class(self, class_name: str) -> Optional[dict]:
        """Parse a DTO class from the codebase to generate accurate examples."""
        try:
            # Remove package prefix if present (e.g., "final String" -> "String")
            clean_class_name = class_name.split('.')[-1] if '.' in class_name else class_name
            
            # Comprehensive DTO search patterns in Spring Boot projects
            search_patterns = [
                f"**/{clean_class_name}.java",
                f"**/dto/**/{clean_class_name}.java", 
                f"**/dto/{clean_class_name}.java",
                f"**/model/**/{clean_class_name}.java",
                f"**/domain/**/{clean_class_name}.java",
                f"**/entity/**/{clean_class_name}.java",
                f"**/request/**/{clean_class_name}.java",
                f"**/response/**/{clean_class_name}.java",
                f"**/bean/**/{clean_class_name}.java",
                f"**/beans/**/{clean_class_name}.java",
                f"**/vo/**/{clean_class_name}.java",
                f"**/pojo/**/{clean_class_name}.java",
                f"src/main/java/**/{clean_class_name}.java",
                f"src/**/java/**/{clean_class_name}.java"
            ]
            
            dto_file_path = None
            for pattern in search_patterns:
                files = list(self.repo_path.glob(pattern))
                if files:
                    dto_file_path = files[0]
                    console.print(f"[green]Found DTO class {clean_class_name} at {dto_file_path}[/green]")
                    break
            
            if not dto_file_path:
                console.print(f"[yellow]DTO class {clean_class_name} not found in codebase. Searched patterns: {search_patterns}[/yellow]")
                return None
            
            dto_content = self.read_file(dto_file_path)
            if not dto_content:
                return None
            
            return self._parse_java_class_fields(dto_content, clean_class_name)
            
        except Exception as e:
            console.print(f"[yellow]Error parsing DTO class {class_name}: {e}[/yellow]")
            return None
    
    def _parse_java_class_fields(self, class_content: str, class_name: str) -> dict:
        """Parse Java class fields and generate example JSON."""
        example = {}
        
        console.print(f"[cyan]Parsing fields for {class_name}...[/cyan]")
        console.print(f"[cyan]Class content preview: {class_content[:200]}...[/cyan]")
        
        # Extract field declarations - comprehensive patterns for better parsing
        field_patterns = [
            # Multi-line validation patterns - handle @NotNull, @Valid, etc. on separate lines
            r'@(?:NotNull|NotEmpty|Valid|NotBlank|DecimalMin|Digits|Pattern)[^\n]*\n\s*private\s+(\w+(?:\.\w+)*(?:<[^>]+>)?)\s+(\w+)\s*;',
            # @JsonProperty annotated fields 
            r'@JsonProperty[^\n]*\n\s*private\s+(\w+(?:\.\w+)*(?:<[^>]+>)?)\s+(\w+)\s*;',
            # Standard private fields with full package names
            r'private\s+(\w+(?:\.\w+)*(?:<[^>]+>)?)\s+(\w+)\s*;',
            # Public fields
            r'public\s+(\w+(?:\.\w+)*(?:<[^>]+>)?)\s+(\w+)\s*;',
            # Protected fields
            r'protected\s+(\w+(?:\.\w+)*(?:<[^>]+>)?)\s+(\w+)\s*;',
            # Package-private fields (no access modifier) - CRITICAL for FeeRequest
            r'^\s*([A-Z]\w*(?:\.\w+)*(?:<[^>]+>)?)\s+(\w+)\s*;',
            # Fields with modifiers like final
            r'(?:private|public|protected)\s+(?:final\s+)?(\w+(?:\.\w+)*(?:<[^>]+>)?)\s+(\w+)\s*;'
        ]
        
        total_matches = 0
        for pattern_idx, pattern in enumerate(field_patterns):
            matches = list(re.finditer(pattern, class_content, re.MULTILINE))
            if matches:
                console.print(f"[cyan]Pattern {pattern_idx} matched {len(matches)} fields: {pattern}[/cyan]")
                for match in matches:
                    field_type = match.group(1)
                    field_name = match.group(2)
                    console.print(f"[cyan]  Found field: {field_type} {field_name}[/cyan]")
                    
                    # Skip @JsonIgnore fields - check only if @JsonIgnore is directly on the field
                    field_context = self._get_field_context(class_content, match.start())
                    # Look for @JsonIgnore on the field specifically, not @JsonIgnoreProperties on class
                    if re.search(r'@JsonIgnore\s*\n\s*' + re.escape(field_type), field_context):
                        console.print(f"[cyan]  Skipping @JsonIgnore field: {field_name}[/cyan]")
                        continue
                    
                    # Generate example value based on field type and name
                    example[field_name] = self._generate_field_example(field_type, field_name, field_context)
                    total_matches += 1
        
        console.print(f"[cyan]Total fields parsed for {class_name}: {total_matches}[/cyan]")
        return example
    
    def _get_field_context(self, content: str, field_position: int) -> str:
        """Get the context around a field (annotations, etc.)."""
        # Look 200 characters before the field for annotations
        start = max(0, field_position - 200)
        context = content[start:field_position + 100]
        return context
    
    def _generate_field_example(self, field_type: str, field_name: str, context: str) -> any:
        """Generate example value for a specific field based on type and context."""
        field_name_lower = field_name.lower()
        
        # Handle primitive and common types with enhanced patterns
        if field_type in ['String', 'string']:
            if 'email' in field_name_lower:
                return "user@example.com"
            elif 'phone' in field_name_lower or 'mobile' in field_name_lower or 'cell' in field_name_lower:
                return "+27821234567"
            elif 'name' in field_name_lower:
                if 'account' in field_name_lower or 'bank' in field_name_lower:
                    return "Bank Account Name"
                elif 'branch' in field_name_lower:
                    return "Main Branch"
                else:
                    return "John Doe"
            elif 'reference' in field_name_lower:
                return "REF123456789"
            elif 'number' in field_name_lower:
                if 'account' in field_name_lower:
                    return "1234567890"
                elif 'branch' in field_name_lower:
                    return "001"
                else:
                    return "123456"
            elif 'token' in field_name_lower:
                return "token123456"
            elif 'id' in field_name_lower:
                if 'profile' in field_name_lower:
                    return "profile_12345"
                else:
                    return "12345"
            elif 'code' in field_name_lower:
                if 'bicfi' in field_name_lower or 'bic' in field_name_lower:
                    return "ABNANL2A"
                elif 'branch' in field_name_lower:
                    return "001"
                else:
                    return "CODE123"
            elif 'bicfi' in field_name_lower or 'bic' in field_name_lower:
                return "ABNANL2A"
            elif 'domain' in field_name_lower:
                return "bank.co.za"
            elif 'uetr' in field_name_lower:
                return "12345678-1234-1234-1234-123456789012"
            elif 'narrative' in field_name_lower or 'description' in field_name_lower:
                return "Payment description"
            else:
                return "example value"
        
        elif field_type in ['BigDecimal', 'Double', 'double', 'Float', 'float']:
            if 'amount' in field_name_lower:
                return 100.50
            else:
                return 1.0
        
        elif field_type in ['Integer', 'int', 'Long', 'long']:
            if 'id' in field_name_lower:
                return 12345
            elif 'number' in field_name_lower:
                return 123456
            else:
                return 1
        
        elif field_type in ['Boolean', 'boolean']:
            return True
        
        elif field_type.startswith('List<') or field_type.startswith('ArrayList<'):
            # Extract generic type
            generic_type = re.search(r'<([^>]+)>', field_type)
            if generic_type:
                inner_type = generic_type.group(1)
                return [self._generate_field_example(inner_type, field_name + "Item", context)]
            return ["example item"]
        
        elif field_type == 'Date' or field_type == 'LocalDate':
            return "2024-01-01"
        
        elif field_type == 'LocalDateTime' or field_type == 'DateTime':
            return "2024-01-01T10:30:00"
        
        # Handle enum types (try to find enum values)
        elif self._is_enum_type(field_type):
            enum_values = self._get_enum_values(field_type)
            return enum_values[0] if enum_values else "ENUM_VALUE"
        
        # For complex objects, try to parse recursively (simplified)
        else:
            return f"<{field_type} object>"
    
    def _is_enum_type(self, type_name: str) -> bool:
        """Check if a type is likely an enum."""
        # Look for enum files in the codebase
        enum_files = list(self.repo_path.glob(f"**/{type_name}.java"))
        for enum_file in enum_files:
            content = self.read_file(enum_file)
            if content and 'enum ' + type_name in content:
                return True
        return False
    
    def _get_enum_values(self, enum_type: str) -> List[str]:
        """Extract enum values from enum class."""
        enum_files = list(self.repo_path.glob(f"**/{enum_type}.java"))
        for enum_file in enum_files:
            content = self.read_file(enum_file)
            if content and 'enum ' + enum_type in content:
                # Simple enum value extraction
                enum_pattern = r'(\w+)\s*(?:\([^)]*\))?\s*[,;]'
                matches = re.findall(enum_pattern, content)
                # Filter out common non-enum words
                values = [m for m in matches if m.isupper() and len(m) > 1]
                return values[:3]  # Return first 3 values
        return []