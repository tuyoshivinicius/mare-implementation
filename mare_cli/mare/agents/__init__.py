"""
MARE CLI - Agents Module
Multi-agent system for requirements engineering
"""

from mare.agents.base import (
    AbstractAgent,
    AgentRole,
    ActionType,
    AgentAction,
    AgentConfig
)

from mare.agents.stakeholder import StakeholderAgent
from mare.agents.collector import CollectorAgent
from mare.agents.modeler import ModelerAgent
from mare.agents.checker import CheckerAgent
from mare.agents.documenter import DocumenterAgent
from mare.agents.factory import AgentFactory

__all__ = [
    # Base classes and enums
    'AbstractAgent',
    'AgentRole',
    'ActionType',
    'AgentAction',
    'AgentConfig',
    
    # Agent implementations
    'StakeholderAgent',
    'CollectorAgent',
    'ModelerAgent',
    'CheckerAgent',
    'DocumenterAgent',
    
    # Factory
    'AgentFactory'
]

