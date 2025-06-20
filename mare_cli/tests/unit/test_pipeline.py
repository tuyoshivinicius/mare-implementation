"""
MARE CLI - Unit Tests for Pipeline
Test suite for validating MARE pipeline implementation
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

from mare.pipeline import (
    MAREPipeline, PipelineConfig, PipelineState, 
    PipelinePhase, PipelineStatus, PipelineExecutor
)
from mare.agents import AgentRole
from mare.utils.exceptions import PipelineExecutionError


class TestPipelineConfig(unittest.TestCase):
    """Test cases for PipelineConfig."""
    
    def test_default_config(self):
        """Test default pipeline configuration."""
        config = PipelineConfig()
        
        self.assertEqual(config.max_iterations, 5)
        self.assertEqual(config.quality_threshold, 0.8)
        self.assertTrue(config.auto_advance)
        self.assertFalse(config.interactive_mode)
        self.assertIsNone(config.agent_configs)
    
    def test_custom_config(self):
        """Test custom pipeline configuration."""
        agent_configs = {
            "stakeholder": {"model": "gpt-4", "temperature": 0.5}
        }
        
        config = PipelineConfig(
            max_iterations=10,
            quality_threshold=0.9,
            auto_advance=False,
            interactive_mode=True,
            agent_configs=agent_configs
        )
        
        self.assertEqual(config.max_iterations, 10)
        self.assertEqual(config.quality_threshold, 0.9)
        self.assertFalse(config.auto_advance)
        self.assertTrue(config.interactive_mode)
        self.assertEqual(config.agent_configs, agent_configs)


class TestMAREPipeline(unittest.TestCase):
    """Test cases for MAREPipeline."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = PipelineConfig(max_iterations=3, quality_threshold=0.7)
        
        # Mock all agent creation to avoid LLM dependencies
        with patch('mare.agents.factory.AgentFactory.create_all_agents') as mock_create:
            mock_agents = {
                AgentRole.STAKEHOLDER: Mock(),
                AgentRole.COLLECTOR: Mock(),
                AgentRole.MODELER: Mock(),
                AgentRole.CHECKER: Mock(),
                AgentRole.DOCUMENTER: Mock()
            }
            mock_create.return_value = mock_agents
            
            self.pipeline = MAREPipeline(self.config)
    
    def test_pipeline_initialization(self):
        """Test pipeline initialization."""
        self.assertEqual(self.pipeline.config, self.config)
        self.assertEqual(len(self.pipeline.agents), 5)
        self.assertIsNotNone(self.pipeline.graph)
    
    def test_extract_questions_list(self):
        """Test extracting questions from text."""
        questions_text = """
        Question 1: What payment methods should be supported?
        Rationale: Need to understand payment requirements
        
        Question 2: How many concurrent users?
        Rationale: Performance requirements
        """
        
        questions = self.pipeline._extract_questions_list(questions_text)
        
        self.assertEqual(len(questions), 2)
        self.assertIn("payment methods", questions[0])
        self.assertIn("concurrent users", questions[1])
    
    def test_parse_check_results(self):
        """Test parsing check results."""
        check_results = """
        Overall Quality Score: 8.5/10
        Critical Issues Count: 0
        Major Issues Count: 2
        """
        
        quality_score, issues = self.pipeline._parse_check_results(check_results)
        
        self.assertEqual(quality_score, 8.5)
        self.assertEqual(len(issues), 2)
    
    def test_should_continue_iterations(self):
        """Test iteration control logic."""
        # Test quality threshold met
        state = {
            "quality_score": 8.5,
            "iteration_count": 2
        }
        self.pipeline.config.quality_threshold = 8.0
        self.pipeline.config.max_iterations = 5
        
        result = self.pipeline._should_continue_iterations(state)
        self.assertEqual(result, "specification")
        
        # Test max iterations reached
        state["quality_score"] = 6.0
        state["iteration_count"] = 5
        
        result = self.pipeline._should_continue_iterations(state)
        self.assertEqual(result, "specification")
        
        # Test continue iterations
        state["iteration_count"] = 2
        
        result = self.pipeline._should_continue_iterations(state)
        self.assertEqual(result, "continue")


class TestPipelineExecutor(unittest.TestCase):
    """Test cases for PipelineExecutor."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_path = self.temp_dir / "test_project"
        self.project_path.mkdir(parents=True)
        
        # Create minimal project structure
        (self.project_path / ".mare").mkdir()
        (self.project_path / ".mare" / "workspace").mkdir()
        
        # Create config file
        config_content = """
project:
  name: "Test Project"
  template: "basic"
  domain: "test"

llm:
  provider: "openai"
  model: "gpt-3.5-turbo"

pipeline:
  max_iterations: 3
  quality_threshold: 0.7

