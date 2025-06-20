"""
MARE CLI - Exceções customizadas
Define classes de exceção customizadas para a aplicação MARE CLI
"""

from typing import Optional, Dict, Any


class MAREException(Exception):
    """
    Classe base de exceção para todos os erros do MARE CLI.
    
    Fornece tratamento estruturado de erros com informações de contexto.
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "MARE_GENERAL_ERROR"
        self.context = context or {}
    
    def __str__(self) -> str:
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (Código: {self.error_code}, Contexto: {context_str})"
        return f"{self.message} (Código: {self.error_code})"


class ProjectInitializationError(MAREException):
    """Lançada quando a inicialização do projeto falha."""
    
    def __init__(self, message: str, project_path: Optional[str] = None):
        super().__init__(
            message, 
            error_code="MARE_INIT_ERROR",
            context={"project_path": project_path} if project_path else None
        )


class ConfigurationError(MAREException):
    """Lançada quando a configuração é inválida ou está ausente."""
    
    def __init__(self, message: str, config_file: Optional[str] = None):
        super().__init__(
            message,
            error_code="MARE_CONFIG_ERROR",
            context={"config_file": config_file} if config_file else None
        )


class WorkspaceError(MAREException):
    """Lançada quando operações do workspace falham."""
    
    def __init__(self, message: str, workspace_path: Optional[str] = None):
        super().__init__(
            message,
            error_code="MARE_WORKSPACE_ERROR",
            context={"workspace_path": workspace_path} if workspace_path else None
        )


class AgentExecutionError(MAREException):
    """Lançada quando a execução do agente falha."""
    
    def __init__(
        self, 
        message: str, 
        agent_name: Optional[str] = None,
        action: Optional[str] = None
    ):
        context = {}
        if agent_name:
            context["agent_name"] = agent_name
        if action:
            context["action"] = action
        
        super().__init__(
            message,
            error_code="MARE_AGENT_ERROR",
            context=context if context else None
        )


class PipelineExecutionError(MAREException):
    """Lançada quando a execução do pipeline falha."""
    
    def __init__(
        self, 
        message: str, 
        phase: Optional[str] = None,
        step: Optional[str] = None
    ):
        context = {}
        if phase:
            context["phase"] = phase
        if step:
            context["step"] = step
        
        super().__init__(
            message,
            error_code="MARE_PIPELINE_ERROR",
            context=context if context else None
        )


class ValidationError(MAREException):
    """Raised when validation fails."""
    
    def __init__(
        self, 
        message: str, 
        artifact_type: Optional[str] = None,
        validation_rule: Optional[str] = None
    ):
        context = {}
        if artifact_type:
            context["artifact_type"] = artifact_type
        if validation_rule:
            context["validation_rule"] = validation_rule
        
        super().__init__(
            message,
            error_code="MARE_VALIDATION_ERROR",
            context=context if context else None
        )


class LLMProviderError(MAREException):
    """Raised when LLM provider operations fail."""
    
    def __init__(
        self, 
        message: str, 
        provider: Optional[str] = None,
        model: Optional[str] = None
    ):
        context = {}
        if provider:
            context["provider"] = provider
        if model:
            context["model"] = model
        
        super().__init__(
            message,
            error_code="MARE_LLM_ERROR",
            context=context if context else None
        )


class ExportError(MAREException):
    """Raised when export operations fail."""
    
    def __init__(
        self, 
        message: str, 
        format_type: Optional[str] = None,
        output_path: Optional[str] = None
    ):
        context = {}
        if format_type:
            context["format_type"] = format_type
        if output_path:
            context["output_path"] = output_path
        
        super().__init__(
            message,
            error_code="MARE_EXPORT_ERROR",
            context=context if context else None
        )


class ArtifactError(MAREException):
    """Raised when artifact operations fail."""
    
    def __init__(
        self, 
        message: str, 
        artifact_id: Optional[str] = None,
        operation: Optional[str] = None
    ):
        context = {}
        if artifact_id:
            context["artifact_id"] = artifact_id
        if operation:
            context["operation"] = operation
        
        super().__init__(
            message,
            error_code="MARE_ARTIFACT_ERROR",
            context=context if context else None
        )

