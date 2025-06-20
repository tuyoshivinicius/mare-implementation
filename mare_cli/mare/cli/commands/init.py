"""
MARE CLI - Implementação do comando init
Gerencia inicialização e configuração de projetos
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
    Inicializa um novo projeto MARE.
    
    Args:
        ctx: Objeto de contexto do Click
        project_name: Nome do projeto a ser criado
        template: Template de projeto a ser usado
        llm_provider: Provedor de LLM a ser configurado
        force: Força inicialização mesmo se o diretório existir
    """
    logger.info("Iniciando inicialização do projeto")
    
    # Determina nome e caminho do projeto
    if project_name is None:
        project_name = click.prompt("Digite o nome do projeto")
    
    project_path = Path.cwd() / project_name
    
    # Verifica se o projeto já existe
    if project_path.exists() and not force:
        if not click.confirm(f"Diretório '{project_name}' já existe. Continuar?"):
            raise ProjectInitializationError(
                "Inicialização do projeto cancelada pelo usuário",
                str(project_path)
            )
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            
            # Cria estrutura do projeto
            task1 = progress.add_task("Criando estrutura do projeto...", total=None)
            _create_project_structure(project_path)
            progress.update(task1, completed=True)
            
            # Gera configuração
            task2 = progress.add_task("Gerando configuração...", total=None)
            _create_project_config(project_path, template, llm_provider)
            progress.update(task2, completed=True)
            
            # Inicializa workspace
            task3 = progress.add_task("Inicializando workspace...", total=None)
            _initialize_workspace(project_path)
            progress.update(task3, completed=True)
            
            # Cria arquivos de exemplo
            task4 = progress.add_task("Criando arquivos de exemplo...", total=None)
            _create_example_files(project_path, template, llm_provider)
            progress.update(task4, completed=True)
        
        # Mensagem de sucesso
        console.print(Panel(
            f"[green]✓[/green] Projeto '{project_name}' inicializado com sucesso!\n\n"
            f"[bold]Próximos passos:[/bold]\n"
            f"1. cd {project_name}\n"
            f"2. Configure suas chaves de API LLM em .mare/config.yaml\n"
            f"3. Execute 'mare run' para começar a processar requisitos\n\n"
            f"[dim]Template: {template} | Provedor LLM: {llm_provider}[/dim]",
            title="[bold green]Projeto Inicializado[/bold green]",
            border_style="green"
        ))
        
        logger.info(f"Projeto '{project_name}' inicializado com sucesso em {project_path}")
        return True
        
    except Exception as e:
        logger.error(f"Falha ao inicializar projeto: {e}")
        raise ProjectInitializationError(
            f"Falha ao inicializar projeto: {e}",
            str(project_path)
        )

def _create_project_structure(project_path: Path) -> None:
    """Cria a estrutura básica de diretórios do projeto."""
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
    """Cria arquivos de configuração do projeto."""
    
    # Configuração principal
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
            "stakeholder": {"enabled": True, "model": "gpt-3.5-turbo"},
            "collector": {"enabled": True, "model": "gpt-3.5-turbo"},
            "modeler": {"enabled": True, "model": "gpt-4"},
            "checker": {"enabled": True, "model": "gpt-4"},
            "documenter": {"enabled": True, "model": "gpt-3.5-turbo"}
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
    
    # Template de ambiente
    env_template = f"""# Configuração de Ambiente MARE CLI
# Copie este arquivo para .env e preencha suas chaves de API

# Configuração do Provedor LLM
MARE_LLM_PROVIDER={llm_provider}

# Configuração OpenAI (se usando OpenAI)
OPENAI_API_KEY=sua_chave_api_openai_aqui

# Configuração Anthropic (se usando Anthropic)
ANTHROPIC_API_KEY=sua_chave_api_anthropic_aqui

# Configuração LLM Local (se usando modelos locais)
LOCAL_LLM_ENDPOINT=http://localhost:8000

# Configuração de Logging
MARE_LOG_LEVEL=INFO
MARE_LOG_FILE=.mare/logs/mare.log

# Configuração do Workspace
MARE_WORKSPACE_PATH=.mare/workspace
"""
    
    with open(project_path / ".env.template", "w") as f:
        f.write(env_template)

