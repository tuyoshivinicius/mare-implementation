"""
MARE CLI - Checker Agent Implementation
Agent responsible for verifying quality, completeness and consistency of requirements
"""

from typing import Any, Dict, List
from mare.agents.base import AbstractAgent, AgentRole, ActionType, AgentConfig


class CheckerAgent(AbstractAgent):
    """
    Checker Agent implementation.
    
    This agent is responsible for:
    - Checking requirements quality and consistency (CheckRequirement)
    - Writing check reports with findings and recommendations (WriteCheckReport)
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the Checker Agent."""
        # Ensure the role is set correctly
        config.role = AgentRole.CHECKER
        
        # Set default system prompt if not provided
        if not config.system_prompt:
            config.system_prompt = self.get_system_prompt()
        
        super().__init__(config)
    
    def can_perform_action(self, action_type: ActionType) -> bool:
        """Check if this agent can perform the specified action."""
        allowed_actions = {
            ActionType.CHECK_REQUIREMENT,
            ActionType.WRITE_CHECK_REPORT
        }
        return action_type in allowed_actions
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the Checker Agent."""
        return """You are an experienced requirements quality assurance specialist. Your role is to:

1. Analyze requirements for quality, completeness, consistency, and correctness
2. Identify gaps, ambiguities, conflicts, and potential issues
3. Provide detailed feedback and recommendations for improvement
4. Ensure requirements meet industry standards and best practices

Quality Criteria to Evaluate:

COMPLETENESS:
- Are all functional requirements covered?
- Are non-functional requirements specified?
- Are all user scenarios addressed?
- Are edge cases and error conditions covered?

CONSISTENCY:
- Are requirements internally consistent?
- Do requirements conflict with each other?
- Is terminology used consistently?
- Are assumptions and constraints aligned?

CLARITY:
- Are requirements unambiguous?
- Is language clear and precise?
- Are acceptance criteria well-defined?
- Can requirements be understood by all stakeholders?

CORRECTNESS:
- Do requirements accurately reflect user needs?
- Are technical specifications feasible?
- Are business rules correctly captured?
- Are dependencies properly identified?

TESTABILITY:
- Can requirements be verified/tested?
- Are acceptance criteria measurable?
- Are success criteria clearly defined?

TRACEABILITY:
- Can requirements be traced to user stories?
- Are relationships between requirements clear?
- Is impact analysis possible?

