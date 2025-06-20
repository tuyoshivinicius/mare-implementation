# Exemplos Práticos - MARE CLI

Esta seção apresenta exemplos detalhados de uso do MARE CLI em diferentes domínios e cenários reais.

## 🛒 Exemplo 1: Sistema de E-commerce

### Contexto

Desenvolvimento de uma plataforma de e-commerce para pequenas e médias empresas.

### Configuração Inicial

```bash
# Criar projeto
mare init ecommerce_platform --template web_app --llm-provider openai

cd ecommerce_platform
```

### Entrada do Sistema (input.md)

```markdown
# Plataforma de E-commerce B2B/B2C

## Visão Geral
Desenvolver uma plataforma de e-commerce que atenda tanto empresas (B2B) quanto consumidores finais (B2C), permitindo múltiplos vendedores e compradores.

## Funcionalidades Principais

### Para Vendedores
- Cadastro e gestão de produtos
- Controle de estoque em tempo real
- Gestão de pedidos e vendas
- Relatórios financeiros e de performance
- Configuração de promoções e descontos

### Para Compradores
- Navegação por categorias de produtos
- Busca avançada com filtros
- Carrinho de compras persistente
- Múltiplas formas de pagamento
- Rastreamento de pedidos
- Sistema de avaliações e comentários

### Administrativo
- Gestão de usuários e permissões
- Moderação de conteúdo
- Análise de dados e métricas
- Configuração de taxas e comissões
- Suporte ao cliente integrado

## Requisitos Técnicos

### Performance
- Suporte a 10.000 usuários simultâneos
- Tempo de resposta < 2 segundos
- Disponibilidade 99.9%
- Escalabilidade horizontal

### Segurança
- Criptografia de dados sensíveis
- Conformidade com PCI DSS
- Autenticação multifator
- Proteção contra fraudes

### Integrações
- Gateways de pagamento (Stripe, PayPal, PagSeguro)
- Sistemas de logística (Correios, transportadoras)
- ERPs empresariais
- Sistemas de email marketing

## Contexto de Negócio
- Mercado: América Latina
- Público-alvo: PMEs e consumidores finais
- Modelo de receita: Comissão sobre vendas + assinaturas premium
- Prazo: 12 meses para MVP, 18 meses para versão completa
```

### Configuração Específica

```yaml
# .mare/config.yaml
project:
  name: "Plataforma E-commerce"
  domain: "e-commerce"
  complexity: "high"

llm:
  provider: "openai"
  model: "gpt-4"
  temperature: 0.6

pipeline:
  max_iterations: 8
  quality_threshold: 0.9
  focus_areas:
    - "user_experience"
    - "security"
    - "scalability"
    - "integration"

agents:
  stakeholder:
    model: "gpt-4"
    temperature: 0.7
    context: |
      Você representa stakeholders de e-commerce com experiência em:
      - Plataformas multi-vendor
      - Pagamentos online
      - Logística e fulfillment
      - Experiência do usuário em compras online
  
  collector:
    model: "gpt-4"
    temperature: 0.5
    max_questions: 25
    focus_areas:
      - "user_journeys"
      - "business_rules"
      - "integration_requirements"
      - "security_requirements"
  
  modeler:
    model: "gpt-4"
    temperature: 0.4
    modeling_approach: "domain_driven_design"
    include_patterns: ["microservices", "event_sourcing", "cqrs"]
  
  checker:
    model: "gpt-4"
    temperature: 0.2
    quality_focus:
      - "scalability"
      - "security"
      - "usability"
      - "maintainability"
  
  documenter:
    model: "gpt-4"
    temperature: 0.3
    output_style: "enterprise"
    include_sections:
      - "architecture_overview"
      - "api_specifications"
      - "security_requirements"
      - "deployment_guide"
```

### Execução

```bash
# Executar pipeline com configurações específicas
mare run --interactive --max-iterations 8

# Monitorar progresso
mare status --detailed

# Exportar documentação completa
mare export pdf --template enterprise --output-file ecommerce_requirements.pdf
```

