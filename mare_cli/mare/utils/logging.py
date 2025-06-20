"""
MARE CLI - Logging utilities
Provides structured logging configuration for the MARE CLI application
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console

# Global console instance
console = Console()

def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Setup structured logging for MARE CLI.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        format_string: Custom format string for log messages
    
    Returns:
        Configured logger instance
    """
    # Default format string
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create root logger
    logger = logging.getLogger("mare")
    logger.setLevel(level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Add rich handler for console output
    rich_handler = RichHandler(
        console=console,
        show_time=True,
        show_path=True,
        markup=True,
        rich_tracebacks=True
    )
    rich_handler.setLevel(level)
    logger.addHandler(rich_handler)
    
    # Add file handler if specified
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
    Get a logger instance for a specific module.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(f"mare.{name}")

class MARELoggerMixin:
    """
    Mixin class that provides logging capabilities to other classes.
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger instance for this class."""
        return get_logger(self.__class__.__module__)
    
    def log_info(self, message: str, **kwargs) -> None:
        """Log info message with optional context."""
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs) -> None:
        """Log warning message with optional context."""
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs) -> None:
        """Log error message with optional context."""
        self.logger.error(message, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs) -> None:
        """Log debug message with optional context."""
        self.logger.debug(message, extra=kwargs)

