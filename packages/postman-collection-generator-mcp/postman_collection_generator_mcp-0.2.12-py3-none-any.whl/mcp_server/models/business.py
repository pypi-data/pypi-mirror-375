"""
Business analysis data models for Product Owner reporting.
These models represent business functionality and product insights extracted from code repositories.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class BusinessDomain(str, Enum):
    """Common business domains for categorizing features."""
    USER_MANAGEMENT = "user_management"
    AUTHENTICATION = "authentication"
    PAYMENT = "payment"
    NOTIFICATION = "notification"
    REPORTING = "reporting"
    INTEGRATION = "integration"
    CONTENT_MANAGEMENT = "content_management"
    WORKFLOW = "workflow"
    DATA_MANAGEMENT = "data_management"
    SECURITY = "security"
    MONITORING = "monitoring"
    OTHER = "other"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CompletionStatus(str, Enum):
    """Feature development completion status."""
    COMPLETE = "complete"
    PARTIAL = "partial"
    SKELETON = "skeleton"
    MISSING = "missing"


class TechnicalStackInfo(BaseModel):
    """High-level technical stack information."""
    primary_language: Optional[str] = None
    framework: Optional[str] = None
    database_type: Optional[str] = None
    deployment_method: Optional[str] = None
    testing_framework: Optional[str] = None
    build_tool: Optional[str] = None
    dependencies_count: int = 0
    architecture_pattern: Optional[str] = None  # e.g., "microservice", "monolith", "mvc"


class SecurityFeature(BaseModel):
    """Security and compliance features identified in the codebase."""
    feature_type: str  # e.g., "authentication", "authorization", "encryption"
    implementation: str  # Brief description of how it's implemented
    confidence: float = Field(ge=0.0, le=1.0)  # How confident we are this exists
    location: Optional[str] = None  # File/module where found
    compliance_relevance: List[str] = Field(default_factory=list)  # e.g., ["GDPR", "PCI-DSS"]


class DataModel(BaseModel):
    """Business data model/entity identified in the codebase."""
    name: str
    description: Optional[str] = None
    fields: List[str] = Field(default_factory=list)
    relationships: List[str] = Field(default_factory=list)
    business_purpose: Optional[str] = None
    location: Optional[str] = None  # File where defined


class IntegrationPoint(BaseModel):
    """External system integration point."""
    name: str
    integration_type: str  # e.g., "REST API", "Database", "Message Queue"
    direction: str  # "inbound", "outbound", "bidirectional"
    description: Optional[str] = None
    authentication_method: Optional[str] = None
    business_purpose: Optional[str] = None


class BusinessFeature(BaseModel):
    """Represents a business capability or feature."""
    name: str
    domain: BusinessDomain
    description: str
    user_value: str  # What value this provides to users/business
    endpoints: List[str] = Field(default_factory=list)  # API endpoints related to this feature
    data_models: List[str] = Field(default_factory=list)  # Data entities involved
    completion_status: CompletionStatus
    confidence: float = Field(ge=0.0, le=1.0)  # How confident we are this feature exists
    technical_implementation: Optional[str] = None  # Brief tech details
    dependencies: List[str] = Field(default_factory=list)  # Other features this depends on
    user_personas: List[str] = Field(default_factory=list)  # Who uses this feature


class RiskAssessment(BaseModel):
    """Risk assessment for technical or business concerns."""
    category: str  # e.g., "Security", "Performance", "Maintainability", "Compliance"
    description: str
    risk_level: RiskLevel
    impact: str  # Business impact if this risk materializes
    mitigation_suggestions: List[str] = Field(default_factory=list)
    affected_features: List[str] = Field(default_factory=list)


class DevelopmentInsight(BaseModel):
    """Insights about the development process and code quality."""
    code_organization: str  # How well organized is the code
    testing_coverage: str  # Assessment of testing
    documentation_quality: str  # Quality of technical documentation
    deployment_readiness: str  # How ready for production
    development_velocity_indicators: List[str] = Field(default_factory=list)
    technical_debt_indicators: List[str] = Field(default_factory=list)


class ProductOwnerReport(BaseModel):
    """Complete business analysis report for Product Owners."""
    
    # Basic Information
    repository_name: str
    analysis_date: datetime = Field(default_factory=datetime.now)
    
    # Executive Summary
    executive_summary: str
    business_value_proposition: str
    
    # Technical Overview (high-level)
    technical_stack: TechnicalStackInfo
    
    # Business Analysis
    identified_features: List[BusinessFeature] = Field(default_factory=list)
    data_models: List[DataModel] = Field(default_factory=list)
    user_journeys: List[str] = Field(default_factory=list)  # Identified user flows
    
    # Integration & Dependencies
    integration_points: List[IntegrationPoint] = Field(default_factory=list)
    external_dependencies: List[str] = Field(default_factory=list)
    
    # Security & Compliance
    security_features: List[SecurityFeature] = Field(default_factory=list)
    compliance_considerations: List[str] = Field(default_factory=list)
    
    # Risk Assessment
    risk_assessments: List[RiskAssessment] = Field(default_factory=list)
    
    # Development Insights
    development_insights: DevelopmentInsight
    
    # Recommendations
    feature_gaps: List[str] = Field(default_factory=list)  # Missing expected features
    enhancement_opportunities: List[str] = Field(default_factory=list)
    priority_recommendations: List[str] = Field(default_factory=list)
    
    # Metrics
    total_endpoints: int = 0
    features_by_domain: Dict[str, int] = Field(default_factory=dict)
    completion_score: float = Field(ge=0.0, le=1.0, default=0.0)  # Overall completion percentage