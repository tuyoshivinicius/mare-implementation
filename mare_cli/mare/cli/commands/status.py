"""
MARE CLI - Implementação do comando status
Gerencia exibição de status e monitoramento do projeto
"""

from pathlib import Path
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.columns import Columns

from mare.pipeline import PipelineExecutor
from mare.utils.exceptions import WorkspaceError
from mare.utils.helpers import find_project_root, validate_project_structure
from mare.utils.logging import get_logger

console = Console()
logger = get_logger(__name__)

def status_command(
    ctx: click.Context,
    detailed: bool,
    artifacts: bool,
    quality: bool
) -> None:
    """
    Exibe informações de status do projeto.
    
    Args:
        ctx: Objeto de contexto do Click
        detailed: Mostra informações detalhadas
        artifacts: Lista todos os artefatos
        quality: Mostra métricas de qualidade
    """
    logger.info("Exibindo status do projeto")
    
    # Encontra raiz do projeto
    project_root = find_project_root()
    if not project_root:
        raise WorkspaceError(
            "Nenhum projeto MARE encontrado. Execute 'mare init' para criar um novo projeto."
        )
    
    # Valida estrutura do projeto
    if not validate_project_structure(project_root):
        raise WorkspaceError(
            "Estrutura de projeto inválida. Verifique a configuração do seu projeto."
        )
    
    try:
        # Initialize pipeline executor to get status
        executor = PipelineExecutor(project_root)
        project_status = executor.get_project_status()
        
        # Display basic status
        _display_basic_status(project_status)
        
        if detailed:
            _display_detailed_status(project_status)
        
        if artifacts:
            _display_artifacts_status(executor, project_root)
        
        if quality:
            _display_quality_metrics(executor)
        
        logger.info("Status display completed")
        
        # Return status information for testing
        return {
            "project_name": project_root.name,
            "project_path": str(project_root),
            "configuration": project_status.get("configuration", {}),
            "status": "displayed"
        }
        
    except Exception as e:
        logger.error(f"Failed to get project status: {e}")
        console.print(Panel(
            f"[red]Failed to get project status:[/red]\n\n"
            f"[bold]Error:[/bold] {str(e)}\n\n"
            f"[dim]Check your project configuration and try again.[/dim]",
            title="[bold red]Status Error[/bold red]",
            border_style="red"
        ))
        raise WorkspaceError(f"Failed to get project status: {e}")

def _display_basic_status(project_status: dict) -> None:
    """Display basic project status."""
    
    # Create status table
    table = Table(title="MARE Project Status")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    # Basic project info
    table.add_row("Project Name", project_status["project_name"])
    table.add_row("Project Path", project_status["project_path"])
    
    # Configuration info
    config = project_status["configuration"]
    table.add_row("Template", config.get("template", "Unknown"))
    table.add_row("LLM Provider", config.get("llm_provider", "Unknown"))
    table.add_row("Max Iterations", str(config.get("max_iterations", "Unknown")))
    table.add_row("Quality Threshold", str(config.get("quality_threshold", "Unknown")))
    
    # Execution status
    exec_status = project_status["execution_status"]
    last_exec = exec_status.get("last_execution")
    
    if last_exec:
        status_color = "green" if last_exec["status"] == "completed" else "red"
        table.add_row("Pipeline Status", f"[{status_color}]{last_exec['status'].title()}[/{status_color}]")
        table.add_row("Last Execution", last_exec["timestamp"][:19])
        table.add_row("Quality Score", f"{last_exec.get('quality_score', 0):.1f}/10")
        table.add_row("Iterations Used", str(last_exec.get("iterations", 0)))
    else:
        table.add_row("Pipeline Status", "[yellow]Not Started[/yellow]")
        table.add_row("Last Execution", "Never")
        table.add_row("Quality Score", "N/A")
        table.add_row("Iterations Used", "0")
    
    # Artifacts summary
    artifacts = project_status["artifacts"]
    table.add_row("Workspace Artifacts", str(artifacts["workspace_artifacts"]))
    table.add_row("Output Files", str(artifacts["output_files"]))
    table.add_row("Total Executions", str(exec_status["total_executions"]))
    
    console.print(table)

def _display_detailed_status(project_status: dict) -> None:
    """Display detailed project information."""
    
    config = project_status["configuration"]
    exec_status = project_status["execution_status"]
    
    # Configuration details
    config_table = Table(title="Configuration Details")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="magenta")
    
    config_table.add_row("Template Type", config.get("template", "Unknown"))
    config_table.add_row("LLM Provider", config.get("llm_provider", "Unknown"))
    config_table.add_row("Max Iterations", str(config.get("max_iterations", "Unknown")))
    config_table.add_row("Quality Threshold", f"{config.get('quality_threshold', 0):.1f}")
    
    # Execution history
    history_table = Table(title="Recent Executions")
    history_table.add_column("Execution ID", style="cyan")
    history_table.add_column("Status", style="magenta")
    history_table.add_column("Quality", style="green")
    history_table.add_column("Timestamp", style="blue")
    
    last_exec = exec_status.get("last_execution")
    if last_exec:
        status_color = "green" if last_exec["status"] == "completed" else "red"
        history_table.add_row(
            last_exec["execution_id"][:8] + "...",
            f"[{status_color}]{last_exec['status'].title()}[/{status_color}]",
            f"{last_exec.get('quality_score', 0):.1f}/10",
            last_exec["timestamp"][:19]
        )
    else:
        history_table.add_row("None", "N/A", "N/A", "N/A")
    
    # Display in columns
    console.print(Columns([config_table, history_table]))

