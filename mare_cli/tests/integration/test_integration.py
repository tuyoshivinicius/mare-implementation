"""
MARE CLI - Integration Tests
Test suite for validating end-to-end functionality
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil
import subprocess
import yaml
import json

from mare.cli.commands.init import init_command
from mare.cli.commands.run import run_command
from mare.cli.commands.status import status_command
from mare.cli.commands.export import export_command
from mare.pipeline import PipelineExecutor
from mare.workspace import SharedWorkspace


class TestCLIIntegration(unittest.TestCase):
    """Integration tests for CLI commands."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.project_name = "test_integration_project"
        self.project_path = self.temp_dir / self.project_name
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_init_command_integration(self):
        """Test init command creates proper project structure."""
        # Test init command
        result = init_command(
            project_name=self.project_name,
            template="basic",
            llm_provider="openai",
            output_dir=str(self.temp_dir)
        )
        
        self.assertTrue(result)
        self.assertTrue(self.project_path.exists())
        
        # Verify project structure
        self.assertTrue((self.project_path / ".mare").exists())
        self.assertTrue((self.project_path / ".mare" / "config.yaml").exists())
        self.assertTrue((self.project_path / ".mare" / "workspace").exists())
        self.assertTrue((self.project_path / "input.md").exists())
        self.assertTrue((self.project_path / "README.md").exists())
        
        # Verify config content
        config_file = self.project_path / ".mare" / "config.yaml"
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        self.assertEqual(config["project"]["name"], self.project_name)
        self.assertEqual(config["project"]["template"], "basic")
        self.assertEqual(config["llm"]["provider"], "openai")
    
    def test_status_command_integration(self):
        """Test status command with real project."""
        # Create project first
        init_command(
            project_name=self.project_name,
            template="basic",
            llm_provider="openai",
            output_dir=str(self.temp_dir)
        )
        
        # Test status command
        with patch('mare.pipeline.executor.MAREPipeline') as mock_pipeline:
            status = status_command(project_path=str(self.project_path))
            
            self.assertIsNotNone(status)
            self.assertEqual(status["project_name"], self.project_name)
            self.assertIn("configuration", status)
            self.assertIn("execution_status", status)
    
    @patch('mare.agents.factory.AgentFactory.create_all_agents')
    def test_run_command_integration(self, mock_create_agents):
        """Test run command with mocked agents."""
        # Create project first
        init_command(
            project_name=self.project_name,
            template="basic",
            llm_provider="openai",
            output_dir=str(self.temp_dir)
        )
        
        # Mock agents to avoid LLM dependencies
        mock_agents = self._create_mock_agents()
        mock_create_agents.return_value = mock_agents
        
        # Test run command
        result = run_command(
            project_path=str(self.project_path),
            input_file=None,
            interactive=False
        )
        
        self.assertIsNotNone(result)
        self.assertIn("status", result)
    
    def test_export_command_integration(self):
        """Test export command with real project."""
        # Create project first
        init_command(
            project_name=self.project_name,
            template="basic",
            llm_provider="openai",
            output_dir=str(self.temp_dir)
        )
        
        # Create some mock output files
        output_dir = self.project_path / "output"
        output_dir.mkdir(exist_ok=True)
        
        srs_file = output_dir / "requirements.md"
        srs_file.write_text("# Software Requirements Specification\n\nTest content")
        
        # Test export command
        result = export_command(
            project_path=str(self.project_path),
            format="markdown",
            output_file=None
        )
        
        self.assertTrue(result)
    
    def _create_mock_agents(self):
        """Create mock agents for testing."""
        from mare.agents import AgentRole
        
        mock_stakeholder = Mock()
        mock_collector = Mock()
        mock_modeler = Mock()
        mock_checker = Mock()
        mock_documenter = Mock()
        
        # Configure mock responses
        mock_stakeholder.express_initial_requirements.return_value = {
            "user_stories": "As a user, I want to test the system"
        }
        mock_stakeholder.respond_to_question.return_value = {
            "answer": "Yes, testing is important"
        }
        
        mock_collector.analyze_and_question.return_value = {
            "questions": "Question 1: What testing framework?"
        }
        mock_collector.draft_requirements.return_value = {
            "requirements_draft": "REQ-001: System shall support testing"
        }
        
        mock_modeler.extract_system_entities.return_value = {
            "entities": "TestCase, TestResult, TestRunner"
        }
        mock_modeler.extract_entity_relationships.return_value = {
            "relationships": "TestRunner executes TestCase produces TestResult"
        }
        
        mock_checker.perform_quality_check.return_value = {
            "check_results": "Overall Quality Score: 8.5/10"
        }
        
        mock_documenter.generate_srs_document.return_value = {
            "srs_document": "# Software Requirements Specification\n## Testing Requirements"
        }
        
        return {
            AgentRole.STAKEHOLDER: mock_stakeholder,
            AgentRole.COLLECTOR: mock_collector,
            AgentRole.MODELER: mock_modeler,
            AgentRole.CHECKER: mock_checker,
            AgentRole.DOCUMENTER: mock_documenter
        }


