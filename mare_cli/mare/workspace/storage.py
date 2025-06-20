"""
MARE CLI - Workspace Implementation
Shared workspace for agent collaboration and artifact management
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import sqlite3
import uuid
import hashlib
from enum import Enum

from mare.utils.logging import MARELoggerMixin
from mare.utils.exceptions import WorkspaceError
from mare.utils.helpers import write_json_file, read_json_file


class ArtifactType(Enum):
    """Types of artifacts stored in the workspace."""
    USER_STORIES = "user_stories"
    QUESTIONS = "questions"
    QA_PAIRS = "qa_pairs"
    REQUIREMENTS_DRAFT = "requirements_draft"
    ENTITIES = "entities"
    RELATIONSHIPS = "relationships"
    CHECK_RESULTS = "check_results"
    FINAL_SRS = "final_srs"
    EXECUTION_LOG = "execution_log"


class ArtifactStatus(Enum):
    """Status of artifacts in the workspace."""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    ARCHIVED = "archived"


@dataclass
class ArtifactMetadata:
    """Metadata for workspace artifacts."""
    artifact_id: str
    artifact_type: ArtifactType
    status: ArtifactStatus
    created_by: str  # Agent role
    created_at: datetime
    updated_at: datetime
    version: int
    parent_id: Optional[str] = None
    execution_id: Optional[str] = None
    tags: List[str] = None
    checksum: Optional[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class WorkspaceArtifact:
    """Complete artifact with metadata and content."""
    metadata: ArtifactMetadata
    content: Union[str, Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert artifact to dictionary."""
        metadata_dict = asdict(self.metadata)
        # Convert enums to strings for JSON serialization
        metadata_dict["artifact_type"] = self.metadata.artifact_type.value
        metadata_dict["status"] = self.metadata.status.value
        # Convert datetime to ISO format
        metadata_dict["created_at"] = self.metadata.created_at.isoformat()
        metadata_dict["updated_at"] = self.metadata.updated_at.isoformat()
        
        return {
            "metadata": metadata_dict,
            "content": self.content
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkspaceArtifact":
        """Create artifact from dictionary."""
        metadata_dict = data["metadata"]
        metadata_dict["artifact_type"] = ArtifactType(metadata_dict["artifact_type"])
        metadata_dict["status"] = ArtifactStatus(metadata_dict["status"])
        metadata_dict["created_at"] = datetime.fromisoformat(metadata_dict["created_at"])
        metadata_dict["updated_at"] = datetime.fromisoformat(metadata_dict["updated_at"])
        
        metadata = ArtifactMetadata(**metadata_dict)
        return cls(metadata=metadata, content=data["content"])


class WorkspaceStorage(MARELoggerMixin):
    """
    Storage backend for the MARE workspace.
    
    Provides persistent storage for artifacts with versioning,
    metadata management, and efficient querying.
    """
    
    def __init__(self, workspace_path: Path):
        """
        Initialize workspace storage.
        
        Args:
            workspace_path: Path to the workspace directory
        """
        self.workspace_path = workspace_path
        self.db_path = workspace_path / "workspace.db"
        self.artifacts_path = workspace_path / "artifacts"
        
        # Ensure directories exist
        self.workspace_path.mkdir(parents=True, exist_ok=True)
        self.artifacts_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        self.log_info(f"Workspace storage initialized at {workspace_path}")
    
    def _init_database(self) -> None:
        """Initialize SQLite database for metadata storage."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS artifacts (
                        artifact_id TEXT PRIMARY KEY,
                        artifact_type TEXT NOT NULL,
                        status TEXT NOT NULL,
                        created_by TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        version INTEGER NOT NULL,
                        parent_id TEXT,
                        execution_id TEXT,
                        tags TEXT,
                        checksum TEXT,
                        content_path TEXT NOT NULL
                    )
                """)
                
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS executions (
                        execution_id TEXT PRIMARY KEY,
                        project_name TEXT NOT NULL,
                        domain TEXT NOT NULL,
                        status TEXT NOT NULL,
                        quality_score REAL,
                        iterations INTEGER,
                        started_at TEXT NOT NULL,
                        completed_at TEXT,
                        error_message TEXT
                    )
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_artifact_type 
                    ON artifacts(artifact_type)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_execution_id 
                    ON artifacts(execution_id)
                """)
                
                conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_created_at 
                    ON artifacts(created_at)
                """)
                
                conn.commit()
                
            self.log_info("Database initialized successfully")
            
        except Exception as e:
            self.log_error(f"Failed to initialize database: {e}")
            raise WorkspaceError(f"Database initialization failed: {e}")
    
    def store_artifact(
        self,
        artifact_type: ArtifactType,
        content: Union[str, Dict[str, Any]],
        created_by: str,
        execution_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
        status: ArtifactStatus = ArtifactStatus.DRAFT
    ) -> str:
        """
        Store an artifact in the workspace.
        
        Args:
            artifact_type: Type of the artifact
            content: Artifact content
            created_by: Agent role that created the artifact
            execution_id: Associated execution ID
            parent_id: Parent artifact ID for versioning
            tags: Optional tags for categorization
            status: Artifact status
            
        Returns:
            Artifact ID
        """
        try:
            # Generate artifact ID
            artifact_id = str(uuid.uuid4())
            
            # Calculate checksum
            content_str = json.dumps(content, sort_keys=True) if isinstance(content, dict) else content
            checksum = hashlib.sha256(content_str.encode()).hexdigest()
            
            # Determine version
            version = 1
            if parent_id:
                parent_version = self._get_artifact_version(parent_id)
                version = parent_version + 1 if parent_version else 1
            
            # Create metadata
            now = datetime.now()
            metadata = ArtifactMetadata(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                status=status,
                created_by=created_by,
                created_at=now,
                updated_at=now,
                version=version,
                parent_id=parent_id,
                execution_id=execution_id,
                tags=tags or [],
                checksum=checksum
            )
            
            # Create artifact
            artifact = WorkspaceArtifact(metadata=metadata, content=content)
            
            # Store content to file
            content_path = self._store_artifact_content(artifact_id, artifact)
            
            # Store metadata to database
            self._store_artifact_metadata(metadata, content_path)
            
            self.log_info(f"Stored artifact {artifact_id} of type {artifact_type.value}")
            return artifact_id
            
        except Exception as e:
            self.log_error(f"Failed to store artifact: {e}")
            raise WorkspaceError(f"Failed to store artifact: {e}")
    
    def get_artifact(self, artifact_id: str) -> Optional[WorkspaceArtifact]:
        """
        Retrieve an artifact by ID.
        
        Args:
            artifact_id: Artifact ID
            
        Returns:
            Artifact if found, None otherwise
        """
        try:
            # Get metadata from database
            metadata = self._get_artifact_metadata(artifact_id)
            if not metadata:
                return None
            
            # Load content from file
            content = self._load_artifact_content(artifact_id)
            if content is None:
                return None
            
            return WorkspaceArtifact(metadata=metadata, content=content)
            
        except Exception as e:
            self.log_error(f"Failed to get artifact {artifact_id}: {e}")
            return None
    
    def update_artifact(
        self,
        artifact_id: str,
        content: Union[str, Dict[str, Any]],
        updated_by: str,
        status: Optional[ArtifactStatus] = None
    ) -> bool:
        """
        Update an existing artifact.
        
        Args:
            artifact_id: Artifact ID
            content: New content
            updated_by: Agent role updating the artifact
            status: New status (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get existing artifact
            artifact = self.get_artifact(artifact_id)
            if not artifact:
                return False
            
            # Calculate new checksum
            content_str = json.dumps(content, sort_keys=True) if isinstance(content, dict) else content
            checksum = hashlib.sha256(content_str.encode()).hexdigest()
            
            # Update metadata
            artifact.metadata.updated_at = datetime.now()
            artifact.metadata.checksum = checksum
            if status:
                artifact.metadata.status = status
            
            # Update content
            artifact.content = content
            
            # Store updated content
            content_path = self._store_artifact_content(artifact_id, artifact)
            
            # Update database
            self._update_artifact_metadata(artifact.metadata, content_path)
            
            self.log_info(f"Updated artifact {artifact_id}")
            return True
            
        except Exception as e:
            self.log_error(f"Failed to update artifact {artifact_id}: {e}")
            return False
    
    def list_artifacts(
        self,
        artifact_type: Optional[ArtifactType] = None,
        execution_id: Optional[str] = None,
        created_by: Optional[str] = None,
        status: Optional[ArtifactStatus] = None,
        limit: Optional[int] = None
    ) -> List[ArtifactMetadata]:
        """
        List artifacts with optional filtering.
        
        Args:
            artifact_type: Filter by artifact type
            execution_id: Filter by execution ID
            created_by: Filter by creator
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of artifact metadata
        """
        try:
            query = "SELECT * FROM artifacts WHERE 1=1"
            params = []
            
            if artifact_type:
                query += " AND artifact_type = ?"
                params.append(artifact_type.value)
            
            if execution_id:
                query += " AND execution_id = ?"
                params.append(execution_id)
            
            if created_by:
                query += " AND created_by = ?"
                params.append(created_by)
            
            if status:
                query += " AND status = ?"
                params.append(status.value)
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
            
            artifacts = []
            for row in rows:
                metadata = self._row_to_metadata(row)
                artifacts.append(metadata)
            
            return artifacts
            
        except Exception as e:
            self.log_error(f"Failed to list artifacts: {e}")
            return []
    
    def get_latest_artifact(
        self,
        artifact_type: ArtifactType,
        execution_id: Optional[str] = None
    ) -> Optional[WorkspaceArtifact]:
        """
        Get the latest artifact of a specific type.
        
        Args:
            artifact_type: Type of artifact
            execution_id: Optional execution ID filter
            
        Returns:
            Latest artifact if found, None otherwise
        """
        artifacts = self.list_artifacts(
            artifact_type=artifact_type,
            execution_id=execution_id,
            limit=1
        )
        
        if artifacts:
            return self.get_artifact(artifacts[0].artifact_id)
        
        return None
    
    def delete_artifact(self, artifact_id: str) -> bool:
        """
        Delete an artifact.
        
        Args:
            artifact_id: Artifact ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete content file
            content_file = self.artifacts_path / f"{artifact_id}.json"
            if content_file.exists():
                content_file.unlink()
            
            # Delete from database
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM artifacts WHERE artifact_id = ?",
                    (artifact_id,)
                )
                deleted = cursor.rowcount > 0
                conn.commit()
            
            if deleted:
                self.log_info(f"Deleted artifact {artifact_id}")
            
            return deleted
            
        except Exception as e:
            self.log_error(f"Failed to delete artifact {artifact_id}: {e}")
            return False
    
    def _store_artifact_content(self, artifact_id: str, artifact: WorkspaceArtifact) -> str:
        """Store artifact content to file."""
        content_file = self.artifacts_path / f"{artifact_id}.json"
        write_json_file(content_file, artifact.to_dict())
        return str(content_file)
    
    def _load_artifact_content(self, artifact_id: str) -> Optional[Union[str, Dict[str, Any]]]:
        """Load artifact content from file."""
        content_file = self.artifacts_path / f"{artifact_id}.json"
        if not content_file.exists():
            return None
        
        try:
            data = read_json_file(content_file)
            return data.get("content")
        except Exception as e:
            self.log_error(f"Failed to load content for artifact {artifact_id}: {e}")
            return None
    
    def _store_artifact_metadata(self, metadata: ArtifactMetadata, content_path: str) -> None:
        """Store artifact metadata to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO artifacts (
                    artifact_id, artifact_type, status, created_by,
                    created_at, updated_at, version, parent_id,
                    execution_id, tags, checksum, content_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata.artifact_id,
                metadata.artifact_type.value,
                metadata.status.value,
                metadata.created_by,
                metadata.created_at.isoformat(),
                metadata.updated_at.isoformat(),
                metadata.version,
                metadata.parent_id,
                metadata.execution_id,
                json.dumps(metadata.tags),
                metadata.checksum,
                content_path
            ))
            conn.commit()
    
    def _update_artifact_metadata(self, metadata: ArtifactMetadata, content_path: str) -> None:
        """Update artifact metadata in database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE artifacts SET
                    status = ?, updated_at = ?, checksum = ?, content_path = ?
                WHERE artifact_id = ?
            """, (
                metadata.status.value,
                metadata.updated_at.isoformat(),
                metadata.checksum,
                content_path,
                metadata.artifact_id
            ))
            conn.commit()
    
    def _get_artifact_metadata(self, artifact_id: str) -> Optional[ArtifactMetadata]:
        """Get artifact metadata from database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM artifacts WHERE artifact_id = ?",
                (artifact_id,)
            )
            row = cursor.fetchone()
        
        if row:
            return self._row_to_metadata(row)
        
        return None
    
    def _get_artifact_version(self, artifact_id: str) -> Optional[int]:
        """Get artifact version."""
        metadata = self._get_artifact_metadata(artifact_id)
        return metadata.version if metadata else None
    
    def _row_to_metadata(self, row: sqlite3.Row) -> ArtifactMetadata:
        """Convert database row to ArtifactMetadata."""
        return ArtifactMetadata(
            artifact_id=row["artifact_id"],
            artifact_type=ArtifactType(row["artifact_type"]),
            status=ArtifactStatus(row["status"]),
            created_by=row["created_by"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            version=row["version"],
            parent_id=row["parent_id"],
            execution_id=row["execution_id"],
            tags=json.loads(row["tags"]) if row["tags"] else [],
            checksum=row["checksum"]
        )