Your analysis should be thorough, constructive, and actionable."""
    
    def _execute_specific_action(
        self, 
        action_type: ActionType, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific action implementation."""
        
        if action_type == ActionType.CHECK_REQUIREMENT:
            return self._check_requirement(input_data)
        elif action_type == ActionType.WRITE_CHECK_REPORT:
            return self._write_check_report(input_data)
        else:
            raise ValueError(f"Unsupported action type: {action_type}")
    
    def _check_requirement(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check requirements for quality and consistency.
        
        Args:
            input_data: Should contain 'requirements', 'entities', 'relationships'
            
        Returns:
            Dictionary containing check results
        """
        requirements = input_data.get('requirements', '')
        entities = input_data.get('entities', '')
        relationships = input_data.get('relationships', '')
        user_stories = input_data.get('user_stories', '')
        domain = input_data.get('domain', 'general software system')
        check_focus = input_data.get('check_focus', 'comprehensive')
        
        prompt_template = """Perform a comprehensive quality check on the following requirements artifacts. Analyze for completeness, consistency, clarity, correctness, and testability.

Requirements: {requirements}

Entities: {entities}

Relationships: {relationships}

Original User Stories: {user_stories}

Domain: {domain}

Check Focus: {check_focus}

Please provide a detailed analysis covering:

1. COMPLETENESS ANALYSIS
   - Missing functional requirements
   - Missing non-functional requirements
   - Uncovered user scenarios
   - Missing edge cases and error handling
   - Score: [1-10] with justification

2. CONSISTENCY ANALYSIS
   - Internal conflicts between requirements
   - Terminology inconsistencies
   - Conflicting assumptions or constraints
   - Misaligned entities and relationships
   - Score: [1-10] with justification

3. CLARITY ANALYSIS
   - Ambiguous requirements
   - Unclear acceptance criteria
   - Vague or imprecise language
   - Missing definitions
   - Score: [1-10] with justification

4. CORRECTNESS ANALYSIS
   - Requirements that don't match user stories
   - Technically infeasible specifications
   - Incorrect business rules
   - Missing or wrong dependencies
   - Score: [1-10] with justification

5. TESTABILITY ANALYSIS
   - Requirements that cannot be tested
   - Missing measurable criteria
   - Unclear success conditions
   - Verification challenges
   - Score: [1-10] with justification

6. TRACEABILITY ANALYSIS
   - Requirements not traceable to user stories
   - Missing requirement relationships
   - Orphaned or duplicate requirements
   - Impact analysis gaps
   - Score: [1-10] with justification

7. OVERALL ASSESSMENT
   - Overall Quality Score: [1-10]
   - Ready for Implementation: [Yes/No]
   - Critical Issues Count: [number]
   - Major Issues Count: [number]
   - Minor Issues Count: [number]

For each issue identified, provide:
- Issue ID (e.g., COMP-001, CONS-001)
- Severity: Critical/Major/Minor
- Description: What the issue is
- Impact: How it affects the project
- Recommendation: How to fix it
- Location: Where in the requirements it occurs"""
        
        prompt = self._format_prompt(prompt_template, {
            'requirements': requirements,
            'entities': entities,
            'relationships': relationships,
            'user_stories': user_stories,
            'domain': domain,
            'check_focus': check_focus
        })
        
        response = self._generate_response(prompt)
        
        return {
            'check_results': response,
            'domain': domain,
            'check_focus': check_focus,
            'artifacts_checked': ['requirements', 'entities', 'relationships'],
            'quality_dimensions': ['completeness', 'consistency', 'clarity', 'correctness', 'testability', 'traceability']
        }
    
    def _write_check_report(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a comprehensive check report.
        
        Args:
            input_data: Should contain 'check_results' and context
            
        Returns:
            Dictionary containing formatted check report
        """
        check_results = input_data.get('check_results', '')
        project_name = input_data.get('project_name', 'Unnamed Project')
        domain = input_data.get('domain', 'general software system')
        report_type = input_data.get('report_type', 'comprehensive')
        
        prompt_template = """Based on the quality check results, create a professional requirements quality assurance report. Format it as a comprehensive document suitable for stakeholders and development teams.

Check Results: {check_results}

Project Name: {project_name}
Domain: {domain}
Report Type: {report_type}

Please create a structured report with the following sections:

# Requirements Quality Assurance Report

## Executive Summary
- Overall quality assessment
- Key findings summary
- Recommendations overview
- Go/No-Go decision

## Project Information
- Project: {project_name}
- Domain: {domain}
- Review Date: [current date]
- Review Type: {report_type}

## Quality Metrics Summary
- Completeness Score: [score/10]
- Consistency Score: [score/10]
- Clarity Score: [score/10]
- Correctness Score: [score/10]
- Testability Score: [score/10]
- Traceability Score: [score/10]
- **Overall Quality Score: [score/10]**

## Issues Summary
- Critical Issues: [count]
- Major Issues: [count]
- Minor Issues: [count]
- Total Issues: [count]

## Detailed Findings

### Critical Issues
[List all critical issues with ID, description, impact, and recommendations]

### Major Issues
[List all major issues with ID, description, impact, and recommendations]

### Minor Issues
[List all minor issues with ID, description, impact, and recommendations]

## Quality Analysis by Dimension

### Completeness Analysis
[Detailed analysis of completeness]

### Consistency Analysis
[Detailed analysis of consistency]

### Clarity Analysis
[Detailed analysis of clarity]

### Correctness Analysis
[Detailed analysis of correctness]

### Testability Analysis
[Detailed analysis of testability]

### Traceability Analysis
[Detailed analysis of traceability]

## Recommendations

### Immediate Actions Required
[Critical and major issues that must be addressed]

### Improvement Opportunities
[Minor issues and enhancement suggestions]

### Process Improvements
[Recommendations for improving the requirements process]

## Conclusion
- Overall assessment
- Readiness for next phase
- Risk assessment
- Sign-off recommendation

## Appendices
- Detailed issue list
- Quality criteria definitions
- Review methodology

---
*This report was generated by the MARE Requirements Quality Checker*"""
        
        prompt = self._format_prompt(prompt_template, {
            'check_results': check_results,
            'project_name': project_name,
            'domain': domain,
            'report_type': report_type
        })
        
        response = self._generate_response(prompt)
        
        return {
            'check_report': response,
            'project_name': project_name,
            'domain': domain,
            'report_type': report_type,
            'report_sections': [
                'executive_summary', 'project_info', 'quality_metrics', 
                'issues_summary', 'detailed_findings', 'quality_analysis',
                'recommendations', 'conclusion', 'appendices'
            ]
        }
    
    def perform_quality_check(
        self, 
        requirements: str,
        entities: str = "",
        relationships: str = "",
        user_stories: str = "",
        domain: str = "general software system",
        check_focus: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Convenience method to perform a quality check.
        
        Args:
            requirements: Requirements to check
            entities: Extracted entities
            relationships: Extracted relationships
            user_stories: Original user stories
            domain: Domain context
            check_focus: Focus area for checking
            
        Returns:
            Action result with check results
        """
        action = self.execute_action(
            ActionType.CHECK_REQUIREMENT,
            {
                'requirements': requirements,
                'entities': entities,
                'relationships': relationships,
                'user_stories': user_stories,
                'domain': domain,
                'check_focus': check_focus
            }
        )
        return action.output_data
    
    def generate_quality_report(
        self, 
        check_results: str,
        project_name: str = "Unnamed Project",
        domain: str = "general software system",
        report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Convenience method to generate a quality report.
        
        Args:
            check_results: Results from quality check
            project_name: Name of the project
            domain: Domain context
            report_type: Type of report to generate
            
        Returns:
            Action result with formatted report
        """
        action = self.execute_action(
            ActionType.WRITE_CHECK_REPORT,
            {
                'check_results': check_results,
                'project_name': project_name,
                'domain': domain,
                'report_type': report_type
            }
        )
        return action.output_data

