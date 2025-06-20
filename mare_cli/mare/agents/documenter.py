"""
MARE CLI - Documenter Agent Implementation
Agent responsible for generating final specifications and documentation
"""

from typing import Any, Dict, List
from mare.agents.base import AbstractAgent, AgentRole, ActionType, AgentConfig


class DocumenterAgent(AbstractAgent):
    """
    Documenter Agent implementation.
    
    This agent is responsible for:
    - Writing Software Requirements Specification (WriteSRS)
    - Writing check reports when quality issues are found (WriteCheckReport)
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the Documenter Agent."""
        # Ensure the role is set correctly
        config.role = AgentRole.DOCUMENTER
        
        # Set default system prompt if not provided
        if not config.system_prompt:
            config.system_prompt = self.get_system_prompt()
        
        super().__init__(config)
    
    def can_perform_action(self, action_type: ActionType) -> bool:
        """Check if this agent can perform the specified action."""
        allowed_actions = {
            ActionType.WRITE_SRS,
            ActionType.WRITE_CHECK_REPORT
        }
        return action_type in allowed_actions
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the Documenter Agent."""
        return """You are an experienced technical writer specializing in software requirements documentation. Your role is to:

1. Create comprehensive Software Requirements Specifications (SRS) that follow industry standards
2. Transform technical requirements into clear, professional documentation
3. Ensure documentation is complete, well-structured, and accessible to all stakeholders
4. Generate problem reports when quality issues prevent proper documentation

SRS Documentation Standards:
- Follow IEEE 830 standard for SRS structure and content
- Use clear, unambiguous language suitable for both technical and non-technical audiences
- Include comprehensive traceability matrices
- Provide detailed functional and non-functional requirements
- Include system models, diagrams, and specifications
- Ensure consistency in terminology and formatting

Documentation Principles:
- Clarity: Use simple, direct language
- Completeness: Cover all aspects of the system
- Consistency: Maintain uniform style and terminology
- Correctness: Ensure technical accuracy
- Conciseness: Avoid unnecessary complexity
- Verifiability: Make requirements testable

