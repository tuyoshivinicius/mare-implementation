#!/usr/bin/env python3
"""
MARE CLI - Framework de Colaboração Multi-Agente para Engenharia de Requisitos
Ponto de entrada principal da CLI e despachador de comandos
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

# Inicializa console rich para saída bonita
console = Console()

# Arte ASCII para MARE CLI
MARE_LOGO = """
███╗   ███╗ █████╗ ██████╗ ███████╗
████╗ ████║██╔══██╗██╔══██╗██╔════╝
██╔████╔██║███████║██████╔╝█████╗  
██║╚██╔╝██║██╔══██║██╔══██╗██╔══╝  
██║ ╚═╝ ██║██║  ██║██║  ██║███████╗
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
Engenharia de Requisitos Multi-Agente
"""

@click.group()
@click.version_option(version="1.0.0", prog_name="MARE CLI")
@click.option(
    "--verbose", "-v", 
    is_flag=True, 
    help="Habilita saída detalhada"
)
@click.option(
    "--debug", 
    is_flag=True, 
    help="Habilita modo de depuração"
)
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="Caminho para arquivo de configuração"
)
@click.pass_context
def cli(ctx, verbose, debug, config):
    """
    MARE CLI - Framework de Colaboração Multi-Agente para Engenharia de Requisitos
    
    Uma ferramenta CLI poderosa que implementa o framework MARE para engenharia
    de requisitos automatizada usando agentes de IA colaborativos.
    
    Baseado no artigo: "MARE: Multi-Agents Collaboration Framework for 
    Requirements Engineering" (https://arxiv.org/abs/2405.03256)
    """
    # Garante que o objeto de contexto existe
    ctx.ensure_object(dict)
    
    # Armazena opções globais no contexto
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug
    ctx.obj['config'] = config
    
    # Configura logging
    log_level = logging.DEBUG if debug else (logging.INFO if verbose else logging.WARNING)
    setup_logging(log_level)
    
    # Exibe logo no modo debug
    if debug:
        console.print(Panel(
            Text(MARE_LOGO, style="bold blue"),
            title="[bold green]MARE CLI v1.0.0[/bold green]",
            subtitle="[italic]Engenharia de Requisitos Multi-Agente[/italic]"
        ))

@cli.command()
@click.argument('project_name', required=False)
@click.option(
    '--template', '-t',
    type=click.Choice(['basic', 'web_app', 'mobile_app', 'enterprise']),
    default='basic',
    help='Template de projeto a ser usado'
)
@click.option(
    '--llm-provider',
    type=click.Choice(['openai', 'anthropic', 'local']),
    default='openai',
    help='Provedor de LLM a ser configurado'
)
@click.option(
    '--force', '-f',
    is_flag=True,
    help='Força inicialização mesmo se o diretório existir'
)
@click.pass_context
def init(ctx, project_name, template, llm_provider, force):
    """
    Inicializa um novo projeto MARE com a configuração especificada.
    
    Cria estrutura do projeto, arquivos de configuração e configuração do workspace.
    
    Exemplos:
        mare init meu_projeto
        mare init meu_projeto --template web_app --llm-provider openai
    """
    try:
        init_command(ctx, project_name, template, llm_provider, force)
    except MAREException as e:
        console.print(f"[red]Erro:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Erro inesperado:[/red] {e}")
        if ctx.obj.get('debug'):
            raise
        sys.exit(1)

@cli.command()
@click.option(
    '--phase', '-p',
    type=click.Choice(['elicitation', 'modeling', 'verification', 'specification']),
    help='Executa apenas uma fase específica'
)
@click.option(
    '--interactive', '-i',
    is_flag=True,
    help='Executa em modo interativo com execução passo a passo'
)
@click.option(
    '--input-file', '-f',
    type=click.Path(exists=True),
    help='Arquivo de entrada com requisitos iniciais'
)
@click.option(
    '--max-iterations',
    type=int,
    default=5,
    help='Número máximo de iterações de refinamento'
)
@click.pass_context
def run(ctx, phase, interactive, input_file, max_iterations):
    """
    Executa o pipeline MARE para processar requisitos.
    
    Executa o processo completo de colaboração multi-agente ou fases específicas
    para transformar requisitos iniciais em especificações estruturadas.
    
    Exemplos:
        mare run
        mare run --phase elicitation --interactive
        mare run --input-file requisitos.txt --max-iterations 3
    """
    try:
        run_command(ctx, phase, interactive, input_file, max_iterations)
    except MAREException as e:
        console.print(f"[red]Erro:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Erro inesperado:[/red] {e}")
        if ctx.obj.get('debug'):
            raise
        sys.exit(1)

@cli.command()
@click.option(
    '--detailed', '-d',
    is_flag=True,
    help='Mostra informações detalhadas de status'
)
@click.option(
    '--artifacts', '-a',
    is_flag=True,
    help='Lista todos os artefatos no workspace'
)
@click.option(
    '--quality', '-q',
    is_flag=True,
    help='Mostra métricas de qualidade e análise'
)
@click.pass_context
def status(ctx, detailed, artifacts, quality):
    """
    Exibe status atual do projeto e informações de progresso.
    
    Mostra estado do pipeline, status dos artefatos, métricas de qualidade e histórico de execução.
    
    Exemplos:
        mare status
        mare status --detailed --quality
        mare status --artifacts
    """
    try:
        status_command(ctx, detailed, artifacts, quality)
    except MAREException as e:
        console.print(f"[red]Erro:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Erro inesperado:[/red] {e}")
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
    help='Caminho do arquivo de saída'
)
@click.option(
    '--template',
    type=click.Path(exists=True),
    help='Arquivo de template personalizado para formatação'
)
@click.option(
    '--include-metadata',
    is_flag=True,
    help='Inclui metadados e informações de rastreabilidade'
)
@click.option(
    '--quality-report',
    is_flag=True,
    help='Inclui relatório de análise de qualidade'
)
@click.pass_context
def export(ctx, format, output, template, include_metadata, quality_report):
    """
    Exporta resultados do projeto no formato especificado.
    
    Gera documentação final, especificações ou relatórios a partir dos
    requisitos processados e artefatos.
    
    Exemplos:
        mare export json
        mare export markdown --output requisitos.md
        mare export pdf --template template_personalizado.html --include-metadata
    """
    try:
        export_command(ctx, format, output, template, include_metadata, quality_report)
    except MAREException as e:
        console.print(f"[red]Erro:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Erro inesperado:[/red] {e}")
        if ctx.obj.get('debug'):
            raise
        sys.exit(1)

def main():
    """Ponto de entrada principal para a aplicação MARE CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[yellow]Operação cancelada pelo usuário[/yellow]")
        sys.exit(130)
    except Exception as e:
        console.print(f"[red]Erro fatal:[/red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

