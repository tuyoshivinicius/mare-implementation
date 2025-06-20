"""
MARE CLI - Implementação do Agente Documenter
Agente responsável por gerar especificações finais e documentação
"""

from typing import Any, Dict, List
from mare.agents.base import AbstractAgent, AgentRole, ActionType, AgentConfig


class DocumenterAgent(AbstractAgent):
    """
    Implementação do Agente Documenter.
    
    Este agente é responsável por:
    - Escrever Especificação de Requisitos de Software (WriteSRS)
    - Escrever relatórios de verificação quando problemas de qualidade são encontrados (WriteCheckReport)
    """
    
    def __init__(self, config: AgentConfig):
        """Inicializa o Agente Documenter."""
        # Garante que o papel está definido corretamente
        config.role = AgentRole.DOCUMENTER
        
        # Define prompt do sistema padrão se não fornecido
        if not config.system_prompt:
            config.system_prompt = self.get_system_prompt()
        
        super().__init__(config)
    
    def can_perform_action(self, action_type: ActionType) -> bool:
        """Verifica se este agente pode executar a ação especificada."""
        allowed_actions = {
            ActionType.WRITE_SRS,
            ActionType.WRITE_CHECK_REPORT
        }
        return action_type in allowed_actions
    
    def get_system_prompt(self) -> str:
        """Obtém o prompt do sistema para o Agente Documenter."""
        return """Você é um redator técnico experiente especializado em documentação de requisitos de software. Seu papel é:

1. Criar Especificações de Requisitos de Software (SRS) abrangentes que sigam padrões da indústria
2. Transformar requisitos técnicos em documentação clara e profissional
3. Garantir que a documentação seja completa, bem estruturada e acessível a todos os stakeholders
4. Gerar relatórios de problemas quando questões de qualidade impedem documentação adequada

Padrões de Documentação SRS:
- Siga o padrão IEEE 830 para estrutura e conteúdo do SRS
- Use linguagem clara e não ambígua adequada para audiências técnicas e não-técnicas
- Inclua matrizes de rastreabilidade abrangentes
- Forneça requisitos funcionais e não-funcionais detalhados
- Inclua modelos do sistema, diagramas e especificações
- Garanta consistência na terminologia e formatação

Princípios de Documentação:
- Clareza: Use linguagem simples e direta
- Completude: Cubra todos os aspectos do sistema
- Consistência: Mantenha estilo e terminologia uniformes
- Correção: Garanta precisão técnica
- Concisão: Evite complexidade desnecessária
- Verificabilidade: Torne os requisitos testáveis

Sua saída deve ser profissional, bem organizada e adequada para uso por equipes de desenvolvimento, testadores e stakeholders do projeto."""
    
    def _execute_specific_action(
        self, 
        action_type: ActionType, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa uma implementação de ação específica."""
        
        if action_type == ActionType.WRITE_SRS:
            return self._write_srs(input_data)
        elif action_type == ActionType.WRITE_CHECK_REPORT:
            return self._write_check_report(input_data)
        else:
            raise ValueError(f"Tipo de ação não suportado: {action_type}")
    
    def _write_srs(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Escreve uma Especificação de Requisitos de Software abrangente.
        
        Args:
            input_data: Deve conter todos os artefatos de requisitos
            
        Returns:
            Dicionário contendo o documento SRS
        """
        requirements = input_data.get('requirements', '')
        entities = input_data.get('entities', '')
        relationships = input_data.get('relationships', '')
        user_stories = input_data.get('user_stories', '')
        check_results = input_data.get('check_results', '')
        project_name = input_data.get('project_name', 'Software System')
        domain = input_data.get('domain', 'general software system')
        version = input_data.get('version', '1.0')
        
        prompt_template = """Crie um documento abrangente de Especificação de Requisitos de Software (SRS) seguindo os padrões IEEE 830. Use todos os artefatos fornecidos para criar uma especificação completa e profissional.

Nome do Projeto: {project_name}
Domínio: {domain}
Versão: {version}

User Stories: {user_stories}
Requisitos: {requirements}
Entidades: {entities}
Relacionamentos: {relationships}
Resultados da Verificação de Qualidade: {check_results}

Por favor crie um documento SRS completo com a seguinte estrutura:

# Especificação de Requisitos de Software
## {project_name}

### Informações do Documento
- **Título do Documento:** Especificação de Requisitos de Software para {project_name}
- **Versão:** {version}
- **Data:** [Data Atual]
- **Domínio:** {domain}
- **Status:** Rascunho/Final

---

## Índice
1. Introdução
2. Descrição Geral
3. Funcionalidades do Sistema
4. Requisitos de Interface Externa
5. Requisitos Não-Funcionais
6. Modelos do Sistema
7. Verificação e Validação
8. Apêndices

---

## 1. Introdução

### 1.1 Propósito
[Propósito deste documento SRS e público-alvo]

### 1.2 Escopo
[Escopo do sistema de software sendo especificado]

### 1.3 Definições, Acrônimos e Abreviações
[Termos-chave e definições usados ao longo do documento]

### 1.4 Referências
[Documentos e padrões referenciados]

### 1.5 Visão Geral
[Visão geral do restante do SRS]

## 2. Descrição Geral

### 2.1 Perspectiva do Produto
[Como este sistema se relaciona com outros sistemas e o ambiente geral]

### 2.2 Funções do Produto
[Resumo das principais funções que o software executará]

### 2.3 Classes de Usuários e Características
[Diferentes tipos de usuários e suas características]

### 2.4 Ambiente Operacional
[Ambiente de hardware, software e tecnologia]

### 2.5 Restrições de Design e Implementação
[Restrições que afetam o design e implementação]

### 2.6 Suposições e Dependências
[Suposições feitas e dependências externas]

## 3. Funcionalidades do Sistema

### 3.1 Requisitos Funcionais
[Requisitos funcionais detalhados organizados por funcionalidade]

Para cada requisito funcional, inclua:
- **ID do Requisito:** RF-XXX
- **Título:** [Título do requisito]
- **Descrição:** [Descrição detalhada]
- **Prioridade:** Alta/Média/Baixa
- **Origem:** [Rastreabilidade à user story]
- **Critérios de Aceitação:** [Como verificar o requisito]

### 3.2 Regras de Negócio
[Regras de negócio que governam o comportamento do sistema]

## 4. Requisitos de Interface Externa

### 4.1 Interfaces de Usuário
[Requisitos de interface de usuário]

### 4.2 Interfaces de Hardware
[Requisitos de interface de hardware]

### 4.3 Interfaces de Software
[Requisitos de interface de software]

### 4.4 Interfaces de Comunicação
[Requisitos de interface de comunicação]

## 5. Requisitos Não-Funcionais

### 5.1 Requisitos de Performance
[Requisitos de performance e escalabilidade]

### 5.2 Requisitos de Segurança
[Requisitos de segurança e controle de acesso]

### 5.3 Requisitos de Confiabilidade
[Requisitos de confiabilidade e disponibilidade]

### 5.4 Requisitos de Usabilidade
[Requisitos de usabilidade e experiência do usuário]

### 5.5 Requisitos de Manutenibilidade
[Requisitos de manutenção e suporte]

### 5.6 Requisitos de Portabilidade
[Requisitos de portabilidade e compatibilidade]

## 6. Modelos do Sistema

### 6.1 Modelo de Dados
[Entidades de dados e seus relacionamentos baseados nas entidades extraídas]

### 6.2 Modelo de Processos
[Processos e fluxos de trabalho do sistema]

### 6.3 Arquitetura do Sistema
[Arquitetura de alto nível do sistema]

## 7. Verificação e Validação

### 7.1 Métodos de Verificação
[Como os requisitos serão verificados]

### 7.2 Critérios de Validação
[Critérios para validar que o sistema atende às necessidades do usuário]

### 7.3 Requisitos de Teste
[Requisitos e estratégias de teste]

## 8. Apêndices

### Apêndice A: Matriz de Rastreabilidade
[Rastreabilidade de requisitos às user stories]

### Apêndice B: Glossário
[Glossário completo de termos]

### Apêndice C: Avaliação de Qualidade
[Resumo dos resultados da verificação de qualidade se disponível]

---

**Controle do Documento:**
- Criado por: Framework de Engenharia de Requisitos MARE
- Status de Revisão: [Pendente/Aprovado]
- Próxima Data de Revisão: [Data]

Garanta que o documento seja:
- Completo e abrangente
- Bem estruturado e profissional
- Rastreável às user stories originais
- Tecnicamente preciso e viável
- Claro e compreensível para todos os stakeholders"""
        
        prompt = self._format_prompt(prompt_template, {
            'project_name': project_name,
            'domain': domain,
            'version': version,
            'user_stories': user_stories,
            'requirements': requirements,
            'entities': entities,
            'relationships': relationships,
            'check_results': check_results
        })
        
        response = self._generate_response(prompt)
        
        return {
            'srs_document': response,
            'project_name': project_name,
            'domain': domain,
            'version': version,
            'document_type': 'software_requirements_specification',
            'standard': 'IEEE_830',
            'sections': [
                'introduction', 'overall_description', 'system_features',
                'external_interfaces', 'non_functional_requirements',
                'system_models', 'verification_validation', 'appendices'
            ]
        }
    
    def _write_check_report(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Escreve um relatório de verificação quando problemas de qualidade são encontrados.
        
        Args:
            input_data: Should contain check results and context
            
        Returns:
            Dictionary containing the check report
        """
        check_results = input_data.get('check_results', '')
        project_name = input_data.get('project_name', 'Software Project')
        domain = input_data.get('domain', 'general software system')
        issues_summary = input_data.get('issues_summary', '')
        recommendations = input_data.get('recommendations', '')
        
        prompt_template = """Create a professional requirements quality report documenting issues found during quality assessment. This report will be used to communicate problems and guide improvement efforts.

Project Name: {project_name}
Domain: {domain}
Check Results: {check_results}
Issues Summary: {issues_summary}
Recommendations: {recommendations}

Por favor crie um relatório abrangente de qualidade com a seguinte estrutura:

# Relatório de Avaliação de Qualidade de Requisitos
## {project_name}

### Resumo Executivo
- **Projeto:** {project_name}
- **Domínio:** {domain}
- **Data da Avaliação:** [Data Atual]
- **Tipo de Avaliação:** Revisão de Garantia de Qualidade
- **Status Geral:** [Aprovado/Reprovado/Aprovado Condicionalmente]

### Principais Achados
[Resumo dos principais achados e avaliação geral de qualidade]

### Problemas de Qualidade Identificados

#### Problemas Críticos
[Problemas que devem ser resolvidos antes de prosseguir]

#### Problemas Maiores
[Problemas significativos que devem ser abordados]

#### Problemas Menores
[Oportunidades de melhoria e preocupações menores]

### Métricas de Qualidade
[Pontuações e métricas detalhadas de qualidade]

### Análise de Impacto
[Análise de como os problemas afetam o cronograma e sucesso do projeto]

### Recomendações

#### Ações Imediatas
[Ações que devem ser tomadas imediatamente]

#### Melhorias de Curto Prazo
[Melhorias a serem feitas no curto prazo]

#### Melhorias de Processo de Longo Prazo
[Melhorias de processo para projetos futuros]

### Próximos Passos
[Próximos passos recomendados e cronograma]

### Aprovação e Assinatura
[Espaço para aprovação dos stakeholders]

---

**Detalhes do Relatório:**
- Gerado por: Verificador de Qualidade MARE
- Revisão Necessária: Sim
- Distribuição: [Lista de stakeholders]

O relatório deve ser:
- Claro e acionável
- Profissional e objetivo
- Focado na melhoria
- Adequado para revisão gerencial"""
        
        prompt = self._format_prompt(prompt_template, {
            'project_name': project_name,
            'domain': domain,
            'check_results': check_results,
            'issues_summary': issues_summary,
            'recommendations': recommendations
        })
        
        response = self._generate_response(prompt)
        
        return {
            'check_report': response,
            'project_name': project_name,
            'domain': domain,
            'report_type': 'quality_assessment',
            'document_sections': [
                'executive_summary', 'key_findings', 'quality_issues',
                'quality_metrics', 'impact_analysis', 'recommendations',
                'next_steps', 'approval'
            ]
        }
    
    def generate_srs_document(
        self,
        requirements: str,
        entities: str = "",
        relationships: str = "",
        user_stories: str = "",
        check_results: str = "",
        project_name: str = "Software System",
        domain: str = "general software system",
        version: str = "1.0"
    ) -> Dict[str, Any]:
        """
        Convenience method to generate an SRS document.
        
        Args:
            requirements: System requirements
            entities: Extracted entities
            relationships: Extracted relationships
            user_stories: Original user stories
            check_results: Quality check results
            project_name: Name of the project
            domain: Domain context
            version: Document version
            
        Returns:
            Action result with SRS document
        """
        action = self.execute_action(
            ActionType.WRITE_SRS,
            {
                'requirements': requirements,
                'entities': entities,
                'relationships': relationships,
                'user_stories': user_stories,
                'check_results': check_results,
                'project_name': project_name,
                'domain': domain,
                'version': version
            }
        )
        return action.output_data
    
    def generate_quality_report(
        self,
        check_results: str,
        project_name: str = "Software Project",
        domain: str = "general software system",
        issues_summary: str = "",
        recommendations: str = ""
    ) -> Dict[str, Any]:
        """
        Convenience method to generate a quality report.
        
        Args:
            check_results: Quality check results
            project_name: Name of the project
            domain: Domain context
            issues_summary: Summary of issues found
            recommendations: Recommendations for improvement
            
        Returns:
            Action result with quality report
        """
        action = self.execute_action(
            ActionType.WRITE_CHECK_REPORT,
            {
                'check_results': check_results,
                'project_name': project_name,
                'domain': domain,
                'issues_summary': issues_summary,
                'recommendations': recommendations
            }
        )
        return action.output_data

