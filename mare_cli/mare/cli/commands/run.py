"""
MARE CLI - Implementação do comando run
Gerencia execução e orquestração do pipeline com transparência aprimorada
"""

from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mare.pipeline import PipelineExecutor
from mare.utils.exceptions import PipelineExecutionError
from mare.utils.helpers import find_project_root, validate_project_structure
from mare.utils.logging import get_logger
from mare.utils.progress import start_progress_tracking, stop_progress_tracking, get_progress_tracker

console = Console()
logger = get_logger(__name__)

def run_command(
    ctx: click.Context,
    phase: Optional[str],
    interactive: bool,
    input_file: Optional[str],
    max_iterations: int,
    timeout: int = 300,
    verbose: bool = False
) -> None:
    """
    Executa o pipeline MARE com transparência aprimorada.
    
    Args:
        ctx: Objeto de contexto do Click
        phase: Fase específica para executar
        interactive: Executa em modo interativo
        input_file: Arquivo de entrada com requisitos
        max_iterations: Número máximo de iterações
        timeout: Timeout de execução em segundos
        verbose: Habilita logging detalhado
    """
    logger.info("Iniciando execução do pipeline")
    
    # Encontra raiz do projeto
    project_root = find_project_root()
    if not project_root:
        raise PipelineExecutionError(
            "Nenhum projeto MARE encontrado. Execute 'mare init' para criar um novo projeto."
        )
    
    # Valida estrutura do projeto
    if not validate_project_structure(project_root):
        raise PipelineExecutionError(
            "Estrutura de projeto inválida. Verifique a configuração do seu projeto."
        )
    
    # Inicia rastreamento de progresso aprimorado
    tracker = start_progress_tracking()
    
    try:
        # Inicializa executor do pipeline
        console.print(Panel(
            f"[blue]Inicializando Pipeline MARE[/blue]\n\n"
            f"[bold]Projeto:[/bold] {project_root.name}\n"
            f"[bold]Fase:[/bold] {phase or 'todas'}\n"
            f"[bold]Interativo:[/bold] {interactive}\n"
            f"[bold]Arquivo de entrada:[/bold] {input_file or 'padrão'}\n"
            f"[bold]Máx iterações:[/bold] {max_iterations}\n"
            f"[bold]Timeout:[/bold] {timeout}s\n"
            f"[bold]Detalhado:[/bold] {verbose}",
            title="[bold blue]Execução do Pipeline MARE[/bold blue]",
            border_style="blue"
        ))
        
        # Inicia fase de inicialização
        tracker.start_phase("initialization", "Criando executor do pipeline")
        
        executor = PipelineExecutor(project_root)
        tracker.update_phase_progress("initialization", 50, "Validando configuração")
        
        # Prepara caminho do arquivo de entrada
        input_path = None
        if input_file:
            input_path = Path(input_file)
            if not input_path.is_absolute():
                input_path = project_root / input_path
        
        tracker.update_phase_progress("initialization", 100, "Pronto para executar")
        tracker.complete_phase("initialization")
        
        # Executa o pipeline com rastreamento aprimorado
        result = executor.execute_pipeline(
            input_file=input_path,
            interactive=interactive,
            max_iterations=max_iterations,
            timeout=timeout,
            progress_tracker=tracker,
            verbose=verbose
        )
        
        # Exibe resultados
        _display_execution_results(result)
        
        logger.info("Execução do pipeline concluída com sucesso")
        
    except Exception as e:
        logger.error(f"Execução do pipeline falhou: {e}")
        
        # Marca fase atual como falhada
        if tracker.current_phase:
            tracker.fail_phase(tracker.current_phase, str(e))
        
        console.print(Panel(
            f"[red]Execução do pipeline falhou:[/red]\n\n"
            f"[bold]Erro:[/bold] {str(e)}\n\n"
            f"[dim]Verifique os logs para mais detalhes.[/dim]",
            title="[bold red]Execução Falhou[/bold red]",
            border_style="red"
        ))
        raise PipelineExecutionError(f"Execução do pipeline falhou: {e}")
    
    finally:
        # Para rastreamento de progresso
        stop_progress_tracking()
        
    # Return result for testing
    return result if 'result' in locals() else {"status": "completed"}