### Resultados Esperados

O pipeline gerará:
- Especificação detalhada de requisitos (50+ páginas)
- Modelo de domínio com 20+ entidades
- Casos de uso detalhados para cada persona
- Requisitos de segurança específicos para e-commerce
- Especificações de API para integrações
- Plano de arquitetura de microserviços

## 🏥 Exemplo 2: Sistema Hospitalar

### Contexto

Sistema de gestão hospitalar para hospital de médio porte.

### Configuração Inicial

```bash
mare init hospital_management --template enterprise --llm-provider openai
cd hospital_management
```

### Entrada do Sistema

```markdown
# Sistema de Gestão Hospitalar Integrado

## Contexto
Hospital de médio porte (200 leitos) necessita de sistema integrado para gestão completa de operações médicas e administrativas.

## Módulos Principais

### Gestão de Pacientes
- Cadastro e prontuário eletrônico
- Histórico médico completo
- Agendamento de consultas e exames
- Controle de internações
- Alta médica e transferências

### Gestão Médica
- Prescrições eletrônicas
- Resultados de exames
- Protocolos clínicos
- Telemedicina
- Gestão de cirurgias

### Gestão Administrativa
- Faturamento e convênios
- Controle financeiro
- Gestão de recursos humanos
- Controle de estoque farmacêutico
- Relatórios gerenciais

### Gestão de Recursos
- Agenda de salas e equipamentos
- Controle de materiais médicos
- Gestão de leitos
- Manutenção preventiva
- Controle de acesso

## Requisitos Regulatórios
- Conformidade com CFM (Conselho Federal de Medicina)
- LGPD (Lei Geral de Proteção de Dados)
- Certificação digital ICP-Brasil
- Padrões HL7 FHIR
- Integração com DATASUS

## Requisitos Técnicos
- Disponibilidade 24/7 (99.99%)
- Backup automático e recuperação de desastres
- Auditoria completa de ações
- Criptografia de dados médicos
- Integração com equipamentos médicos

## Stakeholders
- Médicos e enfermeiros
- Administração hospitalar
- Pacientes e familiares
- Convênios médicos
- Órgãos reguladores
```

### Execução Especializada

```bash
# Configurar para domínio médico
mare config set project.domain "healthcare"
mare config set pipeline.quality_threshold 0.95

# Executar com foco em conformidade
mare run --focus compliance --interactive

# Gerar documentação para auditoria
mare export docx --template regulatory --include-compliance
```

## 📱 Exemplo 3: Aplicativo Móvel de Fitness

### Configuração

```bash
mare init fitness_tracker --template mobile_app
cd fitness_tracker
```

### Entrada Focada em Mobile

```markdown
# Aplicativo de Fitness e Bem-estar

## Conceito
App móvel para acompanhamento de atividades físicas, nutrição e bem-estar geral.

## Funcionalidades Core

### Rastreamento de Atividades
- Contagem de passos automática
- GPS para corridas e caminhadas
- Integração com wearables
- Reconhecimento automático de exercícios
- Métricas de performance

### Nutrição
- Diário alimentar com scanner de código de barras
- Base de dados nutricional brasileira
- Cálculo de macros e calorias
- Sugestões de refeições
- Controle de hidratação

### Gamificação
- Sistema de pontos e conquistas
- Desafios semanais/mensais
- Ranking entre amigos
- Badges por metas alcançadas
- Streaks de atividades

### Social
- Compartilhamento de atividades
- Grupos de exercícios
- Feed de atividades dos amigos
- Comentários e curtidas
- Eventos e competições

## Plataformas
- iOS (iPhone/iPad)
- Android (smartphones/tablets)
- Apple Watch / Wear OS
- Versão web básica

## Monetização
- Freemium (funcionalidades básicas gratuitas)
- Premium: planos personalizados, análises avançadas
- Parcerias com academias e nutricionistas
```

### Configuração Mobile-Specific

