"""
MARE CLI - Shared Workspace Implementation
Collaborative workspace for MARE agents
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime
import threading
from contextlib import contextmanager

from mare.workspace.storage import (
    WorkspaceStorage, WorkspaceArtifact, ArtifactType, 
    ArtifactStatus, ArtifactMetadata
)
from mare.utils.logging import MARELoggerMixin
from mare.utils.exceptions import WorkspaceError


class SharedWorkspace(MARELoggerMixin):
    """
    Shared workspace for MARE agent collaboration.
    
    Provides a high-level interface for agents to:
    - Store and retrieve artifacts
    - Share information between phases
    - Track execution progress
    - Maintain version history
    - Coordinate collaborative work
    """
    
    def __init__(self, workspace_path: Path, execution_id: Optional[str] = None):
        """
        Initialize the shared workspace.
        
        Args:
            workspace_path: Path to the workspace directory
            execution_id: Current execution ID for artifact tracking
        """
        self.workspace_path = workspace_path
        self.execution_id = execution_id
        self.storage = WorkspaceStorage(workspace_path)
        self._lock = threading.RLock()
        
        # Cache for frequently accessed artifacts
        self._artifact_cache: Dict[str, WorkspaceArtifact] = {}
        self._cache_max_size = 50
        
        self.log_info(f"Shared workspace initialized for execution {execution_id}")
    
    @contextmanager
    def transaction(self):
        """Context manager for workspace transactions."""
        with self._lock:
            try:
                yield self
            except Exception as e:
                self.log_error(f"Workspace transaction failed: {e}")
                raise
    
    def store_user_stories(
        self,
        user_stories: str,
        created_by: str,
        status: ArtifactStatus = ArtifactStatus.DRAFT
    ) -> str:
        """
        Store user stories in the workspace.
        
        Args:
            user_stories: User stories content
            created_by: Agent role that created the stories
            status: Artifact status
            
        Returns:
            Artifact ID
        """
        return self.storage.store_artifact(
            artifact_type=ArtifactType.USER_STORIES,
            content=user_stories,
            created_by=created_by,
            execution_id=self.execution_id,
            status=status,
            tags=["requirements", "user_stories"]
        )
    
    def get_user_stories(self, execution_id: Optional[str] = None) -> Optional[str]:
        """
        Get the latest user stories.
        
        Args:
            execution_id: Optional execution ID filter
            
        Returns:
            User stories content if found
        """
        artifact = self.storage.get_latest_artifact(
            ArtifactType.USER_STORIES,
            execution_id or self.execution_id
        )
        return artifact.content if artifact else None
    
    def store_questions(
        self,
        questions: List[str],
        created_by: str,
        context: Optional[str] = None,
        status: ArtifactStatus = ArtifactStatus.DRAFT
    ) -> str:
        """
        Store questions in the workspace.
        
        Args:
            questions: List of questions
            created_by: Agent role that created the questions
            context: Optional context for the questions
            status: Artifact status
            
        Returns:
            Artifact ID
        """
        content = {
            "questions": questions,
            "context": context,
            "count": len(questions)
        }
        
        return self.storage.store_artifact(
            artifact_type=ArtifactType.QUESTIONS,
            content=content,
            created_by=created_by,
            execution_id=self.execution_id,
            status=status,
            tags=["elicitation", "questions"]
        )
    
    def get_questions(self, execution_id: Optional[str] = None) -> List[str]:
        """
        Get the latest questions.
        
        Args:
            execution_id: Optional execution ID filter
            
        Returns:
            List of questions
        """
        artifact = self.storage.get_latest_artifact(
            ArtifactType.QUESTIONS,
            execution_id or self.execution_id
        )
        
        if artifact and isinstance(artifact.content, dict):
            return artifact.content.get("questions", [])
        
        return []
    
    def store_qa_pairs(
        self,
        qa_pairs: List[Dict[str, str]],
        created_by: str,
        status: ArtifactStatus = ArtifactStatus.COMPLETED
    ) -> str:
        """
        Store question-answer pairs in the workspace.
        
        Args:
            qa_pairs: List of Q&A pairs
            created_by: Agent role that created the pairs
            status: Artifact status
            
        Returns:
            Artifact ID
        """
        content = {
            "qa_pairs": qa_pairs,
            "count": len(qa_pairs)
        }
        
        return self.storage.store_artifact(
            artifact_type=ArtifactType.QA_PAIRS,
            content=content,
            created_by=created_by,
            execution_id=self.execution_id,
            status=status,
            tags=["elicitation", "qa_pairs"]
        )
    
    def get_qa_pairs(self, execution_id: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get the latest Q&A pairs.
        
        Args:
            execution_id: Optional execution ID filter
            
        Returns:
            List of Q&A pairs
        """
        artifact = self.storage.get_latest_artifact(
            ArtifactType.QA_PAIRS,
            execution_id or self.execution_id
        )
        
        if artifact and isinstance(artifact.content, dict):
            return artifact.content.get("qa_pairs", [])
        
        return []
    
    def store_requirements_draft(
        self,
        requirements: str,
        created_by: str,
        version_notes: Optional[str] = None,
        status: ArtifactStatus = ArtifactStatus.DRAFT
    ) -> str:
        """
        Store requirements draft in the workspace.
        
        Args:
            requirements: Requirements content
            created_by: Agent role that created the requirements
            version_notes: Optional notes about this version
            status: Artifact status
            
        Returns:
            Artifact ID
        """
        # Get previous version for versioning
        previous_artifact = self.storage.get_latest_artifact(
            ArtifactType.REQUIREMENTS_DRAFT,
            self.execution_id
        )
        
        parent_id = previous_artifact.metadata.artifact_id if previous_artifact else None
        
        content = {
            "requirements": requirements,
            "version_notes": version_notes,
            "word_count": len(requirements.split())
        }
        
        return self.storage.store_artifact(
            artifact_type=ArtifactType.REQUIREMENTS_DRAFT,
            content=content,
            created_by=created_by,
            execution_id=self.execution_id,
            parent_id=parent_id,
            status=status,
            tags=["requirements", "draft"]
        )
    
    def get_requirements_draft(self, execution_id: Optional[str] = None) -> Optional[str]:
        """
        Get the latest requirements draft.
        
        Args:
            execution_id: Optional execution ID filter
            
        Returns:
            Requirements content if found
        """
        artifact = self.storage.get_latest_artifact(
            ArtifactType.REQUIREMENTS_DRAFT,
            execution_id or self.execution_id
        )
        
        if artifact:
            if isinstance(artifact.content, dict):
                return artifact.content.get("requirements")
            return artifact.content
        
        return None
    
    def store_entities(
        self,
        entities: str,
        created_by: str,
        extraction_method: Optional[str] = None,
        status: ArtifactStatus = ArtifactStatus.COMPLETED
    ) -> str:
        """
        Store extracted entities in the workspace.
        
        Args:
            entities: Entities content
            created_by: Agent role that extracted the entities
            extraction_method: Method used for extraction
            status: Artifact status
            
        Returns:
            Artifact ID
        """
        content = {
            "entities": entities,
            "extraction_method": extraction_method,
            "extracted_at": datetime.now().isoformat()
        }
        
        return self.storage.store_artifact(
            artifact_type=ArtifactType.ENTITIES,
            content=content,
            created_by=created_by,
            execution_id=self.execution_id,
            status=status,
            tags=["modeling", "entities"]
        )
    
    def get_entities(self, execution_id: Optional[str] = None) -> Optional[str]:
        """
        Get the latest extracted entities.
        
        Args:
            execution_id: Optional execution ID filter
            
        Returns:
            Entities content if found
        """
        artifact = self.storage.get_latest_artifact(
            ArtifactType.ENTITIES,
            execution_id or self.execution_id
        )
        
        if artifact:
            if isinstance(artifact.content, dict):
                return artifact.content.get("entities")
            return artifact.content
        
        return None
    
    def store_relationships(
        self,
        relationships: str,
        created_by: str,
        extraction_method: Optional[str] = None,
        status: ArtifactStatus = ArtifactStatus.COMPLETED
    ) -> str:
        """
        Store extracted relationships in the workspace.
        
        Args:
            relationships: Relationships content
            created_by: Agent role that extracted the relationships
            extraction_method: Method used for extraction
            status: Artifact status
            
        Returns:
            Artifact ID
        """
        content = {
            "relationships": relationships,
            "extraction_method": extraction_method,
            "extracted_at": datetime.now().isoformat()
        }
        
        return self.storage.store_artifact(
            artifact_type=ArtifactType.RELATIONSHIPS,
            content=content,
            created_by=created_by,
            execution_id=self.execution_id,
            status=status,
            tags=["modeling", "relationships"]
        )
    
    def get_relationships(self, execution_id: Optional[str] = None) -> Optional[str]:
        """
        Get the latest extracted relationships.
        
        Args:
            execution_id: Optional execution ID filter
            
        Returns:
            Relationships content if found
        """
        artifact = self.storage.get_latest_artifact(
            ArtifactType.RELATIONSHIPS,
            execution_id or self.execution_id
        )
        
        if artifact:
            if isinstance(artifact.content, dict):
                return artifact.content.get("relationships")
            return artifact.content
        
        return None
    
    def store_check_results(
        self,
        check_results: str,
        created_by: str,
        quality_score: Optional[float] = None,
        issues_count: Optional[int] = None,
        status: ArtifactStatus = ArtifactStatus.COMPLETED
    ) -> str:
        """
        Store quality check results in the workspace.
        
        Args:
            check_results: Check results content
            created_by: Agent role that performed the check
            quality_score: Overall quality score
            issues_count: Number of issues found
            status: Artifact status
            
        Returns:
            Artifact ID
        """
        content = {
            "check_results": check_results,
            "quality_score": quality_score,
            "issues_count": issues_count,
            "checked_at": datetime.now().isoformat()
        }
        
        return self.storage.store_artifact(
            artifact_type=ArtifactType.CHECK_RESULTS,
            content=content,
            created_by=created_by,
            execution_id=self.execution_id,
            status=status,
            tags=["verification", "quality"]
        )
    
    def get_check_results(self, execution_id: Optional[str] = None) -> Optional[str]:
        """
        Get the latest check results.
        
        Args:
            execution_id: Optional execution ID filter
            
        Returns:
            Check results content if found
        """
        artifact = self.storage.get_latest_artifact(
            ArtifactType.CHECK_RESULTS,
            execution_id or self.execution_id
        )
        
        if artifact:
            if isinstance(artifact.content, dict):
                return artifact.content.get("check_results")
            return artifact.content
        
        return None
    
    def store_final_srs(
        self,
        srs_document: str,
        created_by: str,
        document_type: str = "srs",
        status: ArtifactStatus = ArtifactStatus.COMPLETED
    ) -> str:
        """
        Store final SRS document in the workspace.
        
        Args:
            srs_document: SRS document content
            created_by: Agent role that created the document
            document_type: Type of document (srs, report, etc.)
            status: Artifact status
            
        Returns:
            Artifact ID
        """
        content = {
            "srs_document": srs_document,
            "document_type": document_type,
            "word_count": len(srs_document.split()),
            "generated_at": datetime.now().isoformat()
        }
        
        return self.storage.store_artifact(
            artifact_type=ArtifactType.FINAL_SRS,
            content=content,
            created_by=created_by,
            execution_id=self.execution_id,
            status=status,
            tags=["specification", "final", document_type]
        )
    
    def get_final_srs(self, execution_id: Optional[str] = None) -> Optional[str]:
        """
        Get the final SRS document.
        
        Args:
            execution_id: Optional execution ID filter
            
        Returns:
            SRS document content if found
        """
        artifact = self.storage.get_latest_artifact(
            ArtifactType.FINAL_SRS,
            execution_id or self.execution_id
        )
        
        if artifact:
            if isinstance(artifact.content, dict):
                return artifact.content.get("srs_document")
            return artifact.content
        
        return None
    
    def get_execution_summary(self, execution_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a summary of all artifacts for an execution.
        
        Args:
            execution_id: Optional execution ID filter
            
        Returns:
            Summary of execution artifacts
        """
        exec_id = execution_id or self.execution_id
        
        summary = {
            "execution_id": exec_id,
            "artifacts": {},
            "total_artifacts": 0,
            "phases_completed": []
        }
        
        # Get artifacts for each type
        for artifact_type in ArtifactType:
            artifacts = self.storage.list_artifacts(
                artifact_type=artifact_type,
                execution_id=exec_id
            )
            
            if artifacts:
                latest = artifacts[0]  # Most recent
                summary["artifacts"][artifact_type.value] = {
                    "count": len(artifacts),
                    "latest_id": latest.artifact_id,
                    "status": latest.status.value,
                    "created_by": latest.created_by,
                    "updated_at": latest.updated_at.isoformat()
                }
                summary["total_artifacts"] += len(artifacts)
        
        # Determine completed phases
        if ArtifactType.USER_STORIES.value in summary["artifacts"]:
            summary["phases_completed"].append("elicitation")
        
        if ArtifactType.ENTITIES.value in summary["artifacts"]:
            summary["phases_completed"].append("modeling")
        
        if ArtifactType.CHECK_RESULTS.value in summary["artifacts"]:
            summary["phases_completed"].append("verification")
        
        if ArtifactType.FINAL_SRS.value in summary["artifacts"]:
            summary["phases_completed"].append("specification")
        
        return summary
    
    def cleanup_old_artifacts(self, days_old: int = 30) -> int:
        """
        Clean up old artifacts to save space.
        
        Args:
            days_old: Delete artifacts older than this many days
            
        Returns:
            Number of artifacts deleted
        """
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        deleted_count = 0
        
        # Get all artifacts
        all_artifacts = self.storage.list_artifacts()
        
        for artifact in all_artifacts:
            if artifact.created_at.timestamp() < cutoff_date:
                if artifact.status == ArtifactStatus.ARCHIVED:
                    if self.storage.delete_artifact(artifact.artifact_id):
                        deleted_count += 1
        
        self.log_info(f"Cleaned up {deleted_count} old artifacts")
        return deleted_count
    
    def get_workspace_stats(self) -> Dict[str, Any]:
        """
        Get workspace statistics.
        
        Returns:
            Workspace statistics
        """
        all_artifacts = self.storage.list_artifacts()
        
        stats = {
            "total_artifacts": len(all_artifacts),
            "by_type": {},
            "by_status": {},
            "by_agent": {},
            "storage_size": 0
        }
        
        for artifact in all_artifacts:
            # Count by type
            type_name = artifact.artifact_type.value
            stats["by_type"][type_name] = stats["by_type"].get(type_name, 0) + 1
            
            # Count by status
            status_name = artifact.status.value
            stats["by_status"][status_name] = stats["by_status"].get(status_name, 0) + 1
            
            # Count by agent
            agent_name = artifact.created_by
            stats["by_agent"][agent_name] = stats["by_agent"].get(agent_name, 0) + 1
        
        # Calculate storage size
        if self.workspace_path.exists():
            for file_path in self.workspace_path.rglob("*"):
                if file_path.is_file():
                    stats["storage_size"] += file_path.stat().st_size
        
        return stats

