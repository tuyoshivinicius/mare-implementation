# Análise Detalhada do Framework MARE
## Multi-Agent Collaboration Framework for Requirements Engineering

---

## 📚 Contexto e Desafios da Engenharia de Requisitos

A Engenharia de Requisitos (RE) é uma das fases mais críticas no processo de desenvolvimento de software, responsável por gerar especificações de requisitos a partir das necessidades dos stakeholders. Recentemente, técnicas de deep learning têm sido aplicadas com sucesso em várias tarefas de RE. No entanto, obter especificações de requisitos de alta qualidade requer colaboração entre múltiplas tarefas e papéis.

### Principais Desafios Abordados:

**Complexidade Multi-tarefa**: O processo de RE tradicionalmente envolve múltiplas tarefas como elicitação, análise, especificação e verificação das necessidades e expectativas dos stakeholders para um sistema de software.

**Colaboração Limitada**: As abordagens existentes focam principalmente na automação de poucas tarefas, limitando o aumento da efetividade e eficiência do processo completo.

**Qualidade dos Artefatos**: A necessidade de gerar artefatos de requisitos que atendam aos padrões de qualidade em termos de correção, completude e consistência.

**Automação End-to-End**: A falta de frameworks que automatizem todo o processo de RE de forma integrada e colaborativa.

---

## 🤖 Estrutura dos 5 Agentes Essenciais

O framework MARE é baseado em cinco agentes especializados que colaboram para executar o processo completo de Engenharia de Requisitos:

### 1. **Stakeholder Agent (Alice)**
- **Perfil**: Stakeholder experiente em requisitos
- **Objetivo**: Expressar e detalhar as necessidades dos stakeholders para o sistema a ser desenvolvido
- **Ações Principais**: 
  - SpeakUserStories: Expressa histórias de usuário baseadas em ideias iniciais
  - AnswerQuestion: Responde perguntas dos outros agentes

### 2. **Collector Agent (Bob)**
- **Perfil**: Coletor experiente de requisitos
- **Objetivo**: Entrevistar stakeholders para coletar suas necessidades
- **Ações Principais**:
  - ProposeQuestion: Propõe perguntas para refinar requisitos
  - WriteReqDraft: Escreve rascunhos de requisitos baseados nas histórias dos usuários

### 3. **Modeler Agent (Carol)**
- **Perfil**: Modelador experiente de requisitos
- **Objetivo**: Extrair modelo de requisitos, incluindo entidades e relacionamentos
- **Ações Principais**:
  - ExtractEntity: Extrai entidades dos requisitos
  - ExtractRelation: Extrai relacionamentos entre entidades

### 4. **Checker Agent (Dave)**
- **Perfil**: Verificador experiente de requisitos
- **Objetivo**: Verificar a qualidade dos requisitos baseado no modelo de requisitos
- **Ações Principais**:
  - CheckRequirement: Verifica qualidade e consistência dos requisitos

### 5. **Documenter Agent (Eve)**
- **Perfil**: Documentador experiente de requisitos
- **Objetivo**: Escrever especificação de requisitos ou relatório de verificação
- **Ações Principais**:
  - WriteSRS: Escreve especificação de requisitos de software
  - WriteCheckReport: Escreve relatórios de verificação

---



## ⚡ As 9 Ações Específicas do Framework

O framework MARE define nove ações específicas que são executadas pelos agentes durante o processo de RE:

### Ações de Elicitação:
1. **SpeakUserStories**: Stakeholder expressa histórias de usuário baseadas em ideias iniciais do sistema
2. **ProposeQuestion**: Collector propõe perguntas para refinar e esclarecer requisitos
3. **AnswerQuestion**: Stakeholder responde às perguntas propostas pelo Collector

### Ações de Modelagem:
4. **WriteReqDraft**: Collector escreve rascunhos de requisitos baseados nas histórias e respostas
5. **ExtractEntity**: Modeler extrai entidades dos requisitos (atores, máquinas, etc.)
6. **ExtractRelation**: Modeler extrai relacionamentos entre as entidades identificadas

