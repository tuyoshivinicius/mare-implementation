# MARE CLI - Framework de Colaboração Multi-Agente para Engenharia de Requisitos

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-0.1+-green.svg)](https://langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.0.40+-orange.svg)](https://github.com/langchain-ai/langgraph)

Uma poderosa ferramenta de linha de comando que implementa o framework MARE (Multi-Agent Collaboration Framework for Requirements Engineering) para engenharia de requisitos automatizada usando agentes de IA colaborativos.

## 🎯 Visão Geral

O MARE CLI é uma implementação completa do framework de pesquisa apresentado no paper "MARE: Multi-Agents Collaboration Framework for Requirements Engineering" ([arXiv:2405.03256](https://arxiv.org/abs/2405.03256)). Esta ferramenta revoluciona o processo de engenharia de requisitos através da colaboração inteligente entre cinco agentes especializados, cada um com responsabilidades específicas no ciclo de vida dos requisitos.

### 🤖 Os Cinco Agentes MARE

1. **Stakeholder Agent** - Expressa necessidades dos stakeholders e responde perguntas
2. **Collector Agent** - Coleta requisitos através de questionamento sistemático
3. **Modeler Agent** - Extrai entidades e relacionamentos do sistema
4. **Checker Agent** - Verifica qualidade, completude e consistência
5. **Documenter Agent** - Gera especificações finais ou relatórios de problemas

### 🔄 Pipeline de Quatro Fases

O framework MARE opera através de um pipeline estruturado:

1. **Elicitação** - Coleta inicial de requisitos e esclarecimentos
2. **Modelagem** - Extração de entidades e relacionamentos do sistema
3. **Verificação** - Validação de qualidade e consistência dos requisitos
4. **Especificação** - Geração da documentação final (SRS)

## 🚀 Instalação

### Pré-requisitos

- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)
- Chave de API do OpenAI (ou outro provedor LLM suportado)

### Instalação via pip

```bash
# Clone o repositório
git clone https://github.com/your-org/mare-cli.git
cd mare-cli

# Instale as dependências
pip install -e .

# Verifique a instalação
mare --version
```

### Configuração da API

Configure sua chave de API do OpenAI:

```bash
export OPENAI_API_KEY="sua-chave-api-aqui"
```

Ou crie um arquivo `.env` no diretório do projeto:

```env
OPENAI_API_KEY=sua-chave-api-aqui
```

## 🎮 Uso Rápido

### 1. Inicializar um Novo Projeto

```bash
# Criar um novo projeto MARE
mare init meu_projeto --template basic --llm-provider openai

# Navegar para o diretório do projeto
cd meu_projeto
```

### 2. Configurar Entrada

Edite o arquivo `input.md` com a descrição do seu sistema:

```markdown
# Sistema de E-commerce

Precisamos construir uma plataforma de compras online que permita:
- Usuários navegarem e comprarem produtos
- Comerciantes gerenciarem seu inventário
- Processamento seguro de pagamentos
- Rastreamento de pedidos

Público-alvo: Pequenas e médias empresas
Carga esperada: 1000 usuários simultâneos
```

### 3. Executar o Pipeline MARE

```bash
# Executar o pipeline completo
mare run

# Ou executar de forma interativa
mare run --interactive
```

### 4. Verificar Status e Resultados

```bash
# Verificar status do projeto
mare status

# Exportar resultados
mare export markdown
mare export pdf
```

## 📁 Estrutura do Projeto

Após a inicialização, seu projeto terá a seguinte estrutura:

```
meu_projeto/
├── .mare/
│   ├── config.yaml          # Configuração do projeto
│   └── workspace/           # Workspace compartilhado dos agentes
├── input.md                 # Descrição inicial do sistema
├── output/                  # Artefatos gerados
│   ├── user_stories.md
│   ├── questions_and_answers.md
│   ├── requirements_draft.md
│   ├── system_entities.md
│   ├── entity_relationships.md
│   ├── quality_check_report.md
│   └── requirements_specification.md
└── README.md               # Documentação do projeto
```

## ⚙️ Configuração Avançada

### Arquivo de Configuração

O arquivo `.mare/config.yaml` permite personalização completa:

```yaml
project:
  name: "Meu Sistema E-commerce"
  template: "basic"
  domain: "e-commerce"

llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.7

pipeline:
  max_iterations: 5
  quality_threshold: 0.8
  auto_advance: true
  interactive_mode: false

agents:
  stakeholder:
    enabled: true
    model: "gpt-3.5-turbo"
    temperature: 0.7
    max_tokens: 2048
  
  collector:
    enabled: true
    model: "gpt-3.5-turbo"
    temperature: 0.6
    max_tokens: 2048
  
  modeler:
    enabled: true
    model: "gpt-4"
    temperature: 0.5
    max_tokens: 2048
  
  checker:
    enabled: true
    model: "gpt-4"
    temperature: 0.3
    max_tokens: 2048
  
  documenter:
    enabled: true
    model: "gpt-3.5-turbo"
    temperature: 0.4
    max_tokens: 4096
```

### Templates Disponíveis

- **basic** - Template padrão para sistemas gerais
- **web_app** - Otimizado para aplicações web
- **mobile_app** - Focado em aplicações móveis
- **api_service** - Para serviços e APIs
- **enterprise** - Para sistemas empresariais complexos

## 🔧 Comandos da CLI

### `mare init`

Inicializa um novo projeto MARE.

```bash
mare init NOME_PROJETO [OPTIONS]

Opções:
  --template TEXT        Template do projeto (basic, web_app, mobile_app, api_service, enterprise)
  --llm-provider TEXT    Provedor LLM (openai, anthropic, azure)
  --output-dir PATH      Diretório de saída (padrão: diretório atual)
  --interactive          Modo interativo para configuração
```

### `mare run`

Executa o pipeline MARE para processar requisitos.

```bash
mare run [OPTIONS]

Opções:
  --input-file PATH      Arquivo de entrada personalizado
  --interactive          Modo interativo com pausas entre fases
  --max-iterations INT   Número máximo de iterações (padrão: 5)
  --quality-threshold FLOAT  Limiar de qualidade (padrão: 0.8)
  --resume               Retomar execução anterior
```

### `mare status`

Exibe informações de status e progresso do projeto.

```bash
mare status [OPTIONS]

Opções:
  --detailed             Mostrar informações detalhadas
  --workspace            Mostrar estatísticas do workspace
  --history              Mostrar histórico de execuções
```

### `mare export`

Exporta resultados do projeto em formatos específicos.

```bash
mare export FORMAT [OPTIONS]

Formatos:
  markdown              Exportar como arquivos Markdown
  pdf                   Exportar como PDF
  html                  Exportar como HTML
  json                  Exportar dados estruturados
  docx                  Exportar como documento Word

Opções:
  --output-file PATH    Arquivo de saída específico
  --include-artifacts   Incluir todos os artefatos
  --template TEXT       Template de exportação
```

## 🧪 Exemplos de Uso

### Exemplo 1: Sistema de E-commerce

```bash
# Inicializar projeto
mare init ecommerce_system --template web_app

cd ecommerce_system

# Editar input.md com requisitos do e-commerce
# Executar pipeline
mare run

# Verificar resultados
mare status --detailed
mare export pdf --output-file ecommerce_requirements.pdf
```

### Exemplo 2: API de Pagamentos

```bash
# Inicializar projeto para API
mare init payment_api --template api_service

cd payment_api

# Configurar entrada específica para API
echo "# API de Processamento de Pagamentos
Sistema para processar pagamentos seguros com:
- Múltiplos métodos de pagamento
- Validação de transações
- Webhooks para notificações
- Conformidade PCI DSS" > input.md

# Executar com configurações específicas
mare run --max-iterations 3 --quality-threshold 0.9

# Exportar documentação da API
mare export markdown
```

### Exemplo 3: Aplicativo Móvel

```bash
# Projeto para app móvel
mare init fitness_app --template mobile_app

cd fitness_app

# Executar em modo interativo
mare run --interactive

# Acompanhar progresso
mare status --workspace
```

## 📊 Métricas e Qualidade

O MARE CLI fornece métricas detalhadas sobre a qualidade dos requisitos:

### Métricas de Qualidade

- **Completude** - Cobertura de requisitos funcionais e não-funcionais
- **Consistência** - Ausência de contradições entre requisitos
- **Clareza** - Precisão e compreensibilidade dos requisitos
- **Rastreabilidade** - Ligação entre requisitos e necessidades dos stakeholders
- **Verificabilidade** - Capacidade de validar os requisitos

### Relatórios Gerados

1. **Relatório de Qualidade** - Análise detalhada da qualidade dos requisitos
2. **Matriz de Rastreabilidade** - Mapeamento entre necessidades e requisitos
3. **Análise de Consistência** - Identificação de conflitos e ambiguidades
4. **Métricas de Cobertura** - Avaliação da completude dos requisitos

## 🔍 Workspace Colaborativo

O MARE CLI implementa um workspace compartilhado onde os agentes colaboram:

### Artefatos Gerenciados

- **User Stories** - Histórias de usuário iniciais
- **Questions & Answers** - Perguntas e respostas de esclarecimento
- **Requirements Draft** - Rascunhos de requisitos
- **System Entities** - Entidades do sistema identificadas
- **Entity Relationships** - Relacionamentos entre entidades
- **Quality Check Results** - Resultados de verificação de qualidade
- **Final SRS** - Especificação final de requisitos

### Versionamento

Todos os artefatos são versionados automaticamente, permitindo:
- Rastreamento de mudanças
- Rollback para versões anteriores
- Análise de evolução dos requisitos
- Auditoria completa do processo

## 🧪 Testes e Validação

O projeto inclui uma suíte abrangente de testes:

```bash
# Executar todos os testes
python run_tests.py --all

# Executar apenas testes unitários
python run_tests.py --unit

# Executar testes de integração
python run_tests.py --integration

# Executar testes de performance
python run_tests.py --performance

# Gerar relatório de cobertura
python run_tests.py --coverage
```

### Tipos de Teste

- **Testes Unitários** - Validação de componentes individuais
- **Testes de Integração** - Validação de interações entre componentes
- **Testes End-to-End** - Validação de fluxos completos
- **Testes de Performance** - Validação de desempenho e escalabilidade

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, siga estas diretrizes:

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

### Desenvolvimento Local

```bash
# Clone o repositório
git clone https://github.com/your-org/mare-cli.git
cd mare-cli

# Instale em modo desenvolvimento
pip install -e .

# Instale dependências de desenvolvimento
pip install -r requirements-dev.txt

# Execute os testes
python run_tests.py --all
```

## 📚 Documentação Adicional

- [Guia de Arquitetura](docs/architecture.md)
- [Referência da API](docs/api_reference.md)
- [Exemplos Avançados](docs/examples/)
- [Troubleshooting](docs/troubleshooting.md)
- [FAQ](docs/faq.md)

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- Baseado no paper de pesquisa "MARE: Multi-Agents Collaboration Framework for Requirements Engineering"
- Construído com [LangChain](https://langchain.com/) e [LangGraph](https://github.com/langchain-ai/langgraph)
- Inspirado pela comunidade de engenharia de requisitos

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/your-org/mare-cli/issues)
- **Discussões**: [GitHub Discussions](https://github.com/your-org/mare-cli/discussions)
- **Email**: support@mare-cli.org

---

**MARE CLI** - Revolucionando a Engenharia de Requisitos com IA Colaborativa 🚀