def _display_execution_results(result: dict) -> None:
    """Exibe resultados da execução do pipeline."""
    
    # Painel de status
    status_color = "green" if result["status"] == "completed" else "red"
    console.print(Panel(
        f"[{status_color}]Status do Pipeline: {result['status'].upper()}[/{status_color}]\n\n"
        f"[bold]ID da Execução:[/bold] {result['execution_id'][:8]}...\n"
        f"[bold]Pontuação de Qualidade:[/bold] {result['quality_score']:.1f}/10\n"
        f"[bold]Iterações:[/bold] {result['iterations']}\n"
        f"[bold]Problemas Encontrados:[/bold] {len(result.get('issues_found', []))}",
        title="[bold]Resumo da Execução[/bold]",
        border_style=status_color
    ))
    
    # Resumo de artefatos
    artifacts = result.get("artifacts", {})
    artifacts_table = Table(title="Artefatos Gerados")
    artifacts_table.add_column("Artefato", style="cyan", no_wrap=True)
    artifacts_table.add_column("Status", style="magenta")
    artifacts_table.add_column("Tamanho", style="green")
    
    artifact_info = [
        ("User Stories", artifacts.get("user_stories", "")),
        ("Rascunho de Requisitos", artifacts.get("requirements", "")),
        ("Entidades do Sistema", artifacts.get("entities", "")),
        ("Relacionamentos de Entidades", artifacts.get("relationships", "")),
        ("Resultados de Verificação de Qualidade", artifacts.get("check_results", "")),
        ("Documento SRS Final", artifacts.get("final_srs", ""))
    ]
    
    for name, content in artifact_info:
        if content:
            status = "[green]✓ Gerado[/green]"
            size = f"{len(content)} chars"
        else:
            status = "[red]✗ Ausente[/red]"
            size = "0 chars"
        
        artifacts_table.add_row(name, status, size)
    
    console.print(artifacts_table)
    
    # Resumo de problemas se houver
    if result.get("issues_found"):
        console.print(Panel(
            f"[yellow]Problemas de qualidade foram encontrados durante a verificação.[/yellow]\n\n"
            f"Execute 'mare status --quality' para análise detalhada.",
            title="[bold yellow]Problemas de Qualidade[/bold yellow]",
            border_style="yellow"
        ))
    
    # Mensagem de sucesso
    if result["status"] == "completed":
        console.print(Panel(
            f"[green]✓ Execução do pipeline concluída com sucesso![/green]\n\n"
            f"[bold]Próximos passos:[/bold]\n"
            f"1. Revisar artefatos gerados: 'mare status --artifacts'\n"
            f"2. Exportar especificação final: 'mare export markdown'\n"
            f"3. Verificar métricas de qualidade: 'mare status --quality'\n\n"
            f"[dim]SRS final salvo em: output/requirements_specification.md[/dim]",
            title="[bold green]Execução Concluída[/bold green]",
            border_style="green"
        ))
    else:
        error_msg = result.get("error_message", "Erro desconhecido")
        console.print(Panel(
            f"[red]Execução do pipeline falhou.[/red]\n\n"
            f"[bold]Erro:[/bold] {error_msg}\n\n"
            f"[bold]Solução de problemas:[/bold]\n"
            f"1. Verifique suas chaves de API no arquivo .env\n"
            f"2. Verifique requisitos de entrada em input/requirements.md\n"
            f"3. Revise logs para informações detalhadas do erro\n"
            f"4. Tente executar com flag --interactive para execução passo a passo",
            title="[bold red]Execução Falhou[/bold red]",
            border_style="red"
        ))

