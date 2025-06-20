"""
MARE CLI - Unit Tests for Workspace
Test suite for validating workspace implementation
"""

import unittest
from unittest.mock import Mock, patch
from pathlib import Path
import tempfile
import shutil
import json
from datetime import datetime

from mare.workspace import (
    SharedWorkspace, WorkspaceStorage, WorkspaceArtifact,
    ArtifactType, ArtifactStatus, ArtifactMetadata
)
from mare.utils.exceptions import WorkspaceError


class TestWorkspaceStorage(unittest.TestCase):
    """Test cases for WorkspaceStorage."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.workspace_path = self.temp_dir / "workspace"
        self.storage = WorkspaceStorage(self.workspace_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_storage_initialization(self):
        """Test storage initialization."""
        self.assertTrue(self.workspace_path.exists())
        self.assertTrue((self.workspace_path / "artifacts").exists())
        self.assertTrue((self.workspace_path / "workspace.db").exists())
    
    def test_store_artifact(self):
        """Test storing an artifact."""
        artifact_id = self.storage.store_artifact(
            artifact_type=ArtifactType.USER_STORIES,
            content="User wants to buy products",
            created_by="stakeholder",
            execution_id="test-exec-1",
            tags=["requirements", "user_stories"]
        )
        
        self.assertIsNotNone(artifact_id)
        
        # Verify artifact can be retrieved
        artifact = self.storage.get_artifact(artifact_id)
        self.assertIsNotNone(artifact)
        self.assertEqual(artifact.content, "User wants to buy products")
        self.assertEqual(artifact.metadata.created_by, "stakeholder")
    
    def test_store_and_retrieve_dict_content(self):
        """Test storing and retrieving dictionary content."""
        content = {
            "questions": ["What payment methods?", "How many users?"],
            "context": "e-commerce system"
        }
        
        artifact_id = self.storage.store_artifact(
            artifact_type=ArtifactType.QUESTIONS,
            content=content,
            created_by="collector"
        )
        
        artifact = self.storage.get_artifact(artifact_id)
        self.assertEqual(artifact.content, content)
    
    def test_update_artifact(self):
        """Test updating an artifact."""
        # Store initial artifact
        artifact_id = self.storage.store_artifact(
            artifact_type=ArtifactType.REQUIREMENTS_DRAFT,
            content="Initial requirements",
            created_by="collector"
        )
        
        # Update artifact
        success = self.storage.update_artifact(
            artifact_id=artifact_id,
            content="Updated requirements",
            updated_by="collector",
            status=ArtifactStatus.REVIEWED
        )
        
        self.assertTrue(success)
        
        # Verify update
        artifact = self.storage.get_artifact(artifact_id)
        self.assertEqual(artifact.content, "Updated requirements")
        self.assertEqual(artifact.metadata.status, ArtifactStatus.REVIEWED)
    
    def test_list_artifacts_with_filters(self):
        """Test listing artifacts with filters."""
        # Store multiple artifacts
        self.storage.store_artifact(
            ArtifactType.USER_STORIES, "Story 1", "stakeholder", "exec-1"
        )
        self.storage.store_artifact(
            ArtifactType.QUESTIONS, "Question 1", "collector", "exec-1"
        )
        self.storage.store_artifact(
            ArtifactType.USER_STORIES, "Story 2", "stakeholder", "exec-2"
        )
        
        # Test filtering by type
        user_stories = self.storage.list_artifacts(
            artifact_type=ArtifactType.USER_STORIES
        )
        self.assertEqual(len(user_stories), 2)
        
        # Test filtering by execution
        exec1_artifacts = self.storage.list_artifacts(execution_id="exec-1")
        self.assertEqual(len(exec1_artifacts), 2)
        
        # Test filtering by creator
        stakeholder_artifacts = self.storage.list_artifacts(created_by="stakeholder")
        self.assertEqual(len(stakeholder_artifacts), 2)
    
    def test_get_latest_artifact(self):
        """Test getting latest artifact of a type."""
        # Store multiple artifacts of same type
        id1 = self.storage.store_artifact(
            ArtifactType.REQUIREMENTS_DRAFT, "Draft 1", "collector"
        )
        id2 = self.storage.store_artifact(
            ArtifactType.REQUIREMENTS_DRAFT, "Draft 2", "collector"
        )
        
        latest = self.storage.get_latest_artifact(ArtifactType.REQUIREMENTS_DRAFT)
        self.assertIsNotNone(latest)
        self.assertEqual(latest.metadata.artifact_id, id2)  # Most recent
    
    def test_delete_artifact(self):
        """Test deleting an artifact."""
        artifact_id = self.storage.store_artifact(
            ArtifactType.USER_STORIES, "Test story", "stakeholder"
        )
        
        # Verify artifact exists
        artifact = self.storage.get_artifact(artifact_id)
        self.assertIsNotNone(artifact)
        
        # Delete artifact
        success = self.storage.delete_artifact(artifact_id)
        self.assertTrue(success)
        
        # Verify artifact is gone
        artifact = self.storage.get_artifact(artifact_id)
        self.assertIsNone(artifact)


class TestSharedWorkspace(unittest.TestCase):
    """Test cases for SharedWorkspace."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.workspace_path = self.temp_dir / "workspace"
        self.execution_id = "test-execution-123"
        self.workspace = SharedWorkspace(self.workspace_path, self.execution_id)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_workspace_initialization(self):
        """Test workspace initialization."""
        self.assertEqual(self.workspace.execution_id, self.execution_id)
        self.assertIsNotNone(self.workspace.storage)
    
    def test_store_and_get_user_stories(self):
        """Test storing and retrieving user stories."""
        user_stories = "As a user, I want to buy products online"
        
        artifact_id = self.workspace.store_user_stories(
            user_stories=user_stories,
            created_by="stakeholder"
        )
        
        self.assertIsNotNone(artifact_id)
        
        retrieved_stories = self.workspace.get_user_stories()
        self.assertEqual(retrieved_stories, user_stories)
    
    def test_store_and_get_questions(self):
        """Test storing and retrieving questions."""
        questions = [
            "What payment methods should be supported?",
            "How many concurrent users are expected?"
        ]
        
        artifact_id = self.workspace.store_questions(
            questions=questions,
            created_by="collector",
            context="e-commerce requirements"
        )
        
        self.assertIsNotNone(artifact_id)
        
        retrieved_questions = self.workspace.get_questions()
        self.assertEqual(retrieved_questions, questions)
    
    def test_store_and_get_qa_pairs(self):
        """Test storing and retrieving Q&A pairs."""
        qa_pairs = [
            {
                "question": "What payment methods?",
                "answer": "Credit cards and PayPal"
            },
            {
                "question": "How many users?",
                "answer": "Up to 10,000 concurrent users"
            }
        ]
        
        artifact_id = self.workspace.store_qa_pairs(
            qa_pairs=qa_pairs,
            created_by="stakeholder"
        )
        
        self.assertIsNotNone(artifact_id)
        
        retrieved_pairs = self.workspace.get_qa_pairs()
        self.assertEqual(retrieved_pairs, qa_pairs)
    
    def test_store_and_get_requirements_draft(self):
        """Test storing and retrieving requirements draft."""
        requirements = """
        REQ-001: The system shall support credit card payments
        REQ-002: The system shall handle 10,000 concurrent users
        """
        
        artifact_id = self.workspace.store_requirements_draft(
            requirements=requirements,
            created_by="collector",
            version_notes="Initial draft based on Q&A"
        )
        
        self.assertIsNotNone(artifact_id)
        
        retrieved_requirements = self.workspace.get_requirements_draft()
        self.assertEqual(retrieved_requirements.strip(), requirements.strip())
    
    def test_store_and_get_entities(self):
        """Test storing and retrieving entities."""
        entities = """
        Entity: User
        - Attributes: id, name, email, password
        
        Entity: Product
        - Attributes: id, name, price, description
        """
        
        artifact_id = self.workspace.store_entities(
            entities=entities,
            created_by="modeler",
            extraction_method="LLM-based extraction"
        )
        
        self.assertIsNotNone(artifact_id)
        
        retrieved_entities = self.workspace.get_entities()
        self.assertEqual(retrieved_entities.strip(), entities.strip())
    
    def test_store_and_get_relationships(self):
        """Test storing and retrieving relationships."""
        relationships = """
        User --purchases--> Product
        User --has--> ShoppingCart
        ShoppingCart --contains--> Product
        """
        
        artifact_id = self.workspace.store_relationships(
            relationships=relationships,
            created_by="modeler"
        )
        
        self.assertIsNotNone(artifact_id)
        
        retrieved_relationships = self.workspace.get_relationships()
        self.assertEqual(retrieved_relationships.strip(), relationships.strip())
    
    def test_store_and_get_check_results(self):
        """Test storing and retrieving check results."""
        check_results = """
        Overall Quality Score: 8.5/10
        
        Completeness: Good (8/10)
        Consistency: Excellent (9/10)
        Clarity: Good (8/10)
        
        Issues Found:
        - Minor: Missing error handling requirements
        - Minor: Unclear performance metrics
        """
        
        artifact_id = self.workspace.store_check_results(
            check_results=check_results,
            created_by="checker",
            quality_score=8.5,
            issues_count=2
        )
        
        self.assertIsNotNone(artifact_id)
        
        retrieved_results = self.workspace.get_check_results()
        self.assertEqual(retrieved_results.strip(), check_results.strip())
    
    def test_store_and_get_final_srs(self):
        """Test storing and retrieving final SRS."""
        srs_document = """
        # Software Requirements Specification
        
        ## 1. Introduction
        This document specifies the requirements for an e-commerce system.
        
        ## 2. Functional Requirements
        REQ-001: The system shall support credit card payments
        REQ-002: The system shall handle 10,000 concurrent users
        """
        
        artifact_id = self.workspace.store_final_srs(
            srs_document=srs_document,
            created_by="documenter",
            document_type="srs"
        )
        
        self.assertIsNotNone(artifact_id)
        
        retrieved_srs = self.workspace.get_final_srs()
        self.assertEqual(retrieved_srs.strip(), srs_document.strip())
    
    def test_get_execution_summary(self):
        """Test getting execution summary."""
        # Store various artifacts
        self.workspace.store_user_stories("User stories", "stakeholder")
        self.workspace.store_questions(["Question 1"], "collector")
        self.workspace.store_requirements_draft("Requirements", "collector")
        self.workspace.store_entities("Entities", "modeler")
        self.workspace.store_check_results("Check results", "checker")
        self.workspace.store_final_srs("SRS document", "documenter")
        
        summary = self.workspace.get_execution_summary()
        
        self.assertEqual(summary["execution_id"], self.execution_id)
        self.assertEqual(summary["total_artifacts"], 6)
        self.assertEqual(len(summary["phases_completed"]), 4)
        self.assertIn("elicitation", summary["phases_completed"])
        self.assertIn("modeling", summary["phases_completed"])
        self.assertIn("verification", summary["phases_completed"])
        self.assertIn("specification", summary["phases_completed"])
    
    def test_workspace_transaction(self):
        """Test workspace transaction context manager."""
        with self.workspace.transaction():
            artifact_id = self.workspace.store_user_stories(
                "Test stories", "stakeholder"
            )
            self.assertIsNotNone(artifact_id)
        
        # Verify artifact was stored
        stories = self.workspace.get_user_stories()
        self.assertEqual(stories, "Test stories")
    
    def test_get_workspace_stats(self):
        """Test getting workspace statistics."""
        # Store some artifacts
        self.workspace.store_user_stories("Stories", "stakeholder")
        self.workspace.store_questions(["Q1", "Q2"], "collector")
        self.workspace.store_requirements_draft("Requirements", "collector")
        
        stats = self.workspace.get_workspace_stats()
        
        self.assertEqual(stats["total_artifacts"], 3)
        self.assertIn("by_type", stats)
        self.assertIn("by_status", stats)
        self.assertIn("by_agent", stats)
        self.assertIn("storage_size", stats)
        
        # Check type counts
        self.assertEqual(stats["by_type"]["user_stories"], 1)
        self.assertEqual(stats["by_type"]["questions"], 1)
        self.assertEqual(stats["by_type"]["requirements_draft"], 1)