### Ações de Verificação:
7. **CheckRequirement**: Checker verifica a qualidade, completude e consistência dos requisitos

### Ações de Especificação:
8. **WriteSRS**: Documenter escreve a especificação final de requisitos de software (SRS)
9. **WriteCheckReport**: Documenter escreve relatórios de verificação quando problemas são identificados

---

## 🗄️ Workspace Colaborativo

O framework MARE utiliza um **workspace compartilhado** que serve como mecanismo central de comunicação e colaboração entre os agentes.

### Características do Workspace:

**Armazenamento Centralizado**: Utiliza formato JSON ou SQLite para armazenar todos os artefatos gerados durante o processo.

**Versionamento Automático**: Mantém histórico de versões dos artefatos para rastreabilidade completa.

**Propriedades dos Artefatos**: Cada artefato no workspace possui cinco propriedades:
- **content**: Conteúdo do artefato de requisitos
- **role**: Papel/função do agente que gerou o artefato
- **caused_by**: Ação que gerou o artefato
- **sent_from**: Agente que enviou o artefato
- **send_to**: Agente destinatário do artefato

**Mecanismo de Migração de Ações**: O workspace facilita o fluxo de artefatos entre agentes através de um sistema de migração que determina qual ação deve ser executada em seguida baseada no estado atual.

### Tipos de Artefatos Armazenados:
- Histórias de usuário (User Stories)
- Perguntas e respostas (Questions/Answers)
- Rascunhos de requisitos (Requirement Drafts)
- Modelos de entidades e relacionamentos
- Relatórios de verificação
- Especificações finais (SRS)

---

## 🔄 Fluxo Completo do Processo MARE

O framework MARE executa um processo iterativo e sequencial dividido em quatro etapas principais:

### 1. **Elicitação de Requisitos**
**Objetivo**: Capturar e refinar as necessidades dos stakeholders

**Fluxo**:
1. Stakeholder Agent expressa histórias de usuário iniciais (SpeakUserStories)
2. Collector Agent propõe perguntas para esclarecer detalhes (ProposeQuestion)
3. Stakeholder Agent responde às perguntas (AnswerQuestion)
4. Processo iterativo até que informações suficientes sejam coletadas

### 2. **Modelagem de Requisitos**
**Objetivo**: Estruturar e organizar os requisitos coletados

**Fluxo**:
1. Collector Agent cria rascunhos de requisitos baseados nas informações coletadas (WriteReqDraft)
2. Modeler Agent extrai entidades dos requisitos (ExtractEntity)
3. Modeler Agent identifica relacionamentos entre entidades (ExtractRelation)
4. Geração do modelo estruturado de requisitos

### 3. **Verificação de Requisitos**
**Objetivo**: Validar qualidade, completude e consistência

**Fluxo**:
1. Checker Agent analisa os requisitos e modelo gerados (CheckRequirement)
2. Verificação de critérios de aceitação predefinidos
3. Identificação de inconsistências, lacunas ou problemas
4. Geração de feedback para refinamento se necessário

### 4. **Especificação de Requisitos**
**Objetivo**: Gerar documentação final ou relatórios de problemas

**Fluxo**:
1. Se requisitos atendem aos critérios de qualidade:
   - Documenter Agent gera SRS final (WriteSRS)
2. Se problemas são identificados:
   - Documenter Agent gera relatório de verificação (WriteCheckReport)
   - Retorno para etapas anteriores para refinamento

### Características do Fluxo:
- **Iterativo**: Permite refinamento contínuo até atingir qualidade desejada
- **Colaborativo**: Cada agente contribui com sua especialização
- **Rastreável**: Todas as decisões e mudanças são registradas no workspace
- **Flexível**: Adapta-se a diferentes tipos de sistemas e domínios

---


## 📊 Avaliação e Métricas de Performance