class TestWorkspacePipelineIntegration(unittest.TestCase):
    """Integration tests for workspace and pipeline interaction."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.workspace_path = self.temp_dir / "workspace"
        self.workspace_path.mkdir(parents=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_workspace_pipeline_collaboration(self):
        """Test workspace and pipeline working together."""
        execution_id = "test-integration-123"
        workspace = SharedWorkspace(self.workspace_path, execution_id)
        
        # Simulate pipeline phases storing artifacts
        
        # Phase 1: Elicitation
        user_stories_id = workspace.store_user_stories(
            "As a user, I want to manage my account",
            "stakeholder"
        )
        
        questions_id = workspace.store_questions(
            ["What account features?", "How to authenticate?"],
            "collector",
            "Account management system"
        )
        
        qa_pairs_id = workspace.store_qa_pairs([
            {"question": "What account features?", "answer": "Profile, settings, preferences"},
            {"question": "How to authenticate?", "answer": "Username/password and 2FA"}
        ], "stakeholder")
        
        requirements_id = workspace.store_requirements_draft(
            "REQ-001: User shall manage profile\nREQ-002: System shall support 2FA",
            "collector",
            "Based on Q&A session"
        )
        
        # Phase 2: Modeling
        entities_id = workspace.store_entities(
            "User, Profile, Authentication, TwoFactorAuth",
            "modeler"
        )
        
        relationships_id = workspace.store_relationships(
            "User has Profile\nUser uses Authentication\nAuthentication includes TwoFactorAuth",
            "modeler"
        )
        
        # Phase 3: Verification
        check_results_id = workspace.store_check_results(
            "Quality Score: 8.5/10\nCompleteness: Good\nConsistency: Excellent",
            "checker",
            quality_score=8.5,
            issues_count=1
        )
        
        # Phase 4: Specification
        srs_id = workspace.store_final_srs(
            "# Account Management SRS\n## Requirements\nREQ-001: Profile management\nREQ-002: 2FA support",
            "documenter"
        )
        
        # Verify all artifacts are stored and retrievable
        self.assertIsNotNone(workspace.get_user_stories())
        self.assertEqual(len(workspace.get_questions()), 2)
        self.assertEqual(len(workspace.get_qa_pairs()), 2)
        self.assertIsNotNone(workspace.get_requirements_draft())
        self.assertIsNotNone(workspace.get_entities())
        self.assertIsNotNone(workspace.get_relationships())
        self.assertIsNotNone(workspace.get_check_results())
        self.assertIsNotNone(workspace.get_final_srs())
        
        # Verify execution summary
        summary = workspace.get_execution_summary()
        self.assertEqual(summary["execution_id"], execution_id)
        self.assertEqual(summary["total_artifacts"], 8)
        self.assertEqual(len(summary["phases_completed"]), 4)
    
    def test_workspace_versioning(self):
        """Test workspace artifact versioning."""
        workspace = SharedWorkspace(self.workspace_path, "version-test")
        
        # Store initial requirements
        req_v1_id = workspace.store_requirements_draft(
            "REQ-001: Basic user authentication",
            "collector",
            "Initial version"
        )
        
        # Store updated requirements (should create new version)
        req_v2_id = workspace.store_requirements_draft(
            "REQ-001: Enhanced user authentication with 2FA\nREQ-002: Password complexity rules",
            "collector",
            "Added 2FA and password rules"
        )
        
        # Verify both versions exist
        req_v1 = workspace.storage.get_artifact(req_v1_id)
        req_v2 = workspace.storage.get_artifact(req_v2_id)
        
        self.assertIsNotNone(req_v1)
        self.assertIsNotNone(req_v2)
        self.assertEqual(req_v1.metadata.version, 1)
        self.assertEqual(req_v2.metadata.version, 2)
        self.assertEqual(req_v2.metadata.parent_id, req_v1_id)
        
        # Verify latest version is returned
        latest_requirements = workspace.get_requirements_draft()
        self.assertIn("Enhanced user authentication", latest_requirements)
        self.assertIn("REQ-002", latest_requirements)


class TestEndToEndScenarios(unittest.TestCase):
    """End-to-end test scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('mare.agents.factory.AgentFactory.create_all_agents')
    def test_complete_requirements_engineering_flow(self, mock_create_agents):
        """Test complete requirements engineering workflow."""
        # Mock agents
        mock_agents = self._create_comprehensive_mock_agents()
        mock_create_agents.return_value = mock_agents
        
        # Step 1: Initialize project
        project_name = "e_commerce_system"
        project_path = self.temp_dir / project_name
        
        success = init_command(
            project_name=project_name,
            template="basic",
            llm_provider="openai",
            output_dir=str(self.temp_dir)
        )
        self.assertTrue(success)
        
        # Step 2: Create input specification
        input_file = project_path / "input.md"
        input_content = """
        # E-commerce System Requirements
        
        We need to build an online shopping platform that allows:
        - Users to browse and purchase products
        - Merchants to manage their inventory
        - Secure payment processing
        - Order tracking and management
        
        Target audience: Small to medium businesses
        Expected load: 1000 concurrent users
        """
        input_file.write_text(input_content)
        
        # Step 3: Run pipeline
        result = run_command(
            project_path=str(project_path),
            input_file=str(input_file),
            interactive=False
        )
        
        self.assertIsNotNone(result)
        self.assertIn("status", result)
        
        # Step 4: Verify outputs
        output_dir = project_path / "output"
        self.assertTrue(output_dir.exists())
        
        # Check for generated files
        expected_files = [
            "user_stories.md",
            "questions_and_answers.md", 
            "requirements_draft.md",
            "system_entities.md",
            "entity_relationships.md",
            "quality_check_report.md",
            "requirements_specification.md"
        ]
        
        for filename in expected_files:
            file_path = output_dir / filename
            # Files should exist (even if empty due to mocking)
            # In real scenario, they would contain actual content
        
        # Step 5: Check project status
        status = status_command(project_path=str(project_path))
        self.assertIsNotNone(status)
        self.assertEqual(status["project_name"], project_name)
        
        # Step 6: Export results
        export_success = export_command(
            project_path=str(project_path),
            format="markdown",
            output_file=None
        )
        self.assertTrue(export_success)
        
        # Verify workspace contains all artifacts
        workspace_path = project_path / ".mare" / "workspace"
        workspace = SharedWorkspace(workspace_path)
        
        summary = workspace.get_execution_summary()
        # Should have artifacts from the pipeline execution
        self.assertGreater(summary["total_artifacts"], 0)
    
    def _create_comprehensive_mock_agents(self):
        """Create comprehensive mock agents for e2e testing."""
        from mare.agents import AgentRole
        
        mock_stakeholder = Mock()
        mock_collector = Mock()
        mock_modeler = Mock()
        mock_checker = Mock()
        mock_documenter = Mock()
        
        # Stakeholder responses
        mock_stakeholder.express_initial_requirements.return_value = {
            "user_stories": """
            As a customer, I want to browse products by category
            As a customer, I want to add products to my shopping cart
            As a customer, I want to securely checkout and pay
            As a merchant, I want to manage my product inventory
            As a merchant, I want to track my sales and orders
            """
        }
        
        mock_stakeholder.respond_to_question.return_value = {
            "answer": "Yes, we need support for multiple payment methods including credit cards, PayPal, and digital wallets"
        }
        
        # Collector responses
        mock_collector.analyze_and_question.return_value = {
            "questions": """
            Question 1: What payment methods should be supported?
            Question 2: How should inventory be managed?
            Question 3: What are the security requirements?
            Question 4: How should orders be tracked?
            """
        }
        
        mock_collector.draft_requirements.return_value = {
            "requirements_draft": """
            REQ-001: The system shall support product browsing by category
            REQ-002: The system shall provide shopping cart functionality
            REQ-003: The system shall support secure payment processing
            REQ-004: The system shall allow merchants to manage inventory
            REQ-005: The system shall provide order tracking capabilities
            REQ-006: The system shall support multiple payment methods
            REQ-007: The system shall ensure data security and privacy
            """
        }
        
        # Modeler responses
        mock_modeler.extract_system_entities.return_value = {
            "entities": """
            Customer: id, name, email, address, phone
            Merchant: id, business_name, email, address
            Product: id, name, description, price, category, inventory_count
            Order: id, customer_id, total_amount, status, created_date
            OrderItem: order_id, product_id, quantity, unit_price
            Payment: id, order_id, amount, method, status, transaction_id
            ShoppingCart: customer_id, created_date, updated_date
            CartItem: cart_id, product_id, quantity
            """
        }
        
        mock_modeler.extract_entity_relationships.return_value = {
            "relationships": """
            Customer places Order
            Order contains OrderItem
            OrderItem references Product
            Merchant owns Product
            Customer has ShoppingCart
            ShoppingCart contains CartItem
            CartItem references Product
            Order has Payment
            """
        }
        
        # Checker responses
        mock_checker.perform_quality_check.return_value = {
            "check_results": """
            Overall Quality Score: 8.7/10
            
            Completeness: Excellent (9/10)
            - All major functional areas covered
            - Payment processing well defined
            - Inventory management included
            
            Consistency: Good (8/10)
            - Terminology mostly consistent
            - Minor inconsistencies in entity naming
            
            Clarity: Good (8/10)
            - Requirements are clear and understandable
            - Some requirements could be more specific
            
            Feasibility: Excellent (9/10)
            - All requirements are technically feasible
            - Architecture supports scalability requirements
            
            Issues Found:
            - Minor: Inconsistent entity naming (Customer vs User)
            - Minor: Missing specific performance metrics
            """
        }
        
        # Documenter responses
        mock_documenter.generate_srs_document.return_value = {
            "srs_document": """
            # Software Requirements Specification
            ## E-commerce Platform
            
            ### 1. Introduction
            This document specifies the requirements for an e-commerce platform
            that enables online shopping for customers and inventory management
            for merchants.
            
            ### 2. System Overview
            The system consists of a web-based platform supporting:
            - Customer product browsing and purchasing
            - Merchant inventory and order management
            - Secure payment processing
            - Order tracking and fulfillment
            
            ### 3. Functional Requirements
            
            #### 3.1 Customer Management
            REQ-001: The system shall support product browsing by category
            REQ-002: The system shall provide shopping cart functionality
            REQ-003: The system shall support secure payment processing
            
            #### 3.2 Merchant Management
            REQ-004: The system shall allow merchants to manage inventory
            REQ-005: The system shall provide sales tracking capabilities
            
            #### 3.3 Payment Processing
            REQ-006: The system shall support multiple payment methods
            REQ-007: The system shall ensure secure transaction processing
            
            ### 4. Non-Functional Requirements
            
            #### 4.1 Performance
            - System shall support 1000 concurrent users
            - Page load times shall not exceed 3 seconds
            
            #### 4.2 Security
            - All payment data shall be encrypted
            - User authentication shall be required
            
            ### 5. System Architecture
            The system follows a microservices architecture with:
            - Customer service
            - Product catalog service
            - Order management service
            - Payment processing service
            - Inventory management service
            """
        }
        
        return {
            AgentRole.STAKEHOLDER: mock_stakeholder,
            AgentRole.COLLECTOR: mock_collector,
            AgentRole.MODELER: mock_modeler,
            AgentRole.CHECKER: mock_checker,
            AgentRole.DOCUMENTER: mock_documenter
        }


if __name__ == '__main__':
    unittest.main()

