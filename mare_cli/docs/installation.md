# Guia de Instalação e Configuração - MARE CLI

Este guia fornece instruções detalhadas para instalação, configuração e primeiros passos com o MARE CLI.

## 📋 Requisitos do Sistema

### Requisitos Mínimos

- **Sistema Operacional**: Linux, macOS, ou Windows 10/11
- **Python**: Versão 3.11 ou superior
- **Memória RAM**: Mínimo 4GB, recomendado 8GB
- **Espaço em Disco**: Mínimo 2GB livres
- **Conexão com Internet**: Necessária para APIs de LLM

### Requisitos Recomendados

- **Python**: Versão 3.11 ou 3.12
- **Memória RAM**: 16GB ou superior
- **Processador**: Multi-core (4+ cores)
- **SSD**: Para melhor performance do workspace

## 🔧 Instalação Passo a Passo

### 1. Preparação do Ambiente

#### Linux/macOS

```bash
# Atualizar sistema (Ubuntu/Debian)
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.11+ se necessário
sudo apt install python3.11 python3.11-pip python3.11-venv

# Verificar versão do Python
python3.11 --version
```

#### Windows

1. Baixe Python 3.11+ do [site oficial](https://www.python.org/downloads/)
2. Execute o instalador e marque "Add Python to PATH"
3. Abra o Command Prompt ou PowerShell
4. Verifique a instalação: `python --version`

### 2. Criação do Ambiente Virtual

```bash
# Criar ambiente virtual
python3.11 -m venv mare_env

# Ativar ambiente virtual
# Linux/macOS:
source mare_env/bin/activate

# Windows:
mare_env\Scripts\activate

# Verificar ativação (deve mostrar (mare_env))
which python
```

### 3. Instalação do MARE CLI

#### Opção A: Instalação via Git (Recomendada)

```bash
# Clone o repositório
git clone https://github.com/your-org/mare-cli.git
cd mare-cli

# Instalar em modo desenvolvimento
pip install -e .

# Verificar instalação
mare --version
```

#### Opção B: Instalação via pip (Quando disponível)

```bash
# Instalar diretamente via pip
pip install mare-cli

# Verificar instalação
mare --version
```

### 4. Configuração de Dependências

```bash
# Instalar dependências adicionais (se necessário)
pip install --upgrade pip
pip install -r requirements.txt

# Para desenvolvimento (opcional)
pip install -r requirements-dev.txt
```

## 🔑 Configuração de APIs

### OpenAI (Recomendado)

1. **Obter Chave de API**:
   - Acesse [OpenAI Platform](https://platform.openai.com/)
   - Crie uma conta ou faça login
   - Navegue para "API Keys"
   - Clique em "Create new secret key"
   - Copie a chave gerada

2. **Configurar Chave**:

```bash
# Opção 1: Variável de ambiente (temporária)
export OPENAI_API_KEY="sk-sua-chave-aqui"

# Opção 2: Arquivo .env (permanente)
echo "OPENAI_API_KEY=sk-sua-chave-aqui" > ~/.mare_env

# Opção 3: Configuração global
mare config set openai.api_key "sk-sua-chave-aqui"
```

### Outros Provedores

#### Anthropic Claude

```bash
# Configurar Claude
export ANTHROPIC_API_KEY="sua-chave-anthropic"
mare config set llm.provider anthropic
```

#### Azure OpenAI

```bash
# Configurar Azure OpenAI
export AZURE_OPENAI_API_KEY="sua-chave-azure"
export AZURE_OPENAI_ENDPOINT="https://seu-recurso.openai.azure.com/"
mare config set llm.provider azure
```

## 🎯 Primeiro Projeto

### 1. Criar Projeto de Teste

```bash
# Criar diretório de trabalho
mkdir ~/mare_projects
cd ~/mare_projects

# Inicializar primeiro projeto
mare init meu_primeiro_projeto --template basic --llm-provider openai

# Navegar para o projeto
cd meu_primeiro_projeto
```

### 2. Configurar Entrada

Edite o arquivo `input.md`:

```markdown
# Sistema de Gerenciamento de Biblioteca

Precisamos desenvolver um sistema para gerenciar uma biblioteca que permita:

## Funcionalidades Principais
- Cadastro e busca de livros
- Controle de empréstimos e devoluções
- Gestão de usuários (bibliotecários e leitores)
- Relatórios de uso e estatísticas

## Requisitos Técnicos
- Interface web responsiva
- Base de dados para persistência
- Sistema de autenticação
- Notificações por email

## Contexto
- Biblioteca universitária com 50.000 livros
- 5.000 usuários ativos
- 10 bibliotecários
- Operação 12 horas por dia
```

### 3. Executar Pipeline

```bash
# Executar pipeline completo
mare run

# Ou executar em modo interativo (recomendado para primeiro uso)
mare run --interactive
```

### 4. Verificar Resultados

```bash
# Verificar status
mare status --detailed

# Listar arquivos gerados
ls -la output/

# Visualizar especificação final
cat output/requirements_specification.md
```

## ⚙️ Configuração Avançada

### Arquivo de Configuração Global

Crie `~/.mare/config.yaml`:

```yaml
# Configuração global do MARE CLI
default:
  llm:
    provider: "openai"
    model: "gpt-4"
    temperature: 0.7
    max_tokens: 2048
  
  pipeline:
    max_iterations: 5
    quality_threshold: 0.8
    auto_advance: true
  
  workspace:
    storage_backend: "sqlite"
    enable_versioning: true
    cleanup_days: 30

# Perfis específicos
profiles:
  development:
    llm:
      model: "gpt-3.5-turbo"
      temperature: 0.5
    pipeline:
      max_iterations: 3
  
  production:
    llm:
      model: "gpt-4"
      temperature: 0.3
    pipeline:
      max_iterations: 10
      quality_threshold: 0.9
```

### Configuração por Projeto

Cada projeto pode ter configurações específicas em `.mare/config.yaml`:

```yaml
project:
  name: "Sistema de Biblioteca"
  description: "Sistema de gerenciamento de biblioteca universitária"
  domain: "education"
  template: "web_app"

llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.7

pipeline:
  max_iterations: 7
  quality_threshold: 0.85
  auto_advance: false  # Pausar entre fases
  interactive_mode: true

agents:
  stakeholder:
    enabled: true
    model: "gpt-3.5-turbo"
    temperature: 0.8
    system_prompt: |
      Você é um stakeholder experiente em sistemas educacionais.
      Foque em requisitos práticos e usabilidade.
  
  collector:
    enabled: true
    model: "gpt-4"
    temperature: 0.6
    max_questions: 15
  
  modeler:
    enabled: true
    model: "gpt-4"
    temperature: 0.4
    focus_areas: ["data_model", "user_interactions", "business_logic"]
  
  checker:
    enabled: true
    model: "gpt-4"
    temperature: 0.2
    quality_criteria: ["completeness", "consistency", "feasibility", "testability"]
  
  documenter:
    enabled: true
    model: "gpt-4"
    temperature: 0.3
    output_format: "ieee_830"
    include_diagrams: true
```

## 🔧 Comandos de Configuração

### Gerenciamento de Configuração

```bash
# Listar configurações atuais
mare config list

# Definir configuração específica
mare config set llm.model "gpt-4"
mare config set pipeline.max_iterations 10

# Obter valor de configuração
mare config get llm.provider

# Resetar configuração para padrão
mare config reset llm.temperature

# Usar perfil específico
mare config profile development
```

### Gerenciamento de Templates

```bash
# Listar templates disponíveis
mare template list

# Criar template personalizado
mare template create meu_template --base basic

# Editar template
mare template edit meu_template

# Usar template personalizado
mare init novo_projeto --template meu_template
```

## 🐛 Solução de Problemas

### Problemas Comuns

#### 1. Erro de Chave de API

```
Error: The api_key client option must be set
```

**Solução**:
```bash
# Verificar se a chave está definida
echo $OPENAI_API_KEY

# Redefinir a chave
export OPENAI_API_KEY="sua-chave-correta"

# Ou usar arquivo .env
echo "OPENAI_API_KEY=sua-chave" > .env
```

#### 2. Erro de Dependências

```
ImportError: No module named 'langchain'
```

**Solução**:
```bash
# Reinstalar dependências
pip install --upgrade -r requirements.txt

# Ou reinstalar o MARE CLI
pip install -e . --force-reinstall
```

#### 3. Erro de Permissões

```
PermissionError: [Errno 13] Permission denied
```

**Solução**:
```bash
# Verificar permissões do diretório
ls -la

# Corrigir permissões
chmod 755 .
chmod -R 644 .mare/

# Ou usar diretório do usuário
cd ~/mare_projects
```

#### 4. Timeout de API

```
TimeoutError: Request timed out
```

**Solução**:
```bash
# Aumentar timeout na configuração
mare config set llm.timeout 120

# Ou usar modelo mais rápido
mare config set llm.model "gpt-3.5-turbo"
```

### Logs e Debugging

```bash
# Executar com logs detalhados
mare run --verbose --debug

# Verificar logs do sistema
tail -f ~/.mare/logs/mare.log

# Limpar cache e workspace
mare workspace clean
mare cache clear
```

### Verificação da Instalação

```bash
# Script de verificação completa
mare doctor

# Teste de conectividade com API
mare test api

# Teste de funcionalidade básica
mare test basic
```

## 📊 Monitoramento e Performance

### Métricas de Performance

```bash
# Verificar estatísticas de uso
mare stats

# Monitorar uso de API
mare api usage

# Verificar performance do workspace
mare workspace stats
```

### Otimização

```yaml
# Configurações para melhor performance
performance:
  cache:
    enabled: true
    ttl: 3600  # 1 hora
  
  parallel_processing:
    enabled: true
    max_workers: 4
  
  workspace:
    batch_size: 100
    compression: true
```

## 🔄 Atualizações

### Atualizar MARE CLI

```bash
# Verificar versão atual
mare --version

# Verificar atualizações disponíveis
mare update check

# Atualizar para versão mais recente
mare update install

# Ou atualizar via git
cd mare-cli
git pull origin main
pip install -e . --upgrade
```

### Migração de Projetos

```bash
# Migrar projeto para nova versão
mare migrate project ./meu_projeto

# Backup antes da migração
mare backup create ./meu_projeto

# Restaurar backup se necessário
mare backup restore ./meu_projeto_backup.tar.gz
```

## 🆘 Suporte

### Recursos de Ajuda

```bash
# Ajuda geral
mare --help

# Ajuda para comando específico
mare run --help

# Documentação interativa
mare docs

# Exemplos práticos
mare examples
```

### Comunidade e Suporte

- **Documentação**: [docs.mare-cli.org](https://docs.mare-cli.org)
- **Issues**: [GitHub Issues](https://github.com/your-org/mare-cli/issues)
- **Discussões**: [GitHub Discussions](https://github.com/your-org/mare-cli/discussions)
- **Discord**: [Servidor da Comunidade](https://discord.gg/mare-cli)
- **Email**: support@mare-cli.org

---

Este guia deve cobrir a maioria dos cenários de instalação e configuração. Para casos específicos ou problemas não cobertos aqui, consulte a documentação completa ou entre em contato com o suporte.