```yaml
# .mare/config.yaml
project:
  name: "Fitness Tracker App"
  domain: "mobile_health"
  platforms: ["ios", "android", "wearables"]

pipeline:
  focus_areas:
    - "user_experience"
    - "performance"
    - "offline_capability"
    - "privacy"

agents:
  stakeholder:
    context: |
      Você representa usuários de apps de fitness:
      - Iniciantes em exercícios
      - Atletas amadores
      - Pessoas focadas em perda de peso
      - Entusiastas de tecnologia wearable
  
  modeler:
    mobile_patterns: true
    offline_first: true
    include_patterns: ["mvvm", "repository", "observer"]
```

## 🏦 Exemplo 4: Sistema Bancário Digital

### Configuração para Fintech

```bash
mare init digital_bank --template enterprise
cd digital_bank
```

### Entrada Complexa

```markdown
# Banco Digital - Plataforma Completa

## Visão
Banco 100% digital focado em pessoas físicas e pequenas empresas, com produtos financeiros inovadores.

## Produtos Financeiros

### Conta Corrente Digital
- Abertura de conta 100% online
- Cartão de débito virtual e físico
- PIX integrado
- TED/DOC
- Pagamento de boletos

### Cartão de Crédito
- Aprovação em tempo real
- Limite dinâmico baseado em comportamento
- Cashback personalizado
- Controle total pelo app
- Cartão virtual para compras online

### Investimentos
- CDB, LCI, LCA
- Fundos de investimento
- Tesouro Direto
- Ações e ETFs
- Robo-advisor para iniciantes

### Crédito
- Empréstimo pessoal
- Antecipação de recebíveis
- Financiamento de veículos
- Crédito para MEI/pequenas empresas

## Diferenciais Tecnológicos
- Inteligência artificial para análise de crédito
- Biometria facial e digital
- Blockchain para auditoria
- Open Banking completo
- API-first architecture

## Conformidade Regulatória
- Banco Central do Brasil (BACEN)
- Resolução 4.658 (segurança cibernética)
- LGPD
- Prevenção à lavagem de dinheiro (PLD)
- Know Your Customer (KYC)

## Requisitos de Segurança
- Criptografia end-to-end
- Tokenização de dados sensíveis
- Autenticação multifator obrigatória
- Monitoramento 24/7 de fraudes
- Backup geográfico distribuído
```

### Execução com Foco em Compliance

```bash
# Configurar para setor financeiro
mare config set project.domain "fintech"
mare config set pipeline.compliance_level "banking"
mare config set pipeline.quality_threshold 0.98

# Executar com validação regulatória
mare run --compliance-mode --max-iterations 12

# Gerar documentação para BACEN
mare export pdf --template banking_compliance
```

## 🎓 Exemplo 5: Plataforma Educacional

### Configuração

```bash
mare init learning_platform --template web_app
cd learning_platform
```

### Entrada Educacional

```markdown
# Plataforma de Ensino Online

## Missão
Democratizar o acesso à educação de qualidade através de uma plataforma online completa.

## Funcionalidades Principais

### Para Estudantes
- Catálogo de cursos por área
- Trilhas de aprendizagem personalizadas
- Videoaulas com qualidade adaptativa
- Exercícios interativos e gamificados
- Certificados digitais
- Fórum de discussões
- Mentoria online

### Para Professores
- Criação de cursos com editor visual
- Upload de materiais (vídeos, PDFs, slides)
- Criação de avaliações e quizzes
- Acompanhamento de progresso dos alunos
- Ferramentas de comunicação
- Analytics de engajamento

### Para Instituições
- Gestão de múltiplos cursos
- Relatórios de performance
- Integração com sistemas acadêmicos
- White-label para escolas
- Gestão financeira

## Tecnologias Educacionais
- Adaptive Learning (IA para personalização)
- Realidade Virtual para simulações
- Gamificação avançada
- Proctoring online para avaliações
- Reconhecimento de voz para idiomas

## Acessibilidade
- Conformidade WCAG 2.1 AA
- Legendas automáticas
- Leitor de tela compatível
- Alto contraste
- Navegação por teclado
```