class TestArtifactMetadata(unittest.TestCase):
    """Test cases for ArtifactMetadata."""
    
    def test_metadata_creation(self):
        """Test creating artifact metadata."""
        now = datetime.now()
        metadata = ArtifactMetadata(
            artifact_id="test-123",
            artifact_type=ArtifactType.USER_STORIES,
            status=ArtifactStatus.DRAFT,
            created_by="stakeholder",
            created_at=now,
            updated_at=now,
            version=1,
            execution_id="exec-123",
            tags=["requirements", "user_stories"]
        )
        
        self.assertEqual(metadata.artifact_id, "test-123")
        self.assertEqual(metadata.artifact_type, ArtifactType.USER_STORIES)
        self.assertEqual(metadata.status, ArtifactStatus.DRAFT)
        self.assertEqual(metadata.created_by, "stakeholder")
        self.assertEqual(metadata.version, 1)
        self.assertEqual(len(metadata.tags), 2)
    
    def test_metadata_default_tags(self):
        """Test metadata with default empty tags."""
        now = datetime.now()
        metadata = ArtifactMetadata(
            artifact_id="test-123",
            artifact_type=ArtifactType.USER_STORIES,
            status=ArtifactStatus.DRAFT,
            created_by="stakeholder",
            created_at=now,
            updated_at=now,
            version=1
        )
        
        self.assertEqual(metadata.tags, [])


