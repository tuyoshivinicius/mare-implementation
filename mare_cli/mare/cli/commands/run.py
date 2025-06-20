"""
MARE CLI - Run command implementation
Handles pipeline execution and orchestration
"""

from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table

from mare.pipeline import PipelineExecutor
from mare.utils.exceptions import PipelineExecutionError
from mare.utils.helpers import find_project_root, validate_project_structure
from mare.utils.logging import get_logger

console = Console()
logger = get_logger(__name__)

def run_command(
    ctx: click.Context,
    phase: Optional[str],
    interactive: bool,
    input_file: Optional[str],
    max_iterations: int,
    timeout: int = 300
) -> None:
    """
    Execute the MARE pipeline.
    
    Args:
        ctx: Click context object
        phase: Specific phase to run
        interactive: Run in interactive mode
        input_file: Input file with requirements
        max_iterations: Maximum number of iterations
    """
    logger.info("Starting pipeline execution")
    
    # Find project root
    project_root = find_project_root()
    if not project_root:
        raise PipelineExecutionError(
            "No MARE project found. Run 'mare init' to create a new project."
        )
    
    # Validate project structure
    if not validate_project_structure(project_root):
        raise PipelineExecutionError(
            "Invalid project structure. Please check your project configuration."
        )
    
    try:
        # Initialize pipeline executor
        console.print(Panel(
            f"[blue]Initializing MARE Pipeline[/blue]\n\n"
            f"[bold]Project:[/bold] {project_root.name}\n"
            f"[bold]Phase:[/bold] {phase or 'all'}\n"
            f"[bold]Interactive:[/bold] {interactive}\n"
            f"[bold]Input file:[/bold] {input_file or 'default'}\n"
            f"[bold]Max iterations:[/bold] {max_iterations}",
            title="[bold blue]MARE Pipeline Execution[/bold blue]",
            border_style="blue"
        ))
        
        executor = PipelineExecutor(project_root)
        
        # Prepare input file path
        input_path = None
        if input_file:
            input_path = Path(input_file)
            if not input_path.is_absolute():
                input_path = project_root / input_path
        
        # Execute pipeline with progress tracking
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            
            # Create progress tasks for each phase
            task_init = progress.add_task("Initializing agents...", total=100)
            progress.update(task_init, advance=20)
            
            task_exec = progress.add_task("Executing pipeline...", total=100)
            
            # Execute the pipeline
            result = executor.execute_pipeline(
                input_file=input_path,
                interactive=interactive,
                max_iterations=max_iterations,
                timeout=timeout
            )
            
            progress.update(task_init, completed=100)
            progress.update(task_exec, completed=100)
        
        # Display results
        _display_execution_results(result)
        
        logger.info("Pipeline execution completed successfully")
        
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        console.print(Panel(
            f"[red]Pipeline execution failed:[/red]\n\n"
            f"[bold]Error:[/bold] {str(e)}\n\n"
            f"[dim]Check the logs for more details.[/dim]",
            title="[bold red]Execution Failed[/bold red]",
            border_style="red"
        ))
        raise PipelineExecutionError(f"Pipeline execution failed: {e}")

def _display_execution_results(result: dict) -> None:
    """Display pipeline execution results."""
    
    # Status panel
    status_color = "green" if result["status"] == "completed" else "red"
    console.print(Panel(
        f"[{status_color}]Pipeline Status: {result['status'].upper()}[/{status_color}]\n\n"
        f"[bold]Execution ID:[/bold] {result['execution_id'][:8]}...\n"
        f"[bold]Quality Score:[/bold] {result['quality_score']:.1f}/10\n"
        f"[bold]Iterations:[/bold] {result['iterations']}\n"
        f"[bold]Issues Found:[/bold] {len(result['issues_found'])}",
        title="[bold]Execution Summary[/bold]",
        border_style=status_color
    ))
    
    # Artifacts summary
    artifacts = result["artifacts"]
    artifacts_table = Table(title="Generated Artifacts")
    artifacts_table.add_column("Artifact", style="cyan", no_wrap=True)
    artifacts_table.add_column("Status", style="magenta")
    artifacts_table.add_column("Size", style="green")
    
    artifact_info = [
        ("User Stories", artifacts["user_stories"]),
        ("Requirements Draft", artifacts["requirements"]),
        ("System Entities", artifacts["entities"]),
        ("Entity Relationships", artifacts["relationships"]),
        ("Quality Check Results", artifacts["check_results"]),
        ("Final SRS Document", artifacts["final_srs"])
    ]
    
    for name, content in artifact_info:
        if content:
            status = "[green]✓ Generated[/green]"
            size = f"{len(content)} chars"
        else:
            status = "[red]✗ Missing[/red]"
            size = "0 chars"
        
        artifacts_table.add_row(name, status, size)
    
    console.print(artifacts_table)
    
    # Issues summary if any
    if result["issues_found"]:
        console.print(Panel(
            f"[yellow]Quality issues were found during verification.[/yellow]\n\n"
            f"Run 'mare status --quality' for detailed analysis.",
            title="[bold yellow]Quality Issues[/bold yellow]",
            border_style="yellow"
        ))
    
    # Success message
    if result["status"] == "completed":
        console.print(Panel(
            f"[green]✓ Pipeline execution completed successfully![/green]\n\n"
            f"[bold]Next steps:[/bold]\n"
            f"1. Review generated artifacts: 'mare status --artifacts'\n"
            f"2. Export final specification: 'mare export markdown'\n"
            f"3. Check quality metrics: 'mare status --quality'\n\n"
            f"[dim]Final SRS saved to: output/requirements_specification.md[/dim]",
            title="[bold green]Execution Complete[/bold green]",
            border_style="green"
        ))
    else:
        error_msg = result.get("error_message", "Unknown error")
        console.print(Panel(
            f"[red]Pipeline execution failed.[/red]\n\n"
            f"[bold]Error:[/bold] {error_msg}\n\n"
            f"[bold]Troubleshooting:[/bold]\n"
            f"1. Check your API keys in .env file\n"
            f"2. Verify input requirements in input/requirements.md\n"
            f"3. Review logs for detailed error information\n"
            f"4. Try running with --interactive flag for step-by-step execution",
            title="[bold red]Execution Failed[/bold red]",
            border_style="red"
        ))

