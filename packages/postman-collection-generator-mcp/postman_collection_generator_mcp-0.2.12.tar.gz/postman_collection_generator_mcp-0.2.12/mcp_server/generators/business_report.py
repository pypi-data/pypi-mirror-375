"""
Business report generator for creating Product Owner-friendly documentation.
Generates comprehensive markdown reports from business analysis data.
"""
import os
import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from ..models.business import ProductOwnerReport, BusinessFeature, RiskLevel, CompletionStatus
from rich.console import Console

console = Console(stderr=True)


class BusinessReportGenerator:
    """Generates Product Owner reports in markdown format."""
    
    def __init__(self):
        self.output_dir = Path(os.environ.get("output_directory", "."))
    
    def generate(self, report: ProductOwnerReport, repo_name: str) -> Path:
        """
        Generate a comprehensive Product Owner report.
        
        Args:
            report: Business analysis report data
            repo_name: Name of the repository
            
        Returns:
            Path to the generated markdown report
        """
        console.print(f"[blue]Generating Product Owner report for {repo_name}...[/blue]")
        
        # Generate markdown content
        markdown_content = self._generate_markdown_report(report)
        
        # Save markdown report
        report_filename = f"{repo_name}_product_owner_report.md"
        report_path = self.output_dir / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Also save structured JSON data
        json_filename = f"{repo_name}_business_analysis.json"
        json_path = self.output_dir / json_filename
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report.model_dump(), f, indent=2, default=str)
        
        console.print(f"[green]✓ Generated Product Owner report: {report_filename}[/green]")
        console.print(f"[green]✓ Generated structured data: {json_filename}[/green]")
        
        return report_path
    
    def _generate_markdown_report(self, report: ProductOwnerReport) -> str:
        """Generate the complete markdown report."""
        sections = [
            self._generate_header(report),
            self._generate_executive_summary(report),
            self._generate_technical_overview(report),
            self._generate_business_features(report),
            self._generate_user_journeys(report),
            self._generate_data_models(report),
            self._generate_integrations(report),
            self._generate_security_compliance(report),
            self._generate_risk_assessment(report),
            self._generate_development_insights(report),
            self._generate_recommendations(report),
            self._generate_metrics(report),
            self._generate_footer()
        ]
        
        return '\n\n'.join(filter(None, sections))
    
    def _generate_header(self, report: ProductOwnerReport) -> str:
        """Generate report header."""
        return f"""# Product Owner Report: {report.repository_name}

**Analysis Date:** {report.analysis_date.strftime('%Y-%m-%d %H:%M UTC')}

**Report Purpose:** This report provides a business-focused analysis of the `{report.repository_name}` codebase, translating technical implementation into clear product insights for stakeholders, product owners, and business decision-makers.

---"""
    
    def _generate_executive_summary(self, report: ProductOwnerReport) -> str:
        """Generate executive summary section."""
        completion_percentage = int(report.completion_score * 100)
        
        return f"""## 📊 Executive Summary

### Business Value Proposition
{report.business_value_proposition}

### Key Findings
{report.executive_summary}

### Quick Stats
- **Features Identified:** {len(report.identified_features)}
- **API Endpoints:** {report.total_endpoints}
- **Overall Completion:** {completion_percentage}%
- **Risk Level:** {self._get_overall_risk_level(report)}
- **Primary Language:** {report.technical_stack.primary_language or 'Not detected'}
- **Framework:** {report.technical_stack.framework or 'Not detected'}"""
    
    def _generate_technical_overview(self, report: ProductOwnerReport) -> str:
        """Generate technical overview section."""
        tech = report.technical_stack
        
        architecture = tech.architecture_pattern or "Standard application"
        dependencies_text = f"{tech.dependencies_count} external" if tech.dependencies_count > 0 else "No external"
        
        return f"""## 🏗️ Technical Overview (High Level)

This section provides essential technical context without deep implementation details.

### Technology Stack
- **Primary Language:** {tech.primary_language or 'Not detected'}
- **Framework:** {tech.framework or 'Not detected'}
- **Database:** {tech.database_type or 'Not detected'}
- **Architecture:** {architecture.title()}
- **Dependencies:** {dependencies_text} dependencies
- **Testing Framework:** {tech.testing_framework or 'Not detected'}

### What This Means for Business
- **Development Speed:** {self._interpret_tech_for_business(tech)}
- **Scalability:** {self._interpret_scalability(tech)}
- **Maintenance:** {self._interpret_maintenance(tech)}"""
    
    def _generate_business_features(self, report: ProductOwnerReport) -> str:
        """Generate business features section."""
        if not report.identified_features:
            return """## 🎯 Business Features & Capabilities

No specific business features were identified in the codebase analysis. This may indicate:
- The repository contains infrastructure or utility code
- Features are not clearly separated or documented
- The codebase is in early development stages"""
        
        # Group features by completion status
        complete_features = [f for f in report.identified_features if f.completion_status == CompletionStatus.COMPLETE]
        partial_features = [f for f in report.identified_features if f.completion_status == CompletionStatus.PARTIAL]
        skeleton_features = [f for f in report.identified_features if f.completion_status == CompletionStatus.SKELETON]
        
        content = """## 🎯 Business Features & Capabilities

This section outlines the business functionality implemented or planned in the system.

"""
        
        if complete_features:
            content += """### ✅ Complete Features (Ready for Use)

"""
            for feature in complete_features:
                content += self._format_feature(feature)
        
        if partial_features:
            content += """### 🔄 Partially Implemented Features

"""
            for feature in partial_features:
                content += self._format_feature(feature)
        
        if skeleton_features:
            content += """### 🏗️ Features in Development

"""
            for feature in skeleton_features:
                content += self._format_feature(feature)
        
        return content
    
    def _format_feature(self, feature: BusinessFeature) -> str:
        """Format a single business feature."""
        confidence_emoji = "🟢" if feature.confidence >= 0.8 else "🟡" if feature.confidence >= 0.5 else "🔴"
        
        endpoints_text = ""
        if feature.endpoints:
            endpoints_text = f"\n  - **API Endpoints:** {len(feature.endpoints)}"
        
        dependencies_text = ""
        if feature.dependencies:
            dependencies_text = f"\n  - **Dependencies:** {', '.join(feature.dependencies)}"
        
        return f"""#### {confidence_emoji} {feature.name}
- **Business Value:** {feature.user_value}
- **Description:** {feature.description}
- **Domain:** {feature.domain.value.replace('_', ' ').title()}
- **Completion:** {feature.completion_status.value.title()}{endpoints_text}{dependencies_text}

"""
    
    def _generate_user_journeys(self, report: ProductOwnerReport) -> str:
        """Generate user journeys section."""
        if not report.user_journeys:
            return """## 👤 User Journeys

No clear user journeys were identified from the available features. Consider documenting user flows to better understand the system's business value."""
        
        content = """## 👤 User Journeys

Based on the identified features, these user journeys appear to be supported:

"""
        
        for i, journey in enumerate(report.user_journeys, 1):
            content += f"{i}. **{journey}**\n"
        
        return content
    
    def _generate_data_models(self, report: ProductOwnerReport) -> str:
        """Generate data models section."""
        if not report.data_models:
            return """## 📋 Business Data Models

No clear business data models were identified in the codebase. This may indicate:
- Data models are not clearly defined
- The system primarily handles external data
- Models are defined in external systems or databases"""
        
        content = """## 📋 Business Data Models

These represent the key business entities and data structures:

"""
        
        for model in report.data_models:
            purpose_text = f"**Purpose:** {model.business_purpose}" if model.business_purpose else ""
            fields_text = f"**Key Fields:** {', '.join(model.fields[:5])}" if model.fields else ""
            if len(model.fields) > 5:
                fields_text += f" (and {len(model.fields) - 5} more)"
            
            content += f"""### {model.name}
{purpose_text}
{fields_text}

"""
        
        return content
    
    def _generate_integrations(self, report: ProductOwnerReport) -> str:
        """Generate integrations section."""
        if not report.integration_points and not report.external_dependencies:
            return """## 🔗 External Integrations

No external integrations were detected. The system appears to be self-contained."""
        
        content = """## 🔗 External Integrations & Dependencies

"""
        
        if report.integration_points:
            content += """### Integration Points

"""
            for integration in report.integration_points:
                purpose_text = f"**Business Purpose:** {integration.business_purpose}" if integration.business_purpose else ""
                content += f"""#### {integration.name}
- **Type:** {integration.integration_type}
- **Direction:** {integration.direction.title()}
{purpose_text}

"""
        
        if report.external_dependencies:
            content += """### External Dependencies

"""
            for dependency in report.external_dependencies:
                content += f"- {dependency}\n"
        
        return content
    
    def _generate_security_compliance(self, report: ProductOwnerReport) -> str:
        """Generate security and compliance section."""
        content = """## 🔒 Security & Compliance

"""
        
        if report.security_features:
            content += """### Security Features Implemented

"""
            for security_feature in report.security_features:
                confidence_bar = "🟢" * int(security_feature.confidence * 3)
                compliance_text = ""
                if security_feature.compliance_relevance:
                    compliance_text = f" (Relevant for: {', '.join(security_feature.compliance_relevance)})"
                
                content += f"""#### {security_feature.feature_type}
- **Implementation:** {security_feature.implementation}
- **Confidence:** {confidence_bar} ({int(security_feature.confidence * 100)}%){compliance_text}

"""
        else:
            content += """### Security Features
No specific security implementations were detected through code analysis. This doesn't necessarily mean the system is insecure, but security measures may not be clearly visible or documented.

"""
        
        if report.compliance_considerations:
            content += """### Compliance Considerations

"""
            for consideration in report.compliance_considerations:
                content += f"- {consideration}\n"
        else:
            content += """### Compliance
No specific compliance requirements were identified from the codebase analysis.

"""
        
        return content
    
    def _generate_risk_assessment(self, report: ProductOwnerReport) -> str:
        """Generate risk assessment section."""
        if not report.risk_assessments:
            return """## ⚠️ Risk Assessment

No significant risks were identified through automated analysis. Manual review is still recommended for comprehensive risk assessment."""
        
        content = """## ⚠️ Risk Assessment

"""
        
        # Group risks by level
        critical_risks = [r for r in report.risk_assessments if r.risk_level == RiskLevel.CRITICAL]
        high_risks = [r for r in report.risk_assessments if r.risk_level == RiskLevel.HIGH]
        medium_risks = [r for r in report.risk_assessments if r.risk_level == RiskLevel.MEDIUM]
        low_risks = [r for r in report.risk_assessments if r.risk_level == RiskLevel.LOW]
        
        for risk_group, risks in [
            ("🔴 Critical Risks", critical_risks),
            ("🟠 High Risks", high_risks),
            ("🟡 Medium Risks", medium_risks),
            ("🟢 Low Risks", low_risks)
        ]:
            if risks:
                content += f"""### {risk_group}

"""
                for risk in risks:
                    mitigation_text = ""
                    if risk.mitigation_suggestions:
                        mitigation_text = f"\n**Mitigation:** {'; '.join(risk.mitigation_suggestions)}"
                    
                    content += f"""#### {risk.category}: {risk.description}
**Business Impact:** {risk.impact}{mitigation_text}

"""
        
        return content
    
    def _generate_development_insights(self, report: ProductOwnerReport) -> str:
        """Generate development insights section."""
        insights = report.development_insights
        
        return f"""## 👨‍💻 Development & Delivery Insights

### Code Quality & Organization
- **Code Organization:** {insights.code_organization}
- **Testing Coverage:** {insights.testing_coverage}
- **Documentation Quality:** {insights.documentation_quality}
- **Deployment Readiness:** {insights.deployment_readiness}

### Development Velocity Indicators
{self._format_list_items(insights.development_velocity_indicators, "No velocity indicators detected")}

### Technical Debt Indicators
{self._format_list_items(insights.technical_debt_indicators, "No significant technical debt detected")}

### What This Means for Product Development
- **Development Speed:** {self._interpret_development_speed(insights)}
- **Release Readiness:** {self._interpret_release_readiness(insights)}
- **Future Maintenance:** {self._interpret_maintenance_outlook(insights)}"""
    
    def _generate_recommendations(self, report: ProductOwnerReport) -> str:
        """Generate recommendations section."""
        content = """## 💡 Recommendations & Next Steps

"""
        
        if report.priority_recommendations:
            content += """### Priority Actions

"""
            for i, recommendation in enumerate(report.priority_recommendations, 1):
                content += f"{i}. {recommendation}\n"
        
        if report.feature_gaps:
            content += """
### Identified Feature Gaps

"""
            for gap in report.feature_gaps:
                content += f"- {gap}\n"
        
        if report.enhancement_opportunities:
            content += """
### Enhancement Opportunities

"""
            for opportunity in report.enhancement_opportunities:
                content += f"- {opportunity}\n"
        
        return content
    
    def _generate_metrics(self, report: ProductOwnerReport) -> str:
        """Generate metrics section."""
        content = """## 📈 Key Metrics

"""
        
        if report.features_by_domain:
            content += """### Features by Business Domain

"""
            for domain, count in sorted(report.features_by_domain.items()):
                domain_name = domain.replace('_', ' ').title()
                content += f"- **{domain_name}:** {count} feature{'s' if count != 1 else ''}\n"
        
        completion_percentage = int(report.completion_score * 100)
        content += f"""
### Development Metrics
- **Total Features:** {len(report.identified_features)}
- **Total API Endpoints:** {report.total_endpoints}
- **Feature Completion Score:** {completion_percentage}%
- **Security Features:** {len(report.security_features)}
- **Integration Points:** {len(report.integration_points)}
- **Identified Risks:** {len(report.risk_assessments)}"""
        
        return content
    
    def _generate_footer(self) -> str:
        """Generate report footer."""
        return f"""---

## About This Report

This automated analysis was generated by the Postman Collection Generator MCP Server's business analysis capabilities. The report combines automated code analysis with business intelligence patterns to provide Product Owner-focused insights.

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}

**Note:** This analysis is based on code structure, patterns, and documentation. Manual review by technical and business stakeholders is recommended for comprehensive understanding."""
    
    # Helper methods
    def _get_overall_risk_level(self, report: ProductOwnerReport) -> str:
        """Determine overall risk level."""
        if not report.risk_assessments:
            return "Low (No risks detected)"
        
        risk_levels = [r.risk_level for r in report.risk_assessments]
        
        if RiskLevel.CRITICAL in risk_levels:
            return "Critical"
        elif RiskLevel.HIGH in risk_levels:
            return "High"
        elif RiskLevel.MEDIUM in risk_levels:
            return "Medium"
        else:
            return "Low"
    
    def _interpret_tech_for_business(self, tech) -> str:
        """Interpret technology stack for business stakeholders."""
        if tech.framework:
            framework_speeds = {
                'FastAPI': 'Very fast development with modern Python',
                'Spring Boot': 'Enterprise-grade with robust ecosystem',
                'Express': 'Rapid prototyping and lightweight development',
                'React': 'Modern, maintainable user interfaces',
                'Django': 'Rapid development with built-in features'
            }
            return framework_speeds.get(tech.framework, 'Standard development framework')
        else:
            return 'Custom implementation may require more development time'
    
    def _interpret_scalability(self, tech) -> str:
        """Interpret scalability implications."""
        if tech.architecture_pattern == 'microservice':
            return 'Excellent - designed for high scalability'
        elif tech.database_type in ['PostgreSQL', 'MongoDB']:
            return 'Good - uses scalable database technology'
        else:
            return 'Standard - suitable for typical business needs'
    
    def _interpret_maintenance(self, tech) -> str:
        """Interpret maintenance implications."""
        if tech.dependencies_count > 100:
            return 'Complex - many dependencies require careful management'
        elif tech.dependencies_count > 50:
            return 'Moderate - standard complexity for modern applications'
        else:
            return 'Simple - minimal dependencies make maintenance easier'
    
    def _format_list_items(self, items: list, empty_message: str) -> str:
        """Format list items or return empty message."""
        if items:
            return '\n'.join(f"- {item}" for item in items)
        else:
            return empty_message
    
    def _interpret_development_speed(self, insights) -> str:
        """Interpret development speed indicators."""
        if 'CI/CD pipeline configured' in insights.development_velocity_indicators:
            return 'Fast - automated deployment pipeline enables rapid releases'
        elif 'Automated testing in place' in insights.development_velocity_indicators:
            return 'Good - automated testing supports confident development'
        else:
            return 'Standard - manual processes may slow development'
    
    def _interpret_release_readiness(self, insights) -> str:
        """Interpret release readiness."""
        readiness_score = 0
        if 'production-ready' in insights.deployment_readiness.lower():
            readiness_score += 2
        if 'comprehensive testing' in insights.testing_coverage.lower():
            readiness_score += 2
        if 'well-documented' in insights.documentation_quality.lower():
            readiness_score += 1
        
        if readiness_score >= 4:
            return 'Ready - system appears production-ready'
        elif readiness_score >= 2:
            return 'Nearly ready - minor preparation needed'
        else:
            return 'Needs preparation - additional work required before release'
    
    def _interpret_maintenance_outlook(self, insights) -> str:
        """Interpret future maintenance outlook."""
        if not insights.technical_debt_indicators:
            return 'Excellent - clean codebase should be easy to maintain'
        elif len(insights.technical_debt_indicators) <= 2:
            return 'Good - some technical debt but manageable'
        else:
            return 'Challenging - significant technical debt may impact future development'