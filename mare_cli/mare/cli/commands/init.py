"""
MARE CLI - Init command implementation
Handles project initialization and setup
"""

import os
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from mare.utils.exceptions import ProjectInitializationError, ConfigurationError
from mare.utils.helpers import (
    ensure_directory, 
    write_yaml_file, 
    write_json_file,
    generate_uuid
)
from mare.utils.logging import get_logger

console = Console()
logger = get_logger(__name__)

def init_command(
    ctx: click.Context,
    project_name: Optional[str],
    template: str,
    llm_provider: str,
    force: bool
) -> None:
    """
    Initialize a new MARE project.
    
    Args:
        ctx: Click context object
        project_name: Name of the project to create
        template: Project template to use
        llm_provider: LLM provider to configure
        force: Force initialization even if directory exists
    """
    logger.info("Starting project initialization")
    
    # Determine project name and path
    if project_name is None:
        project_name = click.prompt("Enter project name")
    
    project_path = Path.cwd() / project_name
    
    # Check if project already exists
    if project_path.exists() and not force:
        if not click.confirm(f"Directory '{project_name}' already exists. Continue?"):
            raise ProjectInitializationError(
                "Project initialization cancelled by user",
                str(project_path)
            )
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Create project structure
            task1 = progress.add_task("Creating project structure...", total=None)
            _create_project_structure(project_path)
            progress.update(task1, completed=True)
            
            # Generate configuration
            task2 = progress.add_task("Generating configuration...", total=None)
            _create_project_config(project_path, template, llm_provider)
            progress.update(task2, completed=True)
            
            # Initialize workspace
            task3 = progress.add_task("Initializing workspace...", total=None)
            _initialize_workspace(project_path)
            progress.update(task3, completed=True)
            
            # Create example files
            task4 = progress.add_task("Creating example files...", total=None)
            _create_example_files(project_path, template, llm_provider)
            progress.update(task4, completed=True)
        
        # Success message
        console.print(Panel(
            f"[green]✓[/green] Project '{project_name}' initialized successfully!\n\n"
            f"[bold]Next steps:[/bold]\n"
            f"1. cd {project_name}\n"
            f"2. Configure your LLM API keys in .mare/config.yaml\n"
            f"3. Run 'mare run' to start processing requirements\n\n"
            f"[dim]Template: {template} | LLM Provider: {llm_provider}[/dim]",
            title="[bold green]Project Initialized[/bold green]",
            border_style="green"
        ))
        
        logger.info(f"Project '{project_name}' initialized successfully at {project_path}")
        
    except Exception as e:
        logger.error(f"Failed to initialize project: {e}")
        raise ProjectInitializationError(
            f"Failed to initialize project: {e}",
            str(project_path)
        )

def _create_project_structure(project_path: Path) -> None:
    """Create the basic project directory structure."""
    directories = [
        ".mare",
        ".mare/workspace",
        ".mare/logs",
        ".mare/cache",
        "input",
        "output",
        "templates"
    ]
    
    for directory in directories:
        ensure_directory(project_path / directory)

def _create_project_config(project_path: Path, template: str, llm_provider: str) -> None:
    """Create project configuration files."""
    
    # Main configuration
    config = {
        "project": {
            "name": project_path.name,
            "id": generate_uuid(),
            "template": template,
            "created_at": "2025-06-20T05:00:00",
            "version": "1.0.0"
        },
        "llm": {
            "provider": llm_provider,
            "models": _get_default_models(llm_provider),
            "parameters": _get_default_parameters()
        },
        "agents": {
            "stakeholder": {"enabled": True, "model": "default"},
            "collector": {"enabled": True, "model": "default"},
            "modeler": {"enabled": True, "model": "default"},
            "checker": {"enabled": True, "model": "default"},
            "documenter": {"enabled": True, "model": "default"}
        },
        "pipeline": {
            "max_iterations": 5,
            "quality_threshold": 0.8,
            "auto_advance": True
        },
        "workspace": {
            "storage_type": "sqlite",
            "versioning": True,
            "backup": True
        }
    }
    
    write_yaml_file(project_path / ".mare" / "config.yaml", config)
    
    # Environment template
    env_template = f"""# MARE CLI Environment Configuration
# Copy this file to .env and fill in your API keys

# LLM Provider Configuration
MARE_LLM_PROVIDER={llm_provider}

# OpenAI Configuration (if using OpenAI)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Configuration (if using Anthropic)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Local LLM Configuration (if using local models)
LOCAL_LLM_ENDPOINT=http://localhost:8000

# Logging Configuration
MARE_LOG_LEVEL=INFO
MARE_LOG_FILE=.mare/logs/mare.log

# Workspace Configuration
MARE_WORKSPACE_PATH=.mare/workspace
"""
    
    with open(project_path / ".env.template", "w") as f:
        f.write(env_template)

