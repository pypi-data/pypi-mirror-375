"""
Business analyzer for extracting Product Owner insights from code repositories.
Focuses on business functionality, user value, and product capabilities rather than technical implementation details.
"""
import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Set
from ..models.business import (
    ProductOwnerReport, BusinessFeature, TechnicalStackInfo, SecurityFeature,
    DataModel, IntegrationPoint, RiskAssessment, DevelopmentInsight,
    BusinessDomain, RiskLevel, CompletionStatus
)
from ..models.api import ApiCollection, ApiEndpoint
from .factory import AnalyzerFactory
from rich.console import Console

console = Console(stderr=True)


class BusinessAnalyzer:
    """Analyzes repositories for business insights and Product Owner reporting."""
    
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.repo_name = repo_path.name
        
    def analyze(self) -> ProductOwnerReport:
        """
        Perform comprehensive business analysis of the repository.
        
        Returns:
            Complete Product Owner report with business insights
        """
        console.print(f"[blue]Analyzing {self.repo_name} for business insights...[/blue]")
        
        # Get technical API analysis first
        try:
            api_collection = AnalyzerFactory.analyze_repository(self.repo_path)
        except ValueError:
            # If no technical analyzer matches, create empty collection
            api_collection = ApiCollection(name=self.repo_name, endpoints=[])
        
        # Perform business analysis
        technical_stack = self._analyze_technical_stack()
        features = self._identify_business_features(api_collection)
        data_models = self._analyze_data_models()
        integrations = self._identify_integrations()
        security_features = self._analyze_security_features()
        risks = self._assess_risks()
        dev_insights = self._analyze_development_practices()
        
        # Generate business insights
        user_journeys = self._identify_user_journeys(features)
        feature_gaps = self._identify_feature_gaps(features)
        recommendations = self._generate_recommendations(features, risks)
        
        # Calculate metrics
        features_by_domain = self._calculate_features_by_domain(features)
        completion_score = self._calculate_completion_score(features)
        
        # Generate executive summary
        executive_summary = self._generate_executive_summary(features, technical_stack)
        business_value = self._identify_business_value_proposition(features)
        
        return ProductOwnerReport(
            repository_name=self.repo_name,
            executive_summary=executive_summary,
            business_value_proposition=business_value,
            technical_stack=technical_stack,
            identified_features=features,
            data_models=data_models,
            user_journeys=user_journeys,
            integration_points=integrations,
            external_dependencies=self._identify_external_dependencies(),
            security_features=security_features,
            compliance_considerations=self._identify_compliance_considerations(),
            risk_assessments=risks,
            development_insights=dev_insights,
            feature_gaps=feature_gaps,
            enhancement_opportunities=self._identify_enhancement_opportunities(features),
            priority_recommendations=recommendations,
            total_endpoints=len(api_collection.endpoints),
            features_by_domain=features_by_domain,
            completion_score=completion_score
        )
    
    def _analyze_technical_stack(self) -> TechnicalStackInfo:
        """Analyze the technical stack at a high level."""
        stack = TechnicalStackInfo()
        
        # Detect primary language
        language_files = {
            'python': ['*.py', 'requirements.txt', 'pyproject.toml', 'Pipfile'],
            'java': ['*.java', 'pom.xml', 'build.gradle', 'gradle.properties'],
            'javascript': ['*.js', 'package.json', 'node_modules'],
            'typescript': ['*.ts', 'tsconfig.json'],
            'go': ['*.go', 'go.mod'],
            'rust': ['*.rs', 'Cargo.toml'],
            'csharp': ['*.cs', '*.csproj', '*.sln']
        }
        
        for language, patterns in language_files.items():
            if any(list(self.repo_path.glob(f"**/{pattern}")) for pattern in patterns):
                stack.primary_language = language
                break
        
        # Detect framework
        framework_indicators = {
            'FastAPI': ['fastapi', 'uvicorn'],
            'Spring Boot': ['spring-boot', '@SpringBootApplication', 'application.properties'],
            'Express': ['express', 'app.listen'],
            'Django': ['django', 'manage.py', 'settings.py'],
            'Flask': ['flask', 'app.run'],
            'React': ['react', 'jsx'],
            'Angular': ['angular', '@angular'],
            'Vue': ['vue', '.vue']
        }
        
        for framework, indicators in framework_indicators.items():
            if self._check_indicators_in_code(indicators):
                stack.framework = framework
                break
        
        # Detect database type
        db_indicators = {
            'PostgreSQL': ['postgresql', 'psycopg2', 'pg_'],
            'MySQL': ['mysql', 'pymysql', 'MariaDB'],
            'MongoDB': ['mongodb', 'mongoose', 'pymongo'],
            'SQLite': ['sqlite', 'sqlite3'],
            'Redis': ['redis', 'jedis'],
            'Oracle': ['oracle', 'cx_Oracle']
        }
        
        for db_type, indicators in db_indicators.items():
            if self._check_indicators_in_code(indicators):
                stack.database_type = db_type
                break
        
        # Count dependencies
        stack.dependencies_count = self._count_dependencies()
        
        # Detect architecture pattern
        if self._has_microservice_indicators():
            stack.architecture_pattern = "microservice"
        elif self._has_mvc_structure():
            stack.architecture_pattern = "mvc"
        else:
            stack.architecture_pattern = "monolith"
        
        return stack
    
    def _identify_business_features(self, api_collection: ApiCollection) -> List[BusinessFeature]:
        """Identify business features from API endpoints and code structure."""
        features = []
        
        # Group endpoints by business domain
        endpoint_groups = self._group_endpoints_by_domain(api_collection.endpoints)
        
        for domain, endpoints in endpoint_groups.items():
            feature = self._create_feature_from_endpoints(domain, endpoints)
            if feature:
                features.append(feature)
        
        # Add features identified from code structure
        code_features = self._identify_features_from_code_structure()
        features.extend(code_features)
        
        return features
    
    def _group_endpoints_by_domain(self, endpoints: List[ApiEndpoint]) -> Dict[BusinessDomain, List[ApiEndpoint]]:
        """Group API endpoints by business domain."""
        groups = {}
        
        for endpoint in endpoints:
            domain = self._classify_endpoint_domain(endpoint)
            if domain not in groups:
                groups[domain] = []
            groups[domain].append(endpoint)
        
        return groups
    
    def _classify_endpoint_domain(self, endpoint: ApiEndpoint) -> BusinessDomain:
        """Classify an endpoint into a business domain."""
        path_lower = endpoint.path.lower()
        name_lower = (endpoint.name or "").lower()
        
        # Authentication/Authorization
        if any(keyword in path_lower or keyword in name_lower 
               for keyword in ['auth', 'login', 'logout', 'token', 'session', 'oauth', 'jwt']):
            return BusinessDomain.AUTHENTICATION
        
        # User Management
        if any(keyword in path_lower or keyword in name_lower 
               for keyword in ['user', 'profile', 'account', 'customer', 'member']):
            return BusinessDomain.USER_MANAGEMENT
        
        # Payment
        if any(keyword in path_lower or keyword in name_lower 
               for keyword in ['payment', 'pay', 'transaction', 'billing', 'invoice', 'charge', 'card']):
            return BusinessDomain.PAYMENT
        
        # Notification
        if any(keyword in path_lower or keyword in name_lower 
               for keyword in ['notification', 'notify', 'email', 'sms', 'message', 'alert']):
            return BusinessDomain.NOTIFICATION
        
        # Reporting
        if any(keyword in path_lower or keyword in name_lower 
               for keyword in ['report', 'analytics', 'dashboard', 'metrics', 'stats']):
            return BusinessDomain.REPORTING
        
        # Content Management
        if any(keyword in path_lower or keyword in name_lower 
               for keyword in ['content', 'article', 'post', 'media', 'document', 'file']):
            return BusinessDomain.CONTENT_MANAGEMENT
        
        # Integration
        if any(keyword in path_lower or keyword in name_lower 
               for keyword in ['webhook', 'callback', 'integration', 'sync', 'import', 'export']):
            return BusinessDomain.INTEGRATION
        
        # Security
        if any(keyword in path_lower or keyword in name_lower 
               for keyword in ['security', 'permission', 'role', 'access', 'policy']):
            return BusinessDomain.SECURITY
        
        return BusinessDomain.OTHER
    
    def _create_feature_from_endpoints(self, domain: BusinessDomain, endpoints: List[ApiEndpoint]) -> Optional[BusinessFeature]:
        """Create a business feature from a group of endpoints."""
        if not endpoints:
            return None
        
        # Generate feature name and description based on domain
        domain_info = self._get_domain_info(domain)
        
        # Assess completion status based on CRUD operations
        completion_status = self._assess_feature_completion(endpoints)
        
        # Extract endpoint paths
        endpoint_paths = [f"{ep.method.value} {ep.path}" for ep in endpoints]
        
        return BusinessFeature(
            name=domain_info["name"],
            domain=domain,
            description=domain_info["description"],
            user_value=domain_info["user_value"],
            endpoints=endpoint_paths,
            completion_status=completion_status,
            confidence=0.8,  # High confidence for endpoint-derived features
            technical_implementation=f"Implemented via {len(endpoints)} REST API endpoints"
        )
    
    def _get_domain_info(self, domain: BusinessDomain) -> Dict[str, str]:
        """Get business information for a domain."""
        domain_info = {
            BusinessDomain.AUTHENTICATION: {
                "name": "Authentication & Authorization",
                "description": "User login, logout, and access control functionality",
                "user_value": "Secure access to the system with proper user identity verification"
            },
            BusinessDomain.USER_MANAGEMENT: {
                "name": "User Management",
                "description": "User profile management, registration, and account operations",
                "user_value": "Users can manage their accounts and personal information"
            },
            BusinessDomain.PAYMENT: {
                "name": "Payment Processing",
                "description": "Financial transactions, billing, and payment processing",
                "user_value": "Secure and reliable payment processing for business transactions"
            },
            BusinessDomain.NOTIFICATION: {
                "name": "Notification System",
                "description": "Communication and alert delivery to users",
                "user_value": "Keep users informed with timely notifications and updates"
            },
            BusinessDomain.REPORTING: {
                "name": "Analytics & Reporting",
                "description": "Business intelligence, metrics, and data visualization",
                "user_value": "Data-driven insights for informed business decisions"
            },
            BusinessDomain.CONTENT_MANAGEMENT: {
                "name": "Content Management",
                "description": "Creation, editing, and management of content and media",
                "user_value": "Easy content creation and management capabilities"
            },
            BusinessDomain.INTEGRATION: {
                "name": "External Integrations",
                "description": "Third-party system integrations and data synchronization",
                "user_value": "Seamless connectivity with external tools and services"
            },
            BusinessDomain.SECURITY: {
                "name": "Security & Access Control",
                "description": "Advanced security features and permission management",
                "user_value": "Enterprise-grade security and fine-grained access controls"
            },
            BusinessDomain.OTHER: {
                "name": "Core Business Logic",
                "description": "Primary business functionality and operations",
                "user_value": "Core features that deliver the main business value"
            }
        }
        
        return domain_info.get(domain, domain_info[BusinessDomain.OTHER])
    
    def _assess_feature_completion(self, endpoints: List[ApiEndpoint]) -> CompletionStatus:
        """Assess how complete a feature is based on available endpoints."""
        methods = {ep.method.value for ep in endpoints}
        
        # Check for CRUD operations
        has_create = any(method in methods for method in ['POST'])
        has_read = any(method in methods for method in ['GET'])
        has_update = any(method in methods for method in ['PUT', 'PATCH'])
        has_delete = any(method in methods for method in ['DELETE'])
        
        crud_operations = sum([has_create, has_read, has_update, has_delete])
        
        if crud_operations >= 3:
            return CompletionStatus.COMPLETE
        elif crud_operations >= 2:
            return CompletionStatus.PARTIAL
        elif crud_operations == 1:
            return CompletionStatus.SKELETON
        else:
            return CompletionStatus.MISSING
    
    def _analyze_data_models(self) -> List[DataModel]:
        """Analyze data models and business entities."""
        data_models = []
        
        # Look for model/entity files
        model_patterns = [
            "**/*model*.py", "**/*entity*.py", "**/*dto*.py",
            "**/*Model.java", "**/*Entity.java", "**/*DTO.java",
            "**/*model*.js", "**/*entity*.js",
            "**/*Model.ts", "**/*Entity.ts"
        ]
        
        for pattern in model_patterns:
            for file_path in self.repo_path.glob(pattern):
                models = self._extract_data_models_from_file(file_path)
                data_models.extend(models)
        
        return data_models
    
    def _extract_data_models_from_file(self, file_path: Path) -> List[DataModel]:
        """Extract data model information from a single file."""
        models = []
        
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Simple pattern matching for class definitions
            # This could be enhanced with proper AST parsing
            class_pattern = r'class\s+(\w+).*?{([^}]*)}'
            python_class_pattern = r'class\s+(\w+).*?:\s*(.*?)(?=class|\Z)'
            
            if file_path.suffix == '.py':
                matches = re.finditer(python_class_pattern, content, re.DOTALL)
            else:
                matches = re.finditer(class_pattern, content, re.DOTALL)
            
            for match in matches:
                class_name = match.group(1)
                class_body = match.group(2)
                
                # Extract fields (simplified)
                fields = self._extract_fields_from_class_body(class_body, file_path.suffix)
                
                if fields:  # Only add if we found fields
                    model = DataModel(
                        name=class_name,
                        fields=fields,
                        business_purpose=self._infer_business_purpose(class_name),
                        location=str(file_path.relative_to(self.repo_path))
                    )
                    models.append(model)
        
        except Exception as e:
            console.print(f"[yellow]Warning: Could not analyze {file_path}: {str(e)}[/yellow]")
        
        return models
    
    def _extract_fields_from_class_body(self, class_body: str, file_extension: str) -> List[str]:
        """Extract field names from a class body."""
        fields = []
        
        if file_extension == '.py':
            # Python field patterns
            field_patterns = [
                r'(\w+)\s*:\s*\w+',  # Type annotations
                r'self\.(\w+)\s*=',  # Instance variables
                r'(\w+)\s*=\s*Field\(',  # Pydantic fields
            ]
        elif file_extension in ['.java']:
            # Java field patterns
            field_patterns = [
                r'private\s+\w+\s+(\w+)\s*[;=]',
                r'public\s+\w+\s+(\w+)\s*[;=]',
            ]
        else:
            # JavaScript/TypeScript patterns
            field_patterns = [
                r'(\w+)\s*:\s*\w+',  # Type annotations
                r'this\.(\w+)\s*=',  # Instance variables
            ]
        
        for pattern in field_patterns:
            matches = re.findall(pattern, class_body)
            fields.extend(matches)
        
        # Remove duplicates and common non-field names
        excluded = {'self', 'this', 'constructor', 'toString', 'equals', 'hashCode'}
        fields = list(set(field for field in fields if field not in excluded))
        
        return fields[:10]  # Limit to prevent noise
    
    def _infer_business_purpose(self, class_name: str) -> Optional[str]:
        """Infer the business purpose of a data model from its name."""
        name_lower = class_name.lower()
        
        purpose_mapping = {
            'user': 'Represents system users and their profile information',
            'customer': 'Represents customers and their business relationship',
            'order': 'Represents business orders and transactions',
            'product': 'Represents products or services offered',
            'payment': 'Represents payment information and transactions',
            'invoice': 'Represents billing and invoicing data',
            'notification': 'Represents system notifications and alerts',
            'report': 'Represents business reports and analytics data',
            'transaction': 'Represents business transactions and their details',
            'account': 'Represents user or business accounts',
            'profile': 'Represents user profile and preference data',
            'setting': 'Represents system or user configuration settings',
            'log': 'Represents system logs and audit trails',
            'event': 'Represents business events and activities'
        }
        
        for keyword, purpose in purpose_mapping.items():
            if keyword in name_lower:
                return purpose
        
        return None
    
    def _identify_integrations(self) -> List[IntegrationPoint]:
        """Identify external system integration points."""
        integrations = []
        
        # Look for common integration patterns in code
        integration_patterns = {
            'REST API': ['requests', 'http', 'fetch', 'axios', 'RestTemplate', 'HttpClient'],
            'Database': ['jdbc', 'sqlalchemy', 'mongoose', 'hibernate', 'prisma'],
            'Message Queue': ['kafka', 'rabbitmq', 'sqs', 'redis', 'celery', 'jms'],
            'Payment Gateway': ['stripe', 'paypal', 'braintree', 'square', 'adyen'],
            'Email Service': ['sendgrid', 'mailgun', 'ses', 'nodemailer', 'javamail'],
            'Cloud Storage': ['s3', 'gcs', 'azure-storage', 'cloudinary'],
            'Authentication': ['oauth', 'saml', 'ldap', 'auth0', 'firebase-auth']
        }
        
        for integration_type, indicators in integration_patterns.items():
            if self._check_indicators_in_code(indicators):
                integration = IntegrationPoint(
                    name=f"External {integration_type}",
                    integration_type=integration_type,
                    direction="outbound",
                    business_purpose=self._get_integration_business_purpose(integration_type)
                )
                integrations.append(integration)
        
        return integrations
    
    def _get_integration_business_purpose(self, integration_type: str) -> str:
        """Get the business purpose for an integration type."""
        purposes = {
            'REST API': 'Communicate with external services and third-party APIs',
            'Database': 'Persistent data storage and retrieval for business operations',
            'Message Queue': 'Asynchronous processing and inter-service communication',
            'Payment Gateway': 'Process payments and handle financial transactions',
            'Email Service': 'Send transactional emails and notifications to users',
            'Cloud Storage': 'Store and manage files, documents, and media content',
            'Authentication': 'Secure user authentication and identity management'
        }
        return purposes.get(integration_type, 'External system integration')
    
    def _analyze_security_features(self) -> List[SecurityFeature]:
        """Analyze security features implemented in the codebase."""
        security_features = []
        
        security_patterns = {
            'Authentication': ['@authenticate', 'login', 'jwt', 'oauth', 'passport'],
            'Authorization': ['@authorize', 'permission', 'role', 'access_control'],
            'Input Validation': ['validation', 'sanitize', 'escape', 'validator'],
            'Encryption': ['encrypt', 'hash', 'bcrypt', 'crypto', 'ssl', 'tls'],
            'CSRF Protection': ['csrf', 'xsrf', 'token'],
            'Rate Limiting': ['rate_limit', 'throttle', 'ratelimiter'],
            'SQL Injection Prevention': ['parameterized', 'prepared_statement', 'orm'],
            'Audit Logging': ['audit', 'security_log', 'access_log']
        }
        
        for feature_type, indicators in security_patterns.items():
            confidence = self._calculate_security_feature_confidence(indicators)
            if confidence > 0.3:  # Only include if reasonably confident
                feature = SecurityFeature(
                    feature_type=feature_type,
                    implementation=f"Detected through code patterns and frameworks",
                    confidence=confidence,
                    compliance_relevance=self._get_compliance_relevance(feature_type)
                )
                security_features.append(feature)
        
        return security_features
    
    def _calculate_security_feature_confidence(self, indicators: List[str]) -> float:
        """Calculate confidence level for a security feature."""
        matches = sum(1 for indicator in indicators if self._check_indicators_in_code([indicator]))
        return min(matches / len(indicators), 1.0)
    
    def _get_compliance_relevance(self, feature_type: str) -> List[str]:
        """Get compliance standards relevant to a security feature."""
        compliance_mapping = {
            'Authentication': ['GDPR', 'SOC2', 'ISO27001'],
            'Authorization': ['GDPR', 'SOC2', 'HIPAA'],
            'Encryption': ['PCI-DSS', 'GDPR', 'HIPAA', 'SOC2'],
            'Audit Logging': ['SOC2', 'GDPR', 'HIPAA', 'PCI-DSS'],
            'Input Validation': ['OWASP', 'PCI-DSS'],
            'SQL Injection Prevention': ['OWASP', 'PCI-DSS']
        }
        return compliance_mapping.get(feature_type, [])
    
    def _assess_risks(self) -> List[RiskAssessment]:
        """Assess potential risks in the codebase."""
        risks = []
        
        # Security risks
        if not self._has_strong_authentication():
            risks.append(RiskAssessment(
                category="Security",
                description="Authentication mechanism may not be robust enough",
                risk_level=RiskLevel.HIGH,
                impact="Unauthorized access to sensitive data and functionality",
                mitigation_suggestions=["Implement multi-factor authentication", "Use industry-standard authentication frameworks"]
            ))
        
        # Performance risks
        if self._has_potential_performance_issues():
            risks.append(RiskAssessment(
                category="Performance",
                description="Potential performance bottlenecks detected",
                risk_level=RiskLevel.MEDIUM,
                impact="Poor user experience and system scalability issues",
                mitigation_suggestions=["Implement caching", "Optimize database queries", "Add performance monitoring"]
            ))
        
        # Maintainability risks
        if self._has_maintainability_issues():
            risks.append(RiskAssessment(
                category="Maintainability",
                description="Code organization may hinder long-term maintenance",
                risk_level=RiskLevel.MEDIUM,
                impact="Increased development costs and slower feature delivery",
                mitigation_suggestions=["Refactor complex modules", "Improve documentation", "Add automated tests"]
            ))
        
        return risks
    
    def _analyze_development_practices(self) -> DevelopmentInsight:
        """Analyze development practices and code quality indicators."""
        return DevelopmentInsight(
            code_organization=self._assess_code_organization(),
            testing_coverage=self._assess_testing_coverage(),
            documentation_quality=self._assess_documentation_quality(),
            deployment_readiness=self._assess_deployment_readiness(),
            development_velocity_indicators=self._identify_velocity_indicators(),
            technical_debt_indicators=self._identify_technical_debt()
        )
    
    # Helper methods for analysis
    def _check_indicators_in_code(self, indicators: List[str]) -> bool:
        """Check if any of the indicators are present in the codebase."""
        for indicator in indicators:
            for file_path in self.repo_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in ['.py', '.java', '.js', '.ts', '.json', '.yml', '.yaml', '.xml']:
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        if indicator.lower() in content.lower():
                            return True
                    except:
                        continue
        return False
    
    def _count_dependencies(self) -> int:
        """Count the number of external dependencies."""
        dependency_files = [
            'requirements.txt', 'pyproject.toml', 'Pipfile',
            'package.json', 'pom.xml', 'build.gradle',
            'go.mod', 'Cargo.toml'
        ]
        
        total = 0
        for dep_file in dependency_files:
            file_path = self.repo_path / dep_file
            if file_path.exists():
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    # Simple line counting (could be more sophisticated)
                    total += len([line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')])
                except:
                    continue
        
        return total
    
    def _has_microservice_indicators(self) -> bool:
        """Check for microservice architecture indicators."""
        indicators = ['docker', 'kubernetes', 'k8s', 'microservice', 'service-mesh', 'api-gateway']
        return self._check_indicators_in_code(indicators)
    
    def _has_mvc_structure(self) -> bool:
        """Check for MVC architecture pattern."""
        mvc_dirs = ['controllers', 'models', 'views', 'controller', 'model', 'view']
        return any((self.repo_path / mvc_dir).exists() for mvc_dir in mvc_dirs)
    
    def _identify_features_from_code_structure(self) -> List[BusinessFeature]:
        """Identify additional features from code structure and file organization."""
        features = []
        
        # Look for feature-specific directories or modules
        feature_indicators = {
            'User Management': ['user', 'profile', 'account'],
            'File Management': ['file', 'upload', 'storage', 'document'],
            'Workflow Engine': ['workflow', 'process', 'task', 'job'],
            'Search Functionality': ['search', 'index', 'elasticsearch', 'solr'],
            'Caching System': ['cache', 'redis', 'memcached'],
            'Background Processing': ['queue', 'worker', 'job', 'task', 'celery'],
            'Monitoring & Logging': ['monitor', 'log', 'metric', 'health']
        }
        
        for feature_name, indicators in feature_indicators.items():
            if any((self.repo_path / indicator).exists() or 
                   any(self.repo_path.glob(f"**/*{indicator}*")) for indicator in indicators):
                
                feature = BusinessFeature(
                    name=feature_name,
                    domain=BusinessDomain.OTHER,
                    description=f"Feature identified from code structure: {feature_name}",
                    user_value=f"Provides {feature_name.lower()} capabilities to users",
                    completion_status=CompletionStatus.PARTIAL,
                    confidence=0.6,  # Lower confidence for structure-based detection
                    technical_implementation="Identified from file/directory structure"
                )
                features.append(feature)
        
        return features
    
    def _identify_user_journeys(self, features: List[BusinessFeature]) -> List[str]:
        """Identify possible user journeys based on available features."""
        journeys = []
        
        feature_domains = {f.domain for f in features}
        
        # Common user journey patterns
        if BusinessDomain.AUTHENTICATION in feature_domains and BusinessDomain.USER_MANAGEMENT in feature_domains:
            journeys.append("User Registration → Email Verification → Profile Setup → System Access")
        
        if BusinessDomain.PAYMENT in feature_domains:
            journeys.append("Product Selection → Cart Management → Payment Processing → Order Confirmation")
        
        if BusinessDomain.NOTIFICATION in feature_domains:
            journeys.append("User Action → System Processing → Notification Generation → User Alert")
        
        if BusinessDomain.REPORTING in feature_domains:
            journeys.append("Data Collection → Processing → Report Generation → Dashboard Visualization")
        
        return journeys
    
    def _identify_feature_gaps(self, features: List[BusinessFeature]) -> List[str]:
        """Identify potentially missing features based on common patterns."""
        gaps = []
        
        domains_present = {f.domain for f in features}
        
        # Common feature expectations
        if BusinessDomain.AUTHENTICATION in domains_present and BusinessDomain.USER_MANAGEMENT not in domains_present:
            gaps.append("User profile management functionality")
        
        if BusinessDomain.PAYMENT in domains_present and BusinessDomain.NOTIFICATION not in domains_present:
            gaps.append("Payment confirmation notifications")
        
        if len([f for f in features if f.completion_status == CompletionStatus.COMPLETE]) < len(features) * 0.5:
            gaps.append("Many features appear to be incomplete or in development")
        
        return gaps
    
    def _generate_recommendations(self, features: List[BusinessFeature], risks: List[RiskAssessment]) -> List[str]:
        """Generate priority recommendations for the Product Owner."""
        recommendations = []
        
        # Feature completeness recommendations
        incomplete_features = [f for f in features if f.completion_status in [CompletionStatus.PARTIAL, CompletionStatus.SKELETON]]
        if incomplete_features:
            recommendations.append(f"Complete development of {len(incomplete_features)} partially implemented features")
        
        # Security recommendations
        high_risks = [r for r in risks if r.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]]
        if high_risks:
            recommendations.append("Address high-priority security and compliance risks immediately")
        
        # Integration recommendations
        if not any(f.domain == BusinessDomain.INTEGRATION for f in features):
            recommendations.append("Consider adding API integration capabilities for better ecosystem connectivity")
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _calculate_features_by_domain(self, features: List[BusinessFeature]) -> Dict[str, int]:
        """Calculate feature distribution by business domain."""
        domain_counts = {}
        for feature in features:
            domain_name = feature.domain.value
            domain_counts[domain_name] = domain_counts.get(domain_name, 0) + 1
        return domain_counts
    
    def _calculate_completion_score(self, features: List[BusinessFeature]) -> float:
        """Calculate overall feature completion score."""
        if not features:
            return 0.0
        
        completion_weights = {
            CompletionStatus.COMPLETE: 1.0,
            CompletionStatus.PARTIAL: 0.6,
            CompletionStatus.SKELETON: 0.3,
            CompletionStatus.MISSING: 0.0
        }
        
        total_weight = sum(completion_weights[f.completion_status] for f in features)
        return total_weight / len(features)
    
    def _generate_executive_summary(self, features: List[BusinessFeature], tech_stack: TechnicalStackInfo) -> str:
        """Generate executive summary of the repository."""
        feature_count = len(features)
        complete_features = len([f for f in features if f.completion_status == CompletionStatus.COMPLETE])
        
        framework_text = f" built with {tech_stack.framework}" if tech_stack.framework else ""
        
        return (f"This repository contains a {tech_stack.primary_language or 'software'} application{framework_text} "
                f"implementing {feature_count} business features across multiple domains. "
                f"{complete_features} features appear to be fully implemented, "
                f"while {feature_count - complete_features} are in various stages of development. "
                f"The system demonstrates capabilities in core business areas with {tech_stack.dependencies_count} "
                f"external dependencies supporting the implementation.")
    
    def _identify_business_value_proposition(self, features: List[BusinessFeature]) -> str:
        """Identify the main business value proposition."""
        domain_counts = {}
        for feature in features:
            domain_counts[feature.domain] = domain_counts.get(feature.domain, 0) + 1
        
        if not domain_counts:
            return "Business value proposition could not be determined from available features"
        
        primary_domain = max(domain_counts, key=domain_counts.get)
        
        value_propositions = {
            BusinessDomain.PAYMENT: "Provides secure and efficient payment processing capabilities for business transactions",
            BusinessDomain.USER_MANAGEMENT: "Enables comprehensive user account and profile management functionality",
            BusinessDomain.AUTHENTICATION: "Delivers secure access control and user authentication services",
            BusinessDomain.NOTIFICATION: "Facilitates effective communication and user engagement through notifications",
            BusinessDomain.REPORTING: "Empowers data-driven decision making through analytics and reporting",
            BusinessDomain.INTEGRATION: "Enables seamless connectivity with external systems and services",
            BusinessDomain.CONTENT_MANAGEMENT: "Provides flexible content creation and management capabilities"
        }
        
        return value_propositions.get(primary_domain, "Delivers core business functionality through a well-structured software system")
    
    # Additional helper methods for risk assessment
    def _has_strong_authentication(self) -> bool:
        """Check if the system has strong authentication mechanisms."""
        strong_auth_indicators = ['jwt', 'oauth', 'saml', 'mfa', 'two-factor', 'bcrypt']
        return self._check_indicators_in_code(strong_auth_indicators)
    
    def _has_potential_performance_issues(self) -> bool:
        """Check for potential performance issues."""
        # Simple heuristic: lots of dependencies might indicate complexity
        return self._count_dependencies() > 50
    
    def _has_maintainability_issues(self) -> bool:
        """Check for maintainability red flags."""
        # Look for very large files or deeply nested structures
        large_files = list(self.repo_path.glob("**/*.py")) + list(self.repo_path.glob("**/*.java"))
        large_file_count = 0
        
        for file_path in large_files[:20]:  # Sample first 20 files
            try:
                if file_path.stat().st_size > 10000:  # > 10KB
                    large_file_count += 1
            except:
                continue
        
        return large_file_count > 5
    
    def _assess_code_organization(self) -> str:
        """Assess code organization quality."""
        if self._has_mvc_structure():
            return "Well-organized with clear separation of concerns (MVC pattern detected)"
        elif (self.repo_path / "src").exists():
            return "Organized with standard source code structure"
        else:
            return "Basic organization, could benefit from clearer structure"
    
    def _assess_testing_coverage(self) -> str:
        """Assess testing coverage."""
        test_dirs = ['test', 'tests', 'spec', '__tests__']
        test_files = []
        
        for test_dir in test_dirs:
            test_files.extend(list(self.repo_path.glob(f"**/{test_dir}/**/*.py")))
            test_files.extend(list(self.repo_path.glob(f"**/{test_dir}/**/*.java")))
            test_files.extend(list(self.repo_path.glob(f"**/{test_dir}/**/*.js")))
        
        if len(test_files) > 10:
            return "Comprehensive testing coverage with multiple test files"
        elif len(test_files) > 0:
            return "Basic testing coverage present"
        else:
            return "Limited or no automated tests detected"
    
    def _assess_documentation_quality(self) -> str:
        """Assess documentation quality."""
        doc_files = ['README.md', 'docs', 'documentation', 'wiki']
        doc_count = sum(1 for doc_file in doc_files if (self.repo_path / doc_file).exists())
        
        if doc_count >= 2:
            return "Well-documented with multiple documentation sources"
        elif doc_count == 1:
            return "Basic documentation present"
        else:
            return "Limited documentation available"
    
    def _assess_deployment_readiness(self) -> str:
        """Assess deployment readiness."""
        deployment_files = ['Dockerfile', 'docker-compose.yml', '.github/workflows', 'k8s', 'kubernetes']
        deployment_indicators = sum(1 for df in deployment_files if (self.repo_path / df).exists())
        
        if deployment_indicators >= 2:
            return "Production-ready with multiple deployment options"
        elif deployment_indicators == 1:
            return "Basic deployment configuration present"
        else:
            return "Deployment configuration may need attention"
    
    def _identify_velocity_indicators(self) -> List[str]:
        """Identify development velocity indicators."""
        indicators = []
        
        if (self.repo_path / '.github' / 'workflows').exists():
            indicators.append("CI/CD pipeline configured")
        
        if self._check_indicators_in_code(['test', 'spec']):
            indicators.append("Automated testing in place")
        
        if (self.repo_path / 'requirements.txt').exists() or (self.repo_path / 'package.json').exists():
            indicators.append("Dependency management configured")
        
        return indicators
    
    def _identify_technical_debt(self) -> List[str]:
        """Identify technical debt indicators."""
        debt_indicators = []
        
        if self._count_dependencies() > 100:
            debt_indicators.append("High number of dependencies may indicate complexity")
        
        if not self._check_indicators_in_code(['test', 'spec']):
            debt_indicators.append("Limited test coverage increases maintenance risk")
        
        if self._has_maintainability_issues():
            debt_indicators.append("Large files detected, may benefit from refactoring")
        
        return debt_indicators
    
    def _identify_external_dependencies(self) -> List[str]:
        """Identify external system dependencies."""
        dependencies = []
        
        cloud_services = ['aws', 'azure', 'gcp', 'google-cloud']
        if self._check_indicators_in_code(cloud_services):
            dependencies.append("Cloud services (AWS/Azure/GCP)")
        
        databases = ['postgresql', 'mysql', 'mongodb', 'redis']
        for db in databases:
            if self._check_indicators_in_code([db]):
                dependencies.append(f"{db.title()} database")
        
        return dependencies
    
    def _identify_compliance_considerations(self) -> List[str]:
        """Identify compliance considerations."""
        considerations = []
        
        if self._check_indicators_in_code(['gdpr', 'privacy', 'personal-data']):
            considerations.append("GDPR compliance may be required for personal data handling")
        
        if self._check_indicators_in_code(['payment', 'card', 'pci']):
            considerations.append("PCI-DSS compliance may be required for payment processing")
        
        if self._check_indicators_in_code(['health', 'medical', 'hipaa']):
            considerations.append("HIPAA compliance may be required for healthcare data")
        
        return considerations
    
    def _identify_enhancement_opportunities(self, features: List[BusinessFeature]) -> List[str]:
        """Identify enhancement opportunities."""
        opportunities = []
        
        domains_present = {f.domain for f in features}
        
        if BusinessDomain.AUTHENTICATION in domains_present and BusinessDomain.USER_MANAGEMENT not in domains_present:
            opportunities.append("Add comprehensive user profile management")
        
        if BusinessDomain.PAYMENT in domains_present and BusinessDomain.REPORTING not in domains_present:
            opportunities.append("Add financial reporting and analytics")
        
        if BusinessDomain.NOTIFICATION not in domains_present:
            opportunities.append("Implement user notification system")
        
        return opportunities