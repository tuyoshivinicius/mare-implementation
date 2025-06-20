"""
MARE CLI - Agent Factory
Factory for creating and configuring MARE agents
"""

from typing import Dict, Any, Optional, Type
from mare.agents.base import AbstractAgent, AgentRole, AgentConfig
from mare.agents.stakeholder import StakeholderAgent
from mare.agents.collector import CollectorAgent
from mare.agents.modeler import ModelerAgent
from mare.agents.checker import CheckerAgent
from mare.agents.documenter import DocumenterAgent
from mare.utils.exceptions import ConfigurationError
from mare.utils.logging import get_logger

logger = get_logger(__name__)


class AgentFactory:
    """
    Factory class for creating MARE agents.
    
    Provides centralized agent creation and configuration management.
    """
    
    # Mapping of agent roles to their implementation classes
    AGENT_CLASSES: Dict[AgentRole, Type[AbstractAgent]] = {
        AgentRole.STAKEHOLDER: StakeholderAgent,
        AgentRole.COLLECTOR: CollectorAgent,
        AgentRole.MODELER: ModelerAgent,
        AgentRole.CHECKER: CheckerAgent,
        AgentRole.DOCUMENTER: DocumenterAgent
    }
    
    @classmethod
    def create_agent(
        cls, 
        role: AgentRole, 
        config: AgentConfig
    ) -> AbstractAgent:
        """
        Create an agent instance for the specified role.
        
        Args:
            role: The role of the agent to create
            config: Configuration for the agent
            
        Returns:
            Configured agent instance
            
        Raises:
            ConfigurationError: If agent role is not supported or configuration is invalid
        """
        if role not in cls.AGENT_CLASSES:
            raise ConfigurationError(
                f"Unsupported agent role: {role.value}",
                config_file="agent_factory"
            )
        
        agent_class = cls.AGENT_CLASSES[role]
        
        try:
            logger.info(f"Creating {role.value} agent with model {config.model_name}")
            agent = agent_class(config)
            logger.info(f"Successfully created {role.value} agent")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create {role.value} agent: {e}")
            raise ConfigurationError(
                f"Failed to create {role.value} agent: {e}",
                config_file="agent_factory"
            )
    
    @classmethod
    def create_agent_from_dict(
        cls, 
        role: AgentRole, 
        config_dict: Dict[str, Any]
    ) -> AbstractAgent:
        """
        Create an agent from a configuration dictionary.
        
        Args:
            role: The role of the agent to create
            config_dict: Configuration dictionary
            
        Returns:
            Configured agent instance
        """
        config = AgentConfig(
            role=role,
            model_name=config_dict.get('model', 'gpt-3.5-turbo'),
            temperature=config_dict.get('temperature', 0.7),
            max_tokens=config_dict.get('max_tokens', 2048),
            system_prompt=config_dict.get('system_prompt'),
            enabled=config_dict.get('enabled', True),
            custom_parameters=config_dict.get('custom_parameters')
        )
        
        return cls.create_agent(role, config)
    
    @classmethod
    def create_all_agents(
        cls, 
        agent_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[AgentRole, AbstractAgent]:
        """
        Create all agents from configuration.
        
        Args:
            agent_configs: Dictionary mapping agent names to their configurations
            
        Returns:
            Dictionary mapping agent roles to agent instances
        """
        agents = {}
        
        for role in AgentRole:
            role_name = role.value
            if role_name in agent_configs:
                config_dict = agent_configs[role_name]
                if config_dict.get('enabled', True):
                    try:
                        agent = cls.create_agent_from_dict(role, config_dict)
                        agents[role] = agent
                        logger.info(f"Created and registered {role_name} agent")
                    except Exception as e:
                        logger.error(f"Failed to create {role_name} agent: {e}")
                        # Continue creating other agents even if one fails
                else:
                    logger.info(f"Skipping disabled {role_name} agent")
            else:
                logger.warning(f"No configuration found for {role_name} agent")
        
        return agents
    
    @classmethod
    def get_default_config(cls, role: AgentRole) -> AgentConfig:
        """
        Get default configuration for an agent role.
        
        Args:
            role: Agent role
            
        Returns:
            Default configuration for the role
        """
        default_configs = {
            AgentRole.STAKEHOLDER: AgentConfig(
                role=role,
                model_name="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=2048
            ),
            AgentRole.COLLECTOR: AgentConfig(
                role=role,
                model_name="gpt-3.5-turbo",
                temperature=0.6,
                max_tokens=2048
            ),
            AgentRole.MODELER: AgentConfig(
                role=role,
                model_name="gpt-4",
                temperature=0.5,
                max_tokens=2048
            ),
            AgentRole.CHECKER: AgentConfig(
                role=role,
                model_name="gpt-4",
                temperature=0.3,
                max_tokens=2048
            ),
            AgentRole.DOCUMENTER: AgentConfig(
                role=role,
                model_name="gpt-3.5-turbo",
                temperature=0.4,
                max_tokens=4096
            )
        }
        
        return default_configs.get(role, AgentConfig(role=role, model_name="gpt-3.5-turbo"))
    
    @classmethod
    def validate_agent_config(cls, config: AgentConfig) -> bool:
        """
        Validate agent configuration.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if configuration is valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        if not config.model_name:
            raise ConfigurationError(
                "Model name is required for agent configuration",
                config_file="agent_config"
            )
        
        if config.temperature < 0 or config.temperature > 2:
            raise ConfigurationError(
                "Temperature must be between 0 and 2",
                config_file="agent_config"
            )
        
        if config.max_tokens <= 0:
            raise ConfigurationError(
                "Max tokens must be positive",
                config_file="agent_config"
            )
        
        if config.role not in cls.AGENT_CLASSES:
            raise ConfigurationError(
                f"Unsupported agent role: {config.role.value}",
                config_file="agent_config"
            )
        
        return True

