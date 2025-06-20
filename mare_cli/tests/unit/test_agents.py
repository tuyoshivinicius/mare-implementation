"""
MARE CLI - Unit Tests for Agents
Test suite for validating MARE agent implementations
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

from mare.agents import (
    AgentFactory, AgentRole, ActionType, AgentConfig,
    StakeholderAgent, CollectorAgent, ModelerAgent, CheckerAgent, DocumenterAgent
)
from mare.utils.exceptions import ConfigurationError


class TestAgentFactory(unittest.TestCase):
    """Test cases for AgentFactory."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = AgentConfig(
            role=AgentRole.STAKEHOLDER,
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=2048
        )
    
    def test_create_agent_success(self):
        """Test successful agent creation."""
        with patch('mare.agents.base.ChatOpenAI') as mock_llm:
            mock_llm.return_value = Mock()
            
            agent = AgentFactory.create_agent(AgentRole.STAKEHOLDER, self.test_config)
            
            self.assertIsInstance(agent, StakeholderAgent)
            self.assertEqual(agent.config.role, AgentRole.STAKEHOLDER)
    
    def test_create_agent_invalid_role(self):
        """Test agent creation with invalid role."""
        # Create a mock role that doesn't exist in AGENT_CLASSES
        with patch('mare.agents.factory.AgentFactory.AGENT_CLASSES', {}):
            with self.assertRaises(ConfigurationError):
                AgentFactory.create_agent(AgentRole.STAKEHOLDER, self.test_config)
    
    def test_create_agent_from_dict(self):
        """Test agent creation from configuration dictionary."""
        config_dict = {
            'model': 'gpt-3.5-turbo',
            'temperature': 0.7,
            'max_tokens': 2048,
            'enabled': True
        }
        
        with patch('mare.agents.base.ChatOpenAI') as mock_llm:
            mock_llm.return_value = Mock()
            
            agent = AgentFactory.create_agent_from_dict(AgentRole.COLLECTOR, config_dict)
            
            self.assertIsInstance(agent, CollectorAgent)
            self.assertEqual(agent.config.model_name, 'gpt-3.5-turbo')
    
    def test_get_default_config(self):
        """Test getting default configuration for agent roles."""
        config = AgentFactory.get_default_config(AgentRole.MODELER)
        
        self.assertEqual(config.role, AgentRole.MODELER)
        self.assertEqual(config.model_name, "gpt-4")  # Modeler uses GPT-4 by default
        self.assertEqual(config.temperature, 0.5)
    
    def test_validate_agent_config_success(self):
        """Test successful configuration validation."""
        result = AgentFactory.validate_agent_config(self.test_config)
        self.assertTrue(result)
    
    def test_validate_agent_config_invalid_temperature(self):
        """Test configuration validation with invalid temperature."""
        invalid_config = AgentConfig(
            role=AgentRole.STAKEHOLDER,
            model_name="gpt-3.5-turbo",
            temperature=3.0,  # Invalid temperature
            max_tokens=2048
        )
        
        with self.assertRaises(ConfigurationError):
            AgentFactory.validate_agent_config(invalid_config)
    
    def test_validate_agent_config_invalid_max_tokens(self):
        """Test configuration validation with invalid max_tokens."""
        invalid_config = AgentConfig(
            role=AgentRole.STAKEHOLDER,
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=-100  # Invalid max_tokens
        )
        
        with self.assertRaises(ConfigurationError):
            AgentFactory.validate_agent_config(invalid_config)


class TestStakeholderAgent(unittest.TestCase):
    """Test cases for StakeholderAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = AgentConfig(
            role=AgentRole.STAKEHOLDER,
            model_name="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=2048
        )
        
        with patch('mare.agents.base.ChatOpenAI') as mock_llm:
            mock_llm.return_value = Mock()
            self.agent = StakeholderAgent(self.config)
    
    def test_can_perform_action(self):
        """Test action capability checking."""
        self.assertTrue(self.agent.can_perform_action(ActionType.EXPRESS_REQUIREMENT))
        self.assertTrue(self.agent.can_perform_action(ActionType.RESPOND_TO_QUESTION))
        self.assertFalse(self.agent.can_perform_action(ActionType.EXTRACT_ENTITY))
    
    def test_express_initial_requirements(self):
        """Test expressing initial requirements."""
        with patch.object(self.agent, '_generate_response') as mock_generate:
            mock_generate.return_value = "User story 1\nUser story 2"
            
            result = self.agent.express_initial_requirements(
                "Build a web application",
                "e-commerce"
            )
            
            self.assertIn("user_stories", result)
            self.assertEqual(result["user_stories"], "User story 1\nUser story 2")
    
    def test_respond_to_question(self):
        """Test responding to questions."""
        with patch.object(self.agent, '_generate_response') as mock_generate:
            mock_generate.return_value = "Yes, the system should support multiple payment methods."
            
            result = self.agent.respond_to_question(
                "Should the system support multiple payment methods?",
                context="e-commerce system"
            )
            
            self.assertIn("answer", result)
            self.assertIn("payment methods", result["answer"])


class TestCollectorAgent(unittest.TestCase):
    """Test cases for CollectorAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = AgentConfig(
            role=AgentRole.COLLECTOR,
            model_name="gpt-3.5-turbo",
            temperature=0.6,
            max_tokens=2048
        )
        
        with patch('mare.agents.base.ChatOpenAI') as mock_llm:
            mock_llm.return_value = Mock()
            self.agent = CollectorAgent(self.config)
    
    def test_can_perform_action(self):
        """Test action capability checking."""
        self.assertTrue(self.agent.can_perform_action(ActionType.ANALYZE_AND_QUESTION))
        self.assertTrue(self.agent.can_perform_action(ActionType.DRAFT_REQUIREMENT))
        self.assertFalse(self.agent.can_perform_action(ActionType.CHECK_REQUIREMENT))
    
    def test_analyze_and_question(self):
        """Test analyzing requirements and generating questions."""
        with patch.object(self.agent, '_generate_response') as mock_generate:
            mock_generate.return_value = "Question 1: What payment methods?\nQuestion 2: How many users?"
            
            result = self.agent.analyze_and_question(
                "User wants an e-commerce system",
                "e-commerce"
            )
            
            self.assertIn("questions", result)
            self.assertIn("Question 1", result["questions"])
    
    def test_draft_requirements(self):
        """Test drafting requirements from Q&A."""
        with patch.object(self.agent, '_generate_response') as mock_generate:
            mock_generate.return_value = "REQ-001: System shall support credit card payments"
            
            result = self.agent.draft_requirements(
                "User wants payment system",
                "Q: Payment methods? A: Credit cards",
                "e-commerce"
            )
            
            self.assertIn("requirements_draft", result)
            self.assertIn("REQ-001", result["requirements_draft"])