### Métricas Utilizadas

O framework MARE foi avaliado usando três métricas amplamente utilizadas na área:

**Precision (P)**: Refere-se à razão entre o número de predições corretas e o número total de predições feitas pelo modelo.

**Recall (R)**: Refere-se à razão entre o número de predições corretas e o número total de amostras no conjunto de teste dourado.

**F1-Score (F1)**: É a média harmônica entre Precision e Recall, fornecendo uma medida balanceada da performance.

### Resultados Experimentais

**Datasets de Avaliação**:
- 5 casos públicos para geração de diagramas de caso de uso
- 1 dataset público para geração de modelos de objetivo  
- 4 novos casos de avaliação criados especificamente para este trabalho

**Baselines Comparadas**:
- **IT4RE**: Abordagem para identificar automaticamente atores e ações de descrições de requisitos em linguagem natural
- **EPD**: Método para extrair entidades de requisitos baseado em BERT
- **HAGM**: Abordagem híbrida para requisitos baseada em aprendizado de máquina e raciocínio lógico

### Performance Superior

**Ganho Médio Reportado**: O framework MARE demonstrou performance superior às baselines em aproximadamente **15,4%** em termos de F1-score.

**Resultados Específicos** (baseados nas tabelas do paper):

**Para Modelagem de Diagramas de Problema**:
- MARE(gpt-3.5-turbo): F1-score médio de 68.7%
- MARE(text-davinci-002): F1-score médio de 84.1%
- MARE(text-davinci-003): F1-score médio de 82.6%

**Para Modelagem de Diagramas de Caso de Uso**:
- Performance consistentemente superior às baselines IT4RE, EPD e HAGM
- Melhoria significativa na extração de entidades e relacionamentos

### Avaliação Qualitativa

**Aspectos Avaliados**:
1. **Correção**: Precisão dos requisitos gerados
2. **Completude**: Cobertura abrangente das necessidades dos stakeholders  
3. **Consistência**: Coerência interna dos artefatos gerados

**Metodologia de Avaliação**:
- Avaliação manual por especialistas em engenharia de software
- Comparação com especificações de referência
- Análise de casos reais de sistemas de software

---

## 🔗 Referências e Recursos

**Paper Original**: 
- Título: "MARE: Multi-Agents Collaboration Framework for Requirements Engineering"
- ArXiv: https://arxiv.org/abs/2405.03256
- Autores: Dongning Jin, Zhi Jin, Xiaohong Chen, Chunhui Wang

**Implementação Técnica**:
- Framework base: LangChain/LangGraph para orquestração de agentes
- Modelos LLM: ChatGPT-3.5, text-davinci-002, text-davinci-003
- Armazenamento: JSON/SQLite para workspace compartilhado

**Contribuições Principais**:
1. Primeiro estudo a explorar automação end-to-end do processo completo de RE
2. Framework multi-agente inovador para colaboração em tarefas de RE
3. Workspace compartilhado para facilitar comunicação entre agentes
4. Performance superior demonstrada em múltiplos datasets e métricas

---

## 💡 Insights para Implementação

**Pontos-Chave para Desenvolvimento da CLI**:

1. **Modularidade**: Cada agente deve ser implementado como módulo independente
2. **Flexibilidade**: Suporte a diferentes modelos LLM e configurações
3. **Rastreabilidade**: Logging completo de todas as ações e decisões
4. **Escalabilidade**: Arquitetura que permita adição de novos agentes ou ações
5. **Usabilidade**: Interface CLI intuitiva com comandos claros e documentação

**Considerações Técnicas**:
- Integração com APIs de LLMs (OpenAI, etc.)
- Sistema robusto de tratamento de erros
- Configuração flexível via arquivos de configuração
- Suporte a diferentes formatos de saída (JSON, Markdown, PDF)
- Versionamento e backup automático do workspace

---

*Documento gerado como parte da análise do framework MARE para desenvolvimento da CLI Python com LangChain/LangGraph*