## 🚀 Exemplo 6: Sistema IoT Industrial

### Configuração

```bash
mare init iot_industrial --template api_service
cd iot_industrial
```

### Entrada IoT

```markdown
# Plataforma IoT para Indústria 4.0

## Objetivo
Sistema de monitoramento e controle industrial baseado em IoT para otimização de processos produtivos.

## Componentes

### Sensores e Dispositivos
- Sensores de temperatura, pressão, vibração
- Câmeras de visão computacional
- Controladores PLC
- Gateways de comunicação
- Atuadores automatizados

### Plataforma Central
- Coleta de dados em tempo real
- Processamento de stream de dados
- Machine Learning para manutenção preditiva
- Dashboards em tempo real
- Alertas e notificações

### Integrações
- ERP empresarial
- Sistemas MES (Manufacturing Execution)
- SCADA existente
- Sistemas de qualidade
- Planejamento de produção

## Protocolos de Comunicação
- MQTT para dispositivos IoT
- OPC-UA para equipamentos industriais
- Modbus para sensores legados
- LoRaWAN para dispositivos remotos
- 5G para aplicações críticas

## Casos de Uso
- Manutenção preditiva de equipamentos
- Otimização de consumo energético
- Controle de qualidade automatizado
- Rastreabilidade de produtos
- Segurança industrial
```

## 📊 Comparação de Resultados

### Métricas por Domínio

| Domínio | Requisitos Gerados | Entidades | Tempo Médio | Qualidade |
|---------|-------------------|-----------|-------------|-----------|
| E-commerce | 85-120 | 25-35 | 45-60 min | 8.7/10 |
| Healthcare | 120-180 | 40-60 | 60-90 min | 9.2/10 |
| Mobile App | 60-90 | 15-25 | 30-45 min | 8.4/10 |
| Fintech | 150-200 | 35-50 | 75-120 min | 9.5/10 |
| EdTech | 70-100 | 20-30 | 40-60 min | 8.6/10 |
| IoT Industrial | 90-130 | 30-45 | 50-75 min | 8.9/10 |

### Padrões Identificados

#### Domínios Regulamentados (Healthcare, Fintech)
- Maior número de requisitos de conformidade
- Foco intenso em segurança e auditoria
- Documentação mais extensa
- Maior tempo de processamento

#### Aplicações Consumer (E-commerce, Mobile, EdTech)
- Foco em experiência do usuário
- Requisitos de performance e escalabilidade
- Funcionalidades sociais e gamificação
- Integração com terceiros

#### Sistemas Técnicos (IoT, APIs)
- Requisitos de integração complexos
- Protocolos de comunicação específicos
- Performance em tempo real
- Tolerância a falhas

## 🎯 Dicas de Otimização

### Para Melhores Resultados

1. **Entrada Detalhada**: Quanto mais contexto, melhor a qualidade
2. **Domínio Específico**: Configure o domínio correto para prompts especializados
3. **Iterações Adequadas**: Domínios complexos precisam de mais iterações
4. **Validação Humana**: Sempre revise os resultados gerados
5. **Configuração de Agentes**: Personalize prompts para seu contexto específico

### Configurações Recomendadas por Domínio

```yaml
# Healthcare/Fintech (Alta Conformidade)
pipeline:
  max_iterations: 10-15
  quality_threshold: 0.95
  focus_areas: ["compliance", "security", "auditability"]

# E-commerce/Consumer (UX Focus)
pipeline:
  max_iterations: 6-8
  quality_threshold: 0.85
  focus_areas: ["usability", "scalability", "integration"]

# IoT/Technical (Performance Focus)
pipeline:
  max_iterations: 8-10
  quality_threshold: 0.90
  focus_areas: ["performance", "reliability", "interoperability"]
```

---

Estes exemplos demonstram a versatilidade do MARE CLI em diferentes domínios e complexidades. Cada exemplo pode ser adaptado para necessidades específicas através da configuração de agentes, templates e parâmetros do pipeline.