def _get_default_models(provider: str) -> dict:
    """Obtém configuração padrão de modelos para o provedor."""
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
    """Obtém parâmetros padrão do LLM."""
    return {
        "temperature": 0.7,
        "max_tokens": 2048,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }

def _initialize_workspace(project_path: Path) -> None:
    """Inicializa o banco de dados e estrutura do workspace."""
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
    """Cria arquivos de exemplo de entrada baseados no template."""
    
    examples = {
        "basic": """# Exemplo de Entrada de Requisitos

## Visão Geral do Sistema
Quero desenvolver um sistema simples de gerenciamento de tarefas.

## User Stories
- Como usuário, quero criar tarefas para que eu possa acompanhar meu trabalho
- Como usuário, quero marcar tarefas como concluídas para que eu possa ver meu progresso
- Como usuário, quero deletar tarefas para que eu possa remover itens desnecessários
""",
        "web_app": """# Requisitos de Aplicação Web

## Visão Geral do Sistema
Quero desenvolver uma plataforma de e-commerce baseada na web para vender livros online.

## User Stories
- Como cliente, quero navegar livros por categoria para que eu possa encontrar o que estou procurando
- Como cliente, quero adicionar livros ao meu carrinho para que eu possa comprar múltiplos itens
- Como cliente, quero criar uma conta para que eu possa acompanhar meus pedidos
- Como admin, quero gerenciar inventário para que eu possa controlar os níveis de estoque
""",
        "mobile_app": """# Requisitos de Aplicação Mobile

## Visão Geral do Sistema
Quero desenvolver um aplicativo móvel de acompanhamento de fitness.

## User Stories
- Como usuário, quero registrar meus treinos para que eu possa acompanhar meu progresso fitness
- Como usuário, quero definir metas de fitness para que eu possa me manter motivado
- Como usuário, quero visualizar gráficos de progresso para que eu possa ver minha melhoria ao longo do tempo
- Como usuário, quero compartilhar minhas conquistas para que eu possa motivar outros
""",
        "enterprise": """# Requisitos de Sistema Empresarial

## Visão Geral do Sistema
Quero desenvolver um sistema de planejamento de recursos empresariais (ERP) para empresas de manufatura.

## User Stories
- Como gerente, quero acompanhar cronogramas de produção para que eu possa garantir entrega pontual
- Como funcionário, quero registrar horas de trabalho para que a folha de pagamento possa ser processada com precisão
- Como supervisor, quero monitorar métricas de qualidade para que eu possa manter padrões
- Como administrador, quero gerar relatórios para que eu possa analisar performance do negócio
"""
    }
    
    example_content = examples.get(template, examples["basic"])
    
    with open(project_path / "input" / "requirements.md", "w") as f:
        f.write(example_content)
    
    # Cria README
    readme_content = f"""# {project_path.name}

Projeto MARE CLI para engenharia de requisitos automatizada.

## Começando

1. Configure suas chaves de API LLM em `.env` (copie de `.env.template`)
2. Edite `input/requirements.md` com seus requisitos reais
3. Execute o pipeline: `mare run`
4. Verifique status: `mare status`
5. Exporte resultados: `mare export markdown`

## Estrutura do Projeto

- `input/` - Requisitos de entrada e user stories
- `output/` - Especificações e relatórios gerados
- `.mare/` - Configuração e workspace do MARE CLI
- `templates/` - Templates personalizados para formatação de saída

## Template: {template}
## Provedor LLM: {llm_provider}

Para mais informações, visite: https://github.com/manus-ai/mare-cli
"""
    
    with open(project_path / "README.md", "w") as f:
        f.write(readme_content)

