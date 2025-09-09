"""
Data models for API endpoint representation.
These models are framework-agnostic and represent discovered API endpoints.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class HttpMethod(str, Enum):
    """Supported HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class ParameterLocation(str, Enum):
    """Parameter location in request."""
    PATH = "path"
    QUERY = "query"
    HEADER = "header"
    BODY = "body"


class ApiParameter(BaseModel):
    """API parameter definition."""
    name: str
    location: ParameterLocation
    required: bool = False
    description: Optional[str] = None
    type: Optional[str] = None
    default: Optional[Any] = None
    example: Optional[Any] = None


class ApiEndpoint(BaseModel):
    """Represents a discovered API endpoint."""
    path: str
    method: HttpMethod
    name: Optional[str] = None
    description: Optional[str] = None
    parameters: List[ApiParameter] = Field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    response_examples: List[Dict[str, Any]] = Field(default_factory=list)
    auth_required: bool = False
    auth_type: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    source_file: Optional[str] = None
    line_number: Optional[int] = None


class ApiCollection(BaseModel):
    """Collection of discovered API endpoints."""
    name: str
    base_url: Optional[str] = None
    description: Optional[str] = None
    endpoints: List[ApiEndpoint] = Field(default_factory=list)
    auth_config: Optional[Dict[str, Any]] = None
    version: Optional[str] = None