Your output should be professional, well-organized, and suitable for use by development teams, testers, and project stakeholders."""
    
    def _execute_specific_action(
        self, 
        action_type: ActionType, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific action implementation."""
        
        if action_type == ActionType.WRITE_SRS:
            return self._write_srs(input_data)
        elif action_type == ActionType.WRITE_CHECK_REPORT:
            return self._write_check_report(input_data)
        else:
            raise ValueError(f"Unsupported action type: {action_type}")
    
    def _write_srs(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a comprehensive Software Requirements Specification.
        
        Args:
            input_data: Should contain all requirements artifacts
            
        Returns:
            Dictionary containing the SRS document
        """
        requirements = input_data.get('requirements', '')
        entities = input_data.get('entities', '')
        relationships = input_data.get('relationships', '')
        user_stories = input_data.get('user_stories', '')
        check_results = input_data.get('check_results', '')
        project_name = input_data.get('project_name', 'Software System')
        domain = input_data.get('domain', 'general software system')
        version = input_data.get('version', '1.0')
        
        prompt_template = """Create a comprehensive Software Requirements Specification (SRS) document following IEEE 830 standards. Use all provided artifacts to create a complete, professional specification.

Project Name: {project_name}
Domain: {domain}
Version: {version}

User Stories: {user_stories}
Requirements: {requirements}
Entities: {entities}
Relationships: {relationships}
Quality Check Results: {check_results}

Please create a complete SRS document with the following structure:

# Software Requirements Specification
## {project_name}

### Document Information
- **Document Title:** Software Requirements Specification for {project_name}
- **Version:** {version}
- **Date:** [Current Date]
- **Domain:** {domain}
- **Status:** Draft/Final

---

## Table of Contents
1. Introduction
2. Overall Description
3. System Features
4. External Interface Requirements
5. Non-Functional Requirements
6. System Models
7. Verification and Validation
8. Appendices

---

## 1. Introduction

### 1.1 Purpose
[Purpose of this SRS document and intended audience]

### 1.2 Scope
[Scope of the software system being specified]

### 1.3 Definitions, Acronyms, and Abbreviations
[Key terms and definitions used throughout the document]

### 1.4 References
[Referenced documents and standards]

### 1.5 Overview
[Overview of the remainder of the SRS]

## 2. Overall Description

### 2.1 Product Perspective
[How this system relates to other systems and the overall environment]

### 2.2 Product Functions
[Summary of major functions the software will perform]

### 2.3 User Classes and Characteristics
[Different types of users and their characteristics]

### 2.4 Operating Environment
[Hardware, software, and technology environment]

### 2.5 Design and Implementation Constraints
[Constraints that affect the design and implementation]

### 2.6 Assumptions and Dependencies
[Assumptions made and external dependencies]

## 3. System Features

### 3.1 Functional Requirements
[Detailed functional requirements organized by feature]

For each functional requirement, include:
- **Requirement ID:** FR-XXX
- **Title:** [Requirement title]
- **Description:** [Detailed description]
- **Priority:** High/Medium/Low
- **Source:** [Traceability to user story]
- **Acceptance Criteria:** [How to verify the requirement]

### 3.2 Business Rules
[Business rules that govern system behavior]

## 4. External Interface Requirements

### 4.1 User Interfaces
[User interface requirements]

### 4.2 Hardware Interfaces
[Hardware interface requirements]

### 4.3 Software Interfaces
[Software interface requirements]

### 4.4 Communication Interfaces
[Communication interface requirements]

## 5. Non-Functional Requirements

### 5.1 Performance Requirements
[Performance and scalability requirements]

### 5.2 Security Requirements
[Security and access control requirements]

### 5.3 Reliability Requirements
[Reliability and availability requirements]

### 5.4 Usability Requirements
[Usability and user experience requirements]

### 5.5 Maintainability Requirements
[Maintenance and support requirements]

### 5.6 Portability Requirements
[Portability and compatibility requirements]

## 6. System Models

### 6.1 Data Model
[Data entities and their relationships based on extracted entities]

### 6.2 Process Model
[System processes and workflows]

### 6.3 System Architecture
[High-level system architecture]

## 7. Verification and Validation

### 7.1 Verification Methods
[How requirements will be verified]

### 7.2 Validation Criteria
[Criteria for validating the system meets user needs]

### 7.3 Test Requirements
[Testing requirements and strategies]

## 8. Appendices

### Appendix A: Traceability Matrix
[Requirements traceability to user stories]

### Appendix B: Glossary
[Complete glossary of terms]

### Appendix C: Quality Assessment
[Summary of quality check results if available]

---

**Document Control:**
- Created by: MARE Requirements Engineering Framework
- Review Status: [Pending/Approved]
- Next Review Date: [Date]

Ensure the document is:
- Complete and comprehensive
- Well-structured and professional
- Traceable to original user stories
- Technically accurate and feasible
- Clear and understandable to all stakeholders"""
        
        prompt = self._format_prompt(prompt_template, {
            'project_name': project_name,
            'domain': domain,
            'version': version,
            'user_stories': user_stories,
            'requirements': requirements,
            'entities': entities,
            'relationships': relationships,
            'check_results': check_results
        })
        
        response = self._generate_response(prompt)
        
        return {
            'srs_document': response,
            'project_name': project_name,
            'domain': domain,
            'version': version,
            'document_type': 'software_requirements_specification',
            'standard': 'IEEE_830',
            'sections': [
                'introduction', 'overall_description', 'system_features',
                'external_interfaces', 'non_functional_requirements',
                'system_models', 'verification_validation', 'appendices'
            ]
        }
    
    def _write_check_report(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a check report when quality issues are found.
        
        Args:
            input_data: Should contain check results and context
            
        Returns:
            Dictionary containing the check report
        """
        check_results = input_data.get('check_results', '')
        project_name = input_data.get('project_name', 'Software Project')
        domain = input_data.get('domain', 'general software system')
        issues_summary = input_data.get('issues_summary', '')
        recommendations = input_data.get('recommendations', '')
        
        prompt_template = """Create a professional requirements quality report documenting issues found during quality assessment. This report will be used to communicate problems and guide improvement efforts.

Project Name: {project_name}
Domain: {domain}
Check Results: {check_results}
Issues Summary: {issues_summary}
Recommendations: {recommendations}

Please create a comprehensive quality report with the following structure:

# Requirements Quality Assessment Report
## {project_name}

### Executive Summary
- **Project:** {project_name}
- **Domain:** {domain}
- **Assessment Date:** [Current Date]
- **Assessment Type:** Quality Assurance Review
- **Overall Status:** [Pass/Fail/Conditional Pass]

### Key Findings
[Summary of major findings and overall quality assessment]

### Quality Issues Identified

#### Critical Issues
[Issues that must be resolved before proceeding]

#### Major Issues
[Significant issues that should be addressed]

#### Minor Issues
[Improvement opportunities and minor concerns]

### Quality Metrics
[Detailed quality scores and metrics]

### Impact Analysis
[Analysis of how issues affect project timeline and success]

### Recommendations

#### Immediate Actions
[Actions that must be taken immediately]

#### Short-term Improvements
[Improvements to be made in the near term]

#### Long-term Process Improvements
[Process improvements for future projects]

### Next Steps
[Recommended next steps and timeline]

### Approval and Sign-off
[Space for stakeholder approval]

---

**Report Details:**
- Generated by: MARE Quality Checker
- Review Required: Yes
- Distribution: [Stakeholder list]

The report should be:
- Clear and actionable
- Professional and objective
- Focused on improvement
- Suitable for management review"""
        
        prompt = self._format_prompt(prompt_template, {
            'project_name': project_name,
            'domain': domain,
            'check_results': check_results,
            'issues_summary': issues_summary,
            'recommendations': recommendations
        })
        
        response = self._generate_response(prompt)
        
        return {
            'check_report': response,
            'project_name': project_name,
            'domain': domain,
            'report_type': 'quality_assessment',
            'document_sections': [
                'executive_summary', 'key_findings', 'quality_issues',
                'quality_metrics', 'impact_analysis', 'recommendations',
                'next_steps', 'approval'
            ]
        }
    
    def generate_srs_document(
        self,
        requirements: str,
        entities: str = "",
        relationships: str = "",
        user_stories: str = "",
        check_results: str = "",
        project_name: str = "Software System",
        domain: str = "general software system",
        version: str = "1.0"
    ) -> Dict[str, Any]:
        """
        Convenience method to generate an SRS document.
        
        Args:
            requirements: System requirements
            entities: Extracted entities
            relationships: Extracted relationships
            user_stories: Original user stories
            check_results: Quality check results
            project_name: Name of the project
            domain: Domain context
            version: Document version
            
        Returns:
            Action result with SRS document
        """
        action = self.execute_action(
            ActionType.WRITE_SRS,
            {
                'requirements': requirements,
                'entities': entities,
                'relationships': relationships,
                'user_stories': user_stories,
                'check_results': check_results,
                'project_name': project_name,
                'domain': domain,
                'version': version
            }
        )
        return action.output_data
    
    def generate_quality_report(
        self,
        check_results: str,
        project_name: str = "Software Project",
        domain: str = "general software system",
        issues_summary: str = "",
        recommendations: str = ""
    ) -> Dict[str, Any]:
        """
        Convenience method to generate a quality report.
        
        Args:
            check_results: Quality check results
            project_name: Name of the project
            domain: Domain context
            issues_summary: Summary of issues found
            recommendations: Recommendations for improvement
            
        Returns:
            Action result with quality report
        """
        action = self.execute_action(
            ActionType.WRITE_CHECK_REPORT,
            {
                'check_results': check_results,
                'project_name': project_name,
                'domain': domain,
                'issues_summary': issues_summary,
                'recommendations': recommendations
            }
        )
        return action.output_data