class TestModelerAgent(unittest.TestCase):
    """Test cases for ModelerAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = AgentConfig(
            role=AgentRole.MODELER,
            model_name="gpt-4",
            temperature=0.5,
            max_tokens=2048
        )
        
        with patch('mare.agents.base.ChatOpenAI') as mock_llm:
            mock_llm.return_value = Mock()
            self.agent = ModelerAgent(self.config)
    
    def test_can_perform_action(self):
        """Test action capability checking."""
        self.assertTrue(self.agent.can_perform_action(ActionType.EXTRACT_ENTITY))
        self.assertTrue(self.agent.can_perform_action(ActionType.EXTRACT_RELATIONSHIP))
        self.assertFalse(self.agent.can_perform_action(ActionType.WRITE_SRS))
    
    def test_extract_system_entities(self):
        """Test extracting system entities."""
        with patch.object(self.agent, '_generate_response') as mock_generate:
            mock_generate.return_value = "Entity: User\nEntity: Product\nEntity: Order"
            
            result = self.agent.extract_system_entities(
                "System manages users, products, and orders",
                "e-commerce"
            )
            
            self.assertIn("entities", result)
            self.assertIn("User", result["entities"])
            self.assertIn("Product", result["entities"])
    
    def test_extract_entity_relationships(self):
        """Test extracting entity relationships."""
        with patch.object(self.agent, '_generate_response') as mock_generate:
            mock_generate.return_value = "User places Order\nOrder contains Product"
            
            result = self.agent.extract_entity_relationships(
                "User, Product, Order",
                "Users place orders containing products",
                "e-commerce"
            )
            
            self.assertIn("relationships", result)
            self.assertIn("places", result["relationships"])


class TestCheckerAgent(unittest.TestCase):
    """Test cases for CheckerAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = AgentConfig(
            role=AgentRole.CHECKER,
            model_name="gpt-4",
            temperature=0.3,
            max_tokens=2048
        )
        
        with patch('mare.agents.base.ChatOpenAI') as mock_llm:
            mock_llm.return_value = Mock()
            self.agent = CheckerAgent(self.config)
    
    def test_can_perform_action(self):
        """Test action capability checking."""
        self.assertTrue(self.agent.can_perform_action(ActionType.CHECK_REQUIREMENT))
        self.assertTrue(self.agent.can_perform_action(ActionType.WRITE_CHECK_REPORT))
        self.assertFalse(self.agent.can_perform_action(ActionType.EXPRESS_REQUIREMENT))
    
    def test_perform_quality_check(self):
        """Test performing quality check."""
        with patch.object(self.agent, '_generate_response') as mock_generate:
            mock_generate.return_value = "Overall Quality Score: 8.5/10\nCompleteness: Good"
            
            result = self.agent.perform_quality_check(
                "REQ-001: System shall support payments",
                "User, Payment",
                "User makes Payment",
                "User wants payment system"
            )
            
            self.assertIn("check_results", result)
            self.assertIn("Quality Score", result["check_results"])


class TestDocumenterAgent(unittest.TestCase):
    """Test cases for DocumenterAgent."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = AgentConfig(
            role=AgentRole.DOCUMENTER,
            model_name="gpt-3.5-turbo",
            temperature=0.4,
            max_tokens=4096
        )
        
        with patch('mare.agents.base.ChatOpenAI') as mock_llm:
            mock_llm.return_value = Mock()
            self.agent = DocumenterAgent(self.config)
    
    def test_can_perform_action(self):
        """Test action capability checking."""
        self.assertTrue(self.agent.can_perform_action(ActionType.WRITE_SRS))
        self.assertTrue(self.agent.can_perform_action(ActionType.WRITE_CHECK_REPORT))
        self.assertFalse(self.agent.can_perform_action(ActionType.EXTRACT_ENTITY))
    
    def test_generate_srs_document(self):
        """Test generating SRS document."""
        with patch.object(self.agent, '_generate_response') as mock_generate:
            mock_generate.return_value = "# Software Requirements Specification\n## 1. Introduction"
            
            result = self.agent.generate_srs_document(
                "REQ-001: Payment support",
                "User, Payment",
                "User makes Payment",
                "User wants payment system",
                "Quality check passed",
                "E-commerce System"
            )
            
            self.assertIn("srs_document", result)
            self.assertIn("Software Requirements Specification", result["srs_document"])


if __name__ == '__main__':
    unittest.main()

