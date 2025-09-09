"""
Postman Collection v2.1 data models.
These models represent the structure of a Postman collection.
"""
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field


class PostmanAuth(BaseModel):
    """Authentication configuration for Postman."""
    type: str
    bearer: Optional[List[Dict[str, Any]]] = None
    basic: Optional[List[Dict[str, Any]]] = None
    apikey: Optional[List[Dict[str, Any]]] = None


class PostmanHeader(BaseModel):
    """HTTP header definition."""
    key: str
    value: str
    type: str = "text"
    disabled: bool = False


class PostmanQueryParam(BaseModel):
    """URL query parameter."""
    key: str
    value: str = ""
    description: Optional[str] = None
    disabled: bool = False


class PostmanUrl(BaseModel):
    """URL structure for requests."""
    raw: str
    protocol: Optional[str] = None
    host: Optional[List[str]] = None
    port: Optional[str] = None
    path: Optional[List[str]] = None
    query: Optional[List[PostmanQueryParam]] = None


class PostmanBody(BaseModel):
    """Request body configuration."""
    mode: str = "raw"
    raw: str = ""
    options: Optional[Dict[str, Any]] = None


class PostmanRequest(BaseModel):
    """HTTP request definition."""
    method: str
    header: List[PostmanHeader] = Field(default_factory=list)
    body: Optional[PostmanBody] = None
    url: PostmanUrl
    description: Optional[str] = None
    auth: Optional[PostmanAuth] = None


class PostmanResponse(BaseModel):
    """Example response for a request."""
    name: str
    originalRequest: Optional[PostmanRequest] = None
    status: str
    code: int
    header: List[PostmanHeader] = Field(default_factory=list)
    body: Optional[str] = None


class PostmanItem(BaseModel):
    """Individual request item or folder."""
    name: str
    request: Optional[PostmanRequest] = None
    response: List[PostmanResponse] = Field(default_factory=list)
    item: Optional[List["PostmanItem"]] = None
    description: Optional[str] = None


class PostmanInfo(BaseModel):
    """Collection metadata."""
    name: str
    description: Optional[str] = None
    schema_: str = Field(alias="schema", default="https://schema.getpostman.com/json/collection/v2.1.0/collection.json")


class PostmanCollection(BaseModel):
    """Root Postman collection structure."""
    info: PostmanInfo
    item: List[PostmanItem] = Field(default_factory=list)
    auth: Optional[PostmanAuth] = None
    variable: List[Dict[str, Any]] = Field(default_factory=list)


# Enable forward references
PostmanItem.model_rebuild()