"""
MARE CLI - Workspace Module
Shared workspace for agent collaboration and artifact management
"""

from mare.workspace.storage import (
    WorkspaceStorage,
    WorkspaceArtifact,
    ArtifactType,
    ArtifactStatus,
    ArtifactMetadata
)

from mare.workspace.shared_workspace import SharedWorkspace

__all__ = [
    'WorkspaceStorage',
    'WorkspaceArtifact',
    'ArtifactType',
    'ArtifactStatus',
    'ArtifactMetadata',
    'SharedWorkspace'
]

