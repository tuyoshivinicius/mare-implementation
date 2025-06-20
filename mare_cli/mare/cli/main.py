#!/usr/bin/env python3
"""
MARE CLI - Multi-Agent Collaboration Framework for Requirements Engineering
Main CLI entry point and command dispatcher
"""

import sys
import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from pathlib import Path
import logging

from mare.cli.commands.init import init_command
from mare.cli.commands.run import run_command
from mare.cli.commands.status import status_command
from mare.cli.commands.export import export_command
from mare.utils.logging import setup_logging
from mare.utils.exceptions import MAREException

# Initialize rich console for beautiful output
console = Console()

# ASCII Art for MARE CLI
MARE_LOGO = """
███╗   ███╗ █████╗ ██████╗ ███████╗
████╗ ████║██╔══██╗██╔══██╗██╔════╝
██╔████╔██║███████║██████╔╝█████╗  
██║╚██╔╝██║██╔══██║██╔══██╗██╔══╝  
██║ ╚═╝ ██║██║  ██║██║  ██║███████╗
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
Multi-Agent Requirements Engineering
"""

@click.group()
@click.version_option(version="1.0.0", prog_name="MARE CLI")
@click.option(
    "--verbose", "-v", 
    is_flag=True, 
    help="Enable verbose output"
)
@click.option(
    "--debug", 
    is_flag=True, 
    help="Enable debug mode"
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="Path to configuration file"
)
@click.pass_context
def cli(ctx, verbose, debug, config):
    """
    MARE CLI - Multi-Agent Collaboration Framework for Requirements Engineering
    
    A powerful CLI tool that implements the MARE framework for automated
    requirements engineering using collaborative AI agents.
    
    Based on the paper: "MARE: Multi-Agents Collaboration Framework for 
    Requirements Engineering" (https://arxiv.org/abs/2405.03256)
    """
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Store global options in context
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug
    ctx.obj['config'] = config
    
    # Setup logging
    log_level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
    setup_logging(log_level)
    
    # Display logo in debug mode
    if debug:
        console.print(Panel(
            Text(MARE_LOGO, style="bold blue"),
            title="[bold green]MARE CLI v1.0.0[/bold green]",
            subtitle="[italic]Multi-Agent Requirements Engineering[/italic]"
        ))

@cli.command()
@click.argument('project_name', required=False)
@click.option(
    '--template', '-t',
    type=click.Choice(['basic', 'web_app', 'mobile_app', 'enterprise']),
    default='basic',
    help='Project template to use'
)
@click.option(
    '--llm-provider',
    type=click.Choice(['openai', 'anthropic', 'local']),
    default='openai',
    help='LLM provider to configure'
)
@click.option(
    '--force', '-f',
    is_flag=True,
    help='Force initialization even if directory exists'
)
@click.pass_context
def init(ctx, project_name, template, llm_provider, force):
    """
    Initialize a new MARE project with the specified configuration.
    
    Creates project structure, configuration files, and workspace setup.
    
    Examples:
        mare init my_project
        mare init my_project --template web_app --llm-provider openai
    """
    try:
        init_command(ctx, project_name, template, llm_provider, force)
    except MAREException as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        if ctx.obj.get('debug'):
            raise
        sys.exit(1)

@cli.command()
@click.option(
    '--phase', '-p',
    type=click.Choice(['elicitation', 'modeling', 'verification', 'specification']),
    help='Run specific phase only'
)
@click.option(
    '--interactive', '-i',
    is_flag=True,
    help='Run in interactive mode with step-by-step execution'
)
@click.option(
    '--input-file', '-f',
    type=click.Path(exists=True),
    help='Input file with initial requirements'
)
@click.option(
    '--max-iterations',
    type=int,
    default=5,
    help='Maximum number of refinement iterations'
)
@click.pass_context
def run(ctx, phase, interactive, input_file, max_iterations):
    """
    Execute the MARE pipeline to process requirements.
    
    Runs the complete multi-agent collaboration process or specific phases
    to transform initial requirements into structured specifications.
    
    Examples:
        mare run
        mare run --phase elicitation --interactive
        mare run --input-file requirements.txt --max-iterations 3
    """
    try:
        run_command(ctx, phase, interactive, input_file, max_iterations)
    except MAREException as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        if ctx.obj.get('debug'):
            raise
        sys.exit(1)

@cli.command()
@click.option(
    '--detailed', '-d',
    is_flag=True,
    help='Show detailed status information'
)
@click.option(
    '--artifacts', '-a',
    is_flag=True,
    help='List all artifacts in workspace'
)
@click.option(
    '--quality', '-q',
    is_flag=True,
    help='Show quality metrics and analysis'
)
@click.pass_context
def status(ctx, detailed, artifacts, quality):
    """
    Display current project status and progress information.
    
    Shows pipeline state, artifact status, quality metrics, and execution history.
    
    Examples:
        mare status
        mare status --detailed --quality
        mare status --artifacts
    """
    try:
        status_command(ctx, detailed, artifacts, quality)
    except MAREException as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        if ctx.obj.get('debug'):
            raise
        sys.exit(1)

@cli.command()
@click.argument(
    'format',
    type=click.Choice(['json', 'markdown', 'pdf', 'xml']),
    default='json'
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    help='Output file path'
)
@click.option(
    '--template',
    type=click.Path(exists=True),
    help='Custom template file for formatting'
)
@click.option(
    '--include-metadata',
    is_flag=True,
    help='Include metadata and traceability information'
)
@click.option(
    '--quality-report',
    is_flag=True,
    help='Include quality analysis report'
)
@click.pass_context
def export(ctx, format, output, template, include_metadata, quality_report):
    """
    Export project results in the specified format.
    
    Generates final documentation, specifications, or reports from the
    processed requirements and artifacts.
    
    Examples:
        mare export json
        mare export markdown --output requirements.md
        mare export pdf --template custom_template.html --include-metadata
    """
    try:
        export_command(ctx, format, output, template, include_metadata, quality_report)
    except MAREException as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        if ctx.obj.get('debug'):
            raise
        sys.exit(1)

def main():
    """Main entry point for the MARE CLI application."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Fatal error:[/red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