def _get_default_models(provider: str) -> dict:
    """Get default model configuration for provider."""
    models = {
        "openai": {
            "default": "gpt-3.5-turbo",
            "stakeholder": "gpt-3.5-turbo",
            "collector": "gpt-3.5-turbo",
            "modeler": "gpt-4",
            "checker": "gpt-4",
            "documenter": "gpt-3.5-turbo"
        },
        "anthropic": {
            "default": "claude-3-sonnet-20240229",
            "stakeholder": "claude-3-sonnet-20240229",
            "collector": "claude-3-sonnet-20240229",
            "modeler": "claude-3-opus-20240229",
            "checker": "claude-3-opus-20240229",
            "documenter": "claude-3-sonnet-20240229"
        },
        "local": {
            "default": "llama2",
            "stakeholder": "llama2",
            "collector": "llama2",
            "modeler": "llama2",
            "checker": "llama2",
            "documenter": "llama2"
        }
    }
    
    return models.get(provider, models["openai"])

def _get_default_parameters() -> dict:
    """Get default LLM parameters."""
    return {
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }

def _initialize_workspace(project_path: Path) -> None:
    """Initialize the workspace database and structure."""
    workspace_config = {
        "version": "1.0.0",
        "created_at": "2025-06-20T05:00:00",
        "artifacts": {},
        "versions": {},
        "metadata": {
            "total_artifacts": 0,
            "last_updated": "2025-06-20T05:00:00"
        }
    }
    
    write_json_file(
        project_path / ".mare" / "workspace" / "workspace.json",
        workspace_config
    )

def _create_example_files(project_path: Path, template: str, llm_provider: str) -> None:
    """Create example input files based on template."""
    
    examples = {
        "basic": """# Example Requirements Input

## System Overview
I want to develop a simple task management system.

## User Stories
- As a user, I want to create tasks so that I can track my work
- As a user, I want to mark tasks as complete so that I can see my progress
- As a user, I want to delete tasks so that I can remove unnecessary items
""",
        "web_app": """# Web Application Requirements

## System Overview
I want to develop a web-based e-commerce platform for selling books online.

## User Stories
- As a customer, I want to browse books by category so that I can find what I'm looking for
- As a customer, I want to add books to my cart so that I can purchase multiple items
- As a customer, I want to create an account so that I can track my orders
- As an admin, I want to manage inventory so that I can keep track of stock levels
""",
        "mobile_app": """# Mobile Application Requirements

## System Overview
I want to develop a mobile fitness tracking application.

## User Stories
- As a user, I want to log my workouts so that I can track my fitness progress
- As a user, I want to set fitness goals so that I can stay motivated
- As a user, I want to view my progress charts so that I can see my improvement over time
- As a user, I want to share my achievements so that I can motivate others
""",
        "enterprise": """# Enterprise System Requirements

## System Overview
I want to develop an enterprise resource planning (ERP) system for manufacturing companies.

## User Stories
- As a manager, I want to track production schedules so that I can ensure timely delivery
- As an employee, I want to log work hours so that payroll can be processed accurately
- As a supervisor, I want to monitor quality metrics so that I can maintain standards
- As an administrator, I want to generate reports so that I can analyze business performance
"""
    }
    
    example_content = examples.get(template, examples["basic"])
    
    with open(project_path / "input" / "requirements.md", "w") as f:
        f.write(example_content)
    
    # Create README
    readme_content = f"""# {project_path.name}

MARE CLI project for automated requirements engineering.

## Getting Started

1. Configure your LLM API keys in `.env` (copy from `.env.template`)
2. Edit `input/requirements.md` with your actual requirements
3. Run the pipeline: `mare run`
4. Check status: `mare status`
5. Export results: `mare export markdown`

## Project Structure

- `input/` - Input requirements and user stories
- `output/` - Generated specifications and reports
- `.mare/` - MARE CLI configuration and workspace
- `templates/` - Custom templates for output formatting

## Template: {template}
## LLM Provider: {llm_provider}

For more information, visit: https://github.com/manus-ai/mare-cli
"""
    
    with open(project_path / "README.md", "w") as f:
        f.write(readme_content)