class TestWorkspaceArtifact(unittest.TestCase):
    """Test cases for WorkspaceArtifact."""
    
    def test_artifact_to_dict(self):
        """Test converting artifact to dictionary."""
        now = datetime.now()
        metadata = ArtifactMetadata(
            artifact_id="test-123",
            artifact_type=ArtifactType.USER_STORIES,
            status=ArtifactStatus.DRAFT,
            created_by="stakeholder",
            created_at=now,
            updated_at=now,
            version=1
        )
        
        artifact = WorkspaceArtifact(
            metadata=metadata,
            content="Test user stories"
        )
        
        artifact_dict = artifact.to_dict()
        
        self.assertIn("metadata", artifact_dict)
        self.assertIn("content", artifact_dict)
        self.assertEqual(artifact_dict["content"], "Test user stories")
    
    def test_artifact_from_dict(self):
        """Test creating artifact from dictionary."""
        now = datetime.now()
        artifact_dict = {
            "metadata": {
                "artifact_id": "test-123",
                "artifact_type": "user_stories",
                "status": "draft",
                "created_by": "stakeholder",
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "version": 1,
                "parent_id": None,
                "execution_id": None,
                "tags": [],
                "checksum": None
            },
            "content": "Test user stories"
        }
        
        artifact = WorkspaceArtifact.from_dict(artifact_dict)
        
        self.assertEqual(artifact.metadata.artifact_id, "test-123")
        self.assertEqual(artifact.metadata.artifact_type, ArtifactType.USER_STORIES)
        self.assertEqual(artifact.content, "Test user stories")


if __name__ == '__main__':
    unittest.main()

