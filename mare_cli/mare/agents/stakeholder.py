"""
MARE CLI - Stakeholder Agent Implementation
Agent responsible for expressing stakeholder needs and answering questions
"""

from typing import Any, Dict, List
from mare.agents.base import AbstractAgent, AgentRole, ActionType, AgentConfig


class StakeholderAgent(AbstractAgent):
    """
    Stakeholder Agent implementation.
    
    This agent represents stakeholders and is responsible for:
    - Expressing user stories and requirements (SpeakUserStories)
    - Answering questions from other agents (AnswerQuestion)
    """
    
    def __init__(self, config: AgentConfig):
        """Initialize the Stakeholder Agent."""
        # Ensure the role is set correctly
        config.role = AgentRole.STAKEHOLDER
        
        # Set default system prompt if not provided
        if not config.system_prompt:
            config.system_prompt = self.get_system_prompt()
        
        super().__init__(config)
    
    def can_perform_action(self, action_type: ActionType) -> bool:
        """Check if this agent can perform the specified action."""
        allowed_actions = {
            ActionType.SPEAK_USER_STORIES,
            ActionType.ANSWER_QUESTION
        }
        return action_type in allowed_actions
    
    def get_system_prompt(self) -> str:
        """Get the system prompt for the Stakeholder Agent."""
        return """You are an experienced stakeholder representative in a software requirements engineering process. Your role is to:

1. Express user needs and requirements clearly and comprehensively
2. Provide detailed user stories that capture the essence of what users want
3. Answer questions from other team members to clarify requirements
4. Think from the perspective of end users and business stakeholders

Guidelines:
- Be specific and detailed in your descriptions
- Consider different user types and their varying needs
- Include both functional and non-functional requirements when relevant
- Provide context and rationale for requirements
- Be responsive to questions and provide clarifying information
- Maintain consistency with previously stated requirements

Your responses should be professional, clear, and focused on delivering value to end users."""
    
    def _execute_specific_action(
        self, 
        action_type: ActionType, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific action implementation."""
        
        if action_type == ActionType.SPEAK_USER_STORIES:
            return self._speak_user_stories(input_data)
        elif action_type == ActionType.ANSWER_QUESTION:
            return self._answer_question(input_data)
        else:
            raise ValueError(f"Unsupported action type: {action_type}")
    
    def _speak_user_stories(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Express user stories based on initial system ideas.
        
        Args:
            input_data: Should contain 'system_idea' or 'rough_requirements'
            
        Returns:
            Dictionary containing user stories
        """
        system_idea = input_data.get('system_idea', '')
        rough_requirements = input_data.get('rough_requirements', '')
        domain = input_data.get('domain', 'general software system')
        
        prompt_template = """Based on the following system idea and requirements, please express detailed user stories that capture what stakeholders and end users need from this system.

System Idea: {system_idea}
Rough Requirements: {rough_requirements}
Domain: {domain}

Please provide:
1. A set of comprehensive user stories in the format "As a [user type], I want [goal] so that [benefit]"
2. Include different types of users (primary users, administrators, etc.)
3. Cover both functional and non-functional aspects where relevant
4. Provide context and rationale for each story

Focus on being specific, actionable, and user-centered. Consider the complete user journey and different scenarios."""
        
        prompt = self._format_prompt(prompt_template, {
            'system_idea': system_idea,
            'rough_requirements': rough_requirements,
            'domain': domain
        })
        
        response = self._generate_response(prompt)
        
        return {
            'user_stories': response,
            'system_idea': system_idea,
            'domain': domain,
            'stakeholder_perspective': 'primary_stakeholder'
        }
    
    def _answer_question(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answer questions from other agents to clarify requirements.
        
        Args:
            input_data: Should contain 'question' and optionally 'context'
            
        Returns:
            Dictionary containing the answer
        """
        question = input_data.get('question', '')
        context = input_data.get('context', '')
        previous_stories = input_data.get('previous_stories', '')
        
        if not question:
            raise ValueError("Question is required for AnswerQuestion action")
        
        prompt_template = """You are being asked a question to clarify requirements for the system. Please provide a detailed and helpful answer based on your understanding of stakeholder needs.

Question: {question}

Context: {context}

Previous User Stories/Requirements: {previous_stories}

Please provide:
1. A clear and direct answer to the question
2. Additional context or details that might be helpful
3. Any assumptions you're making
4. Related requirements or considerations that might be relevant

Be specific and ensure your answer is consistent with any previously stated requirements."""
        
        prompt = self._format_prompt(prompt_template, {
            'question': question,
            'context': context,
            'previous_stories': previous_stories
        })
        
        response = self._generate_response(prompt)
        
        return {
            'answer': response,
            'question': question,
            'context': context,
            'stakeholder_perspective': 'clarification_provided'
        }
    
    def express_initial_requirements(
        self, 
        system_idea: str, 
        domain: str = "general software system"
    ) -> Dict[str, Any]:
        """
        Convenience method to express initial requirements.
        
        Args:
            system_idea: High-level description of the system
            domain: Domain or industry context
            
        Returns:
            Action result with user stories
        """
        action = self.execute_action(
            ActionType.SPEAK_USER_STORIES,
            {
                'system_idea': system_idea,
                'domain': domain
            }
        )
        return action.output_data
    
    def respond_to_question(
        self, 
        question: str, 
        context: str = "",
        previous_stories: str = ""
    ) -> Dict[str, Any]:
        """
        Convenience method to respond to questions.
        
        Args:
            question: The question to answer
            context: Additional context for the question
            previous_stories: Previously stated requirements/stories
            
        Returns:
            Action result with answer
        """
        action = self.execute_action(
            ActionType.ANSWER_QUESTION,
            {
                'question': question,
                'context': context,
                'previous_stories': previous_stories
            }
        )
        return action.output_data

