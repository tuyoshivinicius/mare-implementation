"""
MARE CLI - Utilitários de logging
Fornece configuração de logging estruturado para a aplicação MARE CLI
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console

# Instância global do console
console = Console()

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configura logging estruturado para o MARE CLI.
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Caminho opcional do arquivo para saída de log
        format_string: String de formato customizada para mensagens de log
    
    Returns:
        Instância de logger configurada
    """
    # String de formato padrão
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Criar logger raiz
    logger = logging.getLogger("mare")
    logger.setLevel(level)
    
    # Limpar handlers existentes
    logger.handlers.clear()
    
    # Adicionar handler rich para saída do console
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True
    )
    rich_handler.setLevel(level)
    logger.addHandler(rich_handler)
    
    # Adicionar handler de arquivo se especificado
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """
    Obtém uma instância de logger para um módulo específico.
    
    Args:
        name: Nome do logger (tipicamente __name__)
    
    Returns:
        Instância do logger
    """
    return logging.getLogger(f"mare.{name}")

class MARELoggerMixin:
    """
    Classe mixin que fornece capacidades de logging para outras classes.
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Obtém instância de logger para esta classe."""
        return get_logger(self.__class__.__module__)
    
    def log_info(self, message: str, **kwargs) -> None:
        """Registra mensagem de info com contexto opcional."""
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs) -> None:
        """Registra mensagem de warning com contexto opcional."""
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs) -> None:
        """Registra mensagem de erro com contexto opcional."""
        self.logger.error(message, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs) -> None:
        """Registra mensagem de debug com contexto opcional."""
        self.logger.debug(message, extra=kwargs)