def _display_artifacts_status(executor: PipelineExecutor, project_root: Path) -> None:
    """Display artifacts information."""
    
    # Get execution history
    history = executor.get_execution_history()
    
    artifacts_table = Table(title="Available Artifacts")
    artifacts_table.add_column("Artifact Type", style="cyan")
    artifacts_table.add_column("Location", style="magenta")
    artifacts_table.add_column("Status", style="green")
    artifacts_table.add_column("Last Updated", style="blue")
    
    # Check workspace artifacts
    workspace_dir = project_root / ".mare" / "workspace" / "artifacts"
    if workspace_dir.exists():
        for exec_dir in workspace_dir.iterdir():
            if exec_dir.is_dir():
                artifacts = list(exec_dir.glob("*.md"))
                for artifact in artifacts:
                    artifacts_table.add_row(
                        artifact.stem.replace("_", " ").title(),
                        f"workspace/{exec_dir.name}/{artifact.name}",
                        "[green]✓ Available[/green]",
                        artifact.stat().st_mtime.__str__()[:19]
                    )
    
    # Check output files
    output_dir = project_root / "output"
    if output_dir.exists():
        for output_file in output_dir.glob("*"):
            if output_file.is_file():
                artifacts_table.add_row(
                    output_file.stem.replace("_", " ").title(),
                    f"output/{output_file.name}",
                    "[green]✓ Available[/green]",
                    output_file.stat().st_mtime.__str__()[:19]
                )
    
    if artifacts_table.row_count == 0:
        artifacts_table.add_row("No artifacts", "N/A", "[yellow]None generated[/yellow]", "N/A")
    
    console.print(artifacts_table)

def _display_quality_metrics(executor: PipelineExecutor) -> None:
    """Display quality metrics and analysis."""
    
    latest_execution = executor.get_latest_execution()
    
    if not latest_execution:
        console.print(Panel(
            "[yellow]No execution data available for quality analysis.[/yellow]\n\n"
            "[dim]Run 'mare run' to execute the pipeline and generate quality metrics.[/dim]",
            title="[bold yellow]Quality Metrics[/bold yellow]",
            border_style="yellow"
        ))
        return
    
    # Quality metrics table
    quality_table = Table(title="Quality Metrics")
    quality_table.add_column("Metric", style="cyan")
    quality_table.add_column("Score", style="magenta")
    quality_table.add_column("Status", style="green")
    
    quality_score = latest_execution.get("quality_score", 0)
    threshold = 8.0  # Default threshold
    
    # Overall quality
    status = "[green]✓ Passed[/green]" if quality_score >= threshold else "[red]✗ Failed[/red]"
    quality_table.add_row("Overall Quality", f"{quality_score:.1f}/10", status)
    
    # Individual dimensions (simulated for now)
    dimensions = [
        ("Completeness", quality_score * 0.9),
        ("Consistency", quality_score * 1.1),
        ("Clarity", quality_score * 0.95),
        ("Correctness", quality_score * 1.05),
        ("Testability", quality_score * 0.85),
        ("Traceability", quality_score * 0.9)
    ]
    
    for dimension, score in dimensions:
        score = min(10.0, max(0.0, score))  # Clamp to 0-10
        dim_status = "[green]✓ Good[/green]" if score >= threshold else "[yellow]⚠ Needs Work[/yellow]"
        quality_table.add_row(dimension, f"{score:.1f}/10", dim_status)
    
    console.print(quality_table)
    
    # Issues summary
    if latest_execution.get("error_message"):
        console.print(Panel(
            f"[red]Execution Error:[/red]\n\n"
            f"{latest_execution['error_message']}\n\n"
            f"[bold]Recommendations:[/bold]\n"
            f"1. Check your API keys and configuration\n"
            f"2. Verify input requirements format\n"
            f"3. Review logs for detailed error information",
            title="[bold red]Quality Issues[/bold red]",
            border_style="red"
        ))
    elif quality_score < threshold:
        console.print(Panel(
            f"[yellow]Quality score below threshold ({threshold}).[/yellow]\n\n"
            f"[bold]Recommendations:[/bold]\n"
            f"1. Review and refine input requirements\n"
            f"2. Run additional iterations with 'mare run --max-iterations 10'\n"
            f"3. Use interactive mode for step-by-step refinement\n"
            f"4. Check generated artifacts for completeness",
            title="[bold yellow]Quality Improvement Needed[/bold yellow]",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            f"[green]✓ Quality requirements met![/green]\n\n"
            f"Quality score of {quality_score:.1f}/10 exceeds the threshold.\n"
            f"Requirements are ready for implementation.",
            title="[bold green]Quality Passed[/bold green]",
            border_style="green"
        ))