agents:
  stakeholder:
    enabled: true
    model: "gpt-3.5-turbo"
  collector:
    enabled: true
    model: "gpt-3.5-turbo"
"""
        
        config_file = self.project_path / ".mare" / "config.yaml"
        config_file.write_text(config_content)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_executor_initialization(self):
        """Test executor initialization."""
        with patch('mare.pipeline.executor.MAREPipeline') as mock_pipeline:
            executor = PipelineExecutor(self.project_path)
            
            self.assertEqual(executor.project_path, self.project_path)
            self.assertIsNotNone(executor.project_config)
            self.assertEqual(executor.project_config["project"]["name"], "Test Project")
    
    def test_load_project_config(self):
        """Test loading project configuration."""
        with patch('mare.pipeline.executor.MAREPipeline') as mock_pipeline:
            executor = PipelineExecutor(self.project_path)
            config = executor._load_project_config()
            
            self.assertEqual(config["project"]["name"], "Test Project")
            self.assertEqual(config["llm"]["provider"], "openai")
    
    def test_infer_domain(self):
        """Test domain inference."""
        with patch('mare.pipeline.executor.MAREPipeline') as mock_pipeline:
            executor = PipelineExecutor(self.project_path)
            domain = executor._infer_domain()
            
            self.assertEqual(domain, "test")  # From config
    
    def test_get_system_idea_from_config(self):
        """Test getting system idea from project config."""
        with patch('mare.pipeline.executor.MAREPipeline') as mock_pipeline:
            executor = PipelineExecutor(self.project_path)
            system_idea = executor._get_system_idea()
            
            self.assertIn("Test Project", system_idea)
    
    def test_get_project_status(self):
        """Test getting project status."""
        with patch('mare.pipeline.executor.MAREPipeline') as mock_pipeline:
            executor = PipelineExecutor(self.project_path)
            status = executor.get_project_status()
            
            self.assertEqual(status["project_name"], "Test Project")
            self.assertIn("configuration", status)
            self.assertIn("execution_status", status)
            self.assertIn("artifacts", status)


class TestPipelineIntegration(unittest.TestCase):
    """Integration tests for pipeline components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.workspace_path = self.temp_dir / "workspace"
        self.workspace_path.mkdir(parents=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('mare.agents.factory.AgentFactory.create_all_agents')
    def test_pipeline_execution_flow(self, mock_create_agents):
        """Test complete pipeline execution flow."""
        # Mock agents
        mock_stakeholder = Mock()
        mock_collector = Mock()
        mock_modeler = Mock()
        mock_checker = Mock()
        mock_documenter = Mock()
        
        # Configure mock responses
        mock_stakeholder.express_initial_requirements.return_value = {
            "user_stories": "User wants to buy products online"
        }
        mock_stakeholder.respond_to_question.return_value = {
            "answer": "Yes, credit card payments are required"
        }
        
        mock_collector.analyze_and_question.return_value = {
            "questions": "Question 1: What payment methods?"
        }
        mock_collector.draft_requirements.return_value = {
            "requirements_draft": "REQ-001: Support credit card payments"
        }
        
        mock_modeler.extract_system_entities.return_value = {
            "entities": "User, Product, Payment"
        }
        mock_modeler.extract_entity_relationships.return_value = {
            "relationships": "User purchases Product using Payment"
        }
        
        mock_checker.perform_quality_check.return_value = {
            "check_results": "Overall Quality Score: 8.5/10"
        }
        
        mock_documenter.generate_srs_document.return_value = {
            "srs_document": "# Software Requirements Specification"
        }
        
        mock_agents = {
            AgentRole.STAKEHOLDER: mock_stakeholder,
            AgentRole.COLLECTOR: mock_collector,
            AgentRole.MODELER: mock_modeler,
            AgentRole.CHECKER: mock_checker,
            AgentRole.DOCUMENTER: mock_documenter
        }
        mock_create_agents.return_value = mock_agents
        
        # Create and execute pipeline
        config = PipelineConfig(max_iterations=1, quality_threshold=0.7)
        pipeline = MAREPipeline(config)
        
        result = pipeline.execute(
            system_idea="Build an e-commerce system",
            domain="e-commerce",
            project_name="Test E-commerce",
            workspace_path=self.workspace_path
        )
        
        # Verify execution
        self.assertEqual(result["status"], PipelineStatus.COMPLETED)
        self.assertEqual(result["project_name"], "Test E-commerce")
        self.assertIn("user_stories", result)
        self.assertIn("final_srs", result)
        
        # Verify agent calls
        mock_stakeholder.express_initial_requirements.assert_called()
        mock_collector.analyze_and_question.assert_called()
        mock_modeler.extract_system_entities.assert_called()
        mock_checker.perform_quality_check.assert_called()
        mock_documenter.generate_srs_document.assert_called()


if __name__ == '__main__':
    unittest.main()

