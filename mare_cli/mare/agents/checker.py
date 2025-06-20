"""
MARE CLI - Implementação do Agente Checker
Agente responsável por verificar qualidade, completude e consistência dos requisitos
"""

from typing import Any, Dict, List
from mare.agents.base import AbstractAgent, AgentRole, ActionType, AgentConfig


class CheckerAgent(AbstractAgent):
    """
    Implementação do Agente Checker.
    
    Este agente é responsável por:
    - Verificar qualidade e consistência dos requisitos (CheckRequirement)
    - Escrever relatórios de verificação com descobertas e recomendações (WriteCheckReport)
    """
    
    def __init__(self, config: AgentConfig):
        """Inicializa o Agente Checker."""
        # Garante que o papel está definido corretamente
        config.role = AgentRole.CHECKER
        
        # Define prompt do sistema padrão se não fornecido
        if not config.system_prompt:
            config.system_prompt = self.get_system_prompt()
        
        super().__init__(config)
    
    def can_perform_action(self, action_type: ActionType) -> bool:
        """Verifica se este agente pode executar a ação especificada."""
        allowed_actions = {
            ActionType.CHECK_REQUIREMENT,
            ActionType.WRITE_CHECK_REPORT
        }
        return action_type in allowed_actions
    
    def get_system_prompt(self) -> str:
        """Obtém o prompt do sistema para o Agente Checker."""
        return """Você é um especialista experiente em garantia de qualidade de requisitos. Seu papel é:

1. Analisar requisitos quanto à qualidade, completude, consistência e correção
2. Identificar lacunas, ambiguidades, conflitos e problemas potenciais
3. Fornecer feedback detalhado e recomendações para melhoria
4. Garantir que os requisitos atendam aos padrões da indústria e melhores práticas

Critérios de Qualidade para Avaliar:

COMPLETUDE:
- Todos os requisitos funcionais estão cobertos?
- Os requisitos não-funcionais estão especificados?
- Todos os cenários de usuário estão abordados?
- Casos extremos e condições de erro estão cobertos?

CONSISTÊNCIA:
- Os requisitos são internamente consistentes?
- Os requisitos conflitam entre si?
- A terminologia é usada consistentemente?
- As suposições e restrições estão alinhadas?

CLAREZA:
- Os requisitos são não ambíguos?
- A linguagem é clara e precisa?
- Os critérios de aceitação estão bem definidos?
- Os requisitos podem ser entendidos por todos os stakeholders?

CORREÇÃO:
- Os requisitos refletem com precisão as necessidades dos usuários?
- As especificações técnicas são viáveis?
- As regras de negócio estão capturadas corretamente?
- As dependências estão identificadas adequadamente?

TESTABILIDADE:
- Os requisitos podem ser verificados/testados?
- Os critérios de aceitação são mensuráveis?
- Os critérios de sucesso estão claramente definidos?

RASTREABILIDADE:
- Os requisitos podem ser rastreados às user stories?
- Os relacionamentos entre requisitos estão claros?
- A análise de impacto é possível?

Sua análise deve ser completa, construtiva e acionável."""
    
    def _execute_specific_action(
        self, 
        action_type: ActionType, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa uma implementação de ação específica."""
        
        if action_type == ActionType.CHECK_REQUIREMENT:
            return self._check_requirement(input_data)
        elif action_type == ActionType.WRITE_CHECK_REPORT:
            return self._write_check_report(input_data)
        else:
            raise ValueError(f"Tipo de ação não suportado: {action_type}")
    
    def _check_requirement(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verifica requisitos quanto à qualidade e consistência.
        
        Args:
            input_data: Deve conter 'requirements', 'entities', 'relationships'
            
        Returns:
            Dicionário contendo resultados da verificação
        """
        requirements = input_data.get('requirements', '')
        entities = input_data.get('entities', '')
        relationships = input_data.get('relationships', '')
        user_stories = input_data.get('user_stories', '')
        domain = input_data.get('domain', 'sistema de software geral')
        check_focus = input_data.get('check_focus', 'abrangente')
        
        prompt_template = """Execute uma verificação abrangente de qualidade nos seguintes artefatos de requisitos. Analise quanto à completude, consistência, clareza, correção e testabilidade.

Requisitos: {requirements}

Entidades: {entities}

Relacionamentos: {relationships}

User Stories Originais: {user_stories}

Domínio: {domain}

Foco da Verificação: {check_focus}

Por favor forneça uma análise detalhada cobrindo:

1. ANÁLISE DE COMPLETUDE
   - Requisitos funcionais ausentes
   - Requisitos não-funcionais ausentes
   - Cenários de usuário não cobertos
   - Casos extremos e tratamento de erro ausentes
   - Pontuação: [1-10] com justificativa

2. ANÁLISE DE CONSISTÊNCIA
   - Conflitos internos entre requisitos
   - Inconsistências de terminologia
   - Suposições ou restrições conflitantes
   - Entidades e relacionamentos desalinhados
   - Pontuação: [1-10] com justificativa

3. ANÁLISE DE CLAREZA
   - Requisitos ambíguos
   - Critérios de aceitação pouco claros
   - Linguagem vaga ou imprecisa
   - Definições ausentes
   - Pontuação: [1-10] com justificativa

4. ANÁLISE DE CORREÇÃO
   - Requisitos que não correspondem às user stories
   - Especificações tecnicamente inviáveis
   - Regras de negócio incorretas
   - Dependências ausentes ou erradas
   - Pontuação: [1-10] com justificativa

5. ANÁLISE DE TESTABILIDADE
   - Requisitos que não podem ser testados
   - Critérios mensuráveis ausentes
   - Condições de sucesso pouco claras
   - Desafios de verificação
   - Pontuação: [1-10] com justificativa

6. ANÁLISE DE RASTREABILIDADE
   - Requisitos não rastreáveis às user stories
   - Relacionamentos de requisitos ausentes
   - Requisitos órfãos ou duplicados
   - Lacunas na análise de impacto
   - Pontuação: [1-10] com justificativa

7. AVALIAÇÃO GERAL
   - Pontuação Geral de Qualidade: [1-10]
   - Pronto para Implementação: [Sim/Não]
   - Contagem de Problemas Críticos: [número]
   - Contagem de Problemas Maiores: [número]
   - Contagem de Problemas Menores: [número]

Para cada problema identificado, forneça:
- ID do Problema (ex: COMP-001, CONS-001)
- Severidade: Crítico/Maior/Menor
- Descrição: Qual é o problema
- Impacto: Como afeta o projeto
- Recomendação: Como corrigi-lo
- Localização: Onde nos requisitos ocorre"""
        
        prompt = self._format_prompt(prompt_template, {
            'requirements': requirements,
            'entities': entities,
            'relationships': relationships,
            'user_stories': user_stories,
            'domain': domain,
            'check_focus': check_focus
        })
        
        response = self._generate_response(prompt)
        
        return {
            'check_results': response,
            'domain': domain,
            'check_focus': check_focus,
            'artifacts_checked': ['requirements', 'entities', 'relationships'],
            'quality_dimensions': ['completeness', 'consistency', 'clarity', 'correctness', 'testability', 'traceability']
        }
    
    def _write_check_report(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write a comprehensive check report.
        
        Args:
            input_data: Should contain 'check_results' and context
            
        Returns:
            Dictionary containing formatted check report
        """
        check_results = input_data.get('check_results', '')
        project_name = input_data.get('project_name', 'Unnamed Project')
        domain = input_data.get('domain', 'general software system')
        report_type = input_data.get('report_type', 'comprehensive')
        
        prompt_template = """Com base nos resultados da verificação de qualidade, crie um relatório profissional de garantia de qualidade de requisitos. Formate-o como um documento abrangente adequado para stakeholders e equipes de desenvolvimento.

Resultados da Verificação: {check_results}

Nome do Projeto: {project_name}
Domínio: {domain}
Tipo de Relatório: {report_type}

Por favor crie um relatório estruturado com as seguintes seções:

# Relatório de Garantia de Qualidade de Requisitos

## Resumo Executivo
- Avaliação geral de qualidade
- Resumo dos principais achados
- Visão geral das recomendações
- Decisão Prosseguir/Não Prosseguir

## Informações do Projeto
- Projeto: {project_name}
- Domínio: {domain}
- Data da Revisão: [data atual]
- Tipo de Revisão: {report_type}

## Resumo das Métricas de Qualidade
- Pontuação de Completude: [pontuação/10]
- Pontuação de Consistência: [pontuação/10]
- Pontuação de Clareza: [pontuação/10]
- Pontuação de Correção: [pontuação/10]
- Pontuação de Testabilidade: [pontuação/10]
- Pontuação de Rastreabilidade: [pontuação/10]
- **Pontuação Geral de Qualidade: [pontuação/10]**

## Resumo de Problemas
- Problemas Críticos: [contagem]
- Problemas Maiores: [contagem]
- Problemas Menores: [contagem]
- Total de Problemas: [contagem]

## Achados Detalhados

### Problemas Críticos
[Liste todos os problemas críticos com ID, descrição, impacto e recomendações]

### Problemas Maiores
[Liste todos os problemas maiores com ID, descrição, impacto e recomendações]

### Problemas Menores
[Liste todos os problemas menores com ID, descrição, impacto e recomendações]

## Análise de Qualidade por Dimensão

### Análise de Completude
[Análise detalhada de completude]

### Análise de Consistência
[Análise detalhada de consistência]

### Análise de Clareza
[Análise detalhada de clareza]

### Análise de Correção
[Análise detalhada de correção]

### Análise de Testabilidade
[Análise detalhada de testabilidade]

### Análise de Rastreabilidade
[Análise detalhada de rastreabilidade]

## Recomendações

### Ações Imediatas Necessárias
[Problemas críticos e maiores que devem ser abordados]

### Oportunidades de Melhoria
[Problemas menores e sugestões de aprimoramento]

### Melhorias de Processo
[Recomendações para melhorar o processo de requisitos]

## Conclusão
- Avaliação geral
- Prontidão para próxima fase
- Avaliação de risco
- Recomendação de aprovação

## Apêndices
- Lista detalhada de problemas
- Definições de critérios de qualidade
- Metodologia de revisão

---
*Este relatório foi gerado pelo Verificador de Qualidade de Requisitos MARE*"""
        
        prompt = self._format_prompt(prompt_template, {
            'check_results': check_results,
            'project_name': project_name,
            'domain': domain,
            'report_type': report_type
        })
        
        response = self._generate_response(prompt)
        
        return {
            'check_report': response,
            'project_name': project_name,
            'domain': domain,
            'report_type': report_type,
            'report_sections': [
                'executive_summary', 'project_info', 'quality_metrics', 
                'issues_summary', 'detailed_findings', 'quality_analysis',
                'recommendations', 'conclusion', 'appendices'
            ]
        }
    
    def perform_quality_check(
        self, 
        requirements: str,
        entities: str = "",
        relationships: str = "",
        user_stories: str = "",
        domain: str = "general software system",
        check_focus: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Convenience method to perform a quality check.
        
        Args:
            requirements: Requirements to check
            entities: Extracted entities
            relationships: Extracted relationships
            user_stories: Original user stories
            domain: Domain context
            check_focus: Focus area for checking
            
        Returns:
            Action result with check results
        """
        action = self.execute_action(
            ActionType.CHECK_REQUIREMENT,
            {
                'requirements': requirements,
                'entities': entities,
                'relationships': relationships,
                'user_stories': user_stories,
                'domain': domain,
                'check_focus': check_focus
            }
        )
        return action.output_data
    
    def generate_quality_report(
        self, 
        check_results: str,
        project_name: str = "Unnamed Project",
        domain: str = "general software system",
        report_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Convenience method to generate a quality report.
        
        Args:
            check_results: Results from quality check
            project_name: Name of the project
            domain: Domain context
            report_type: Type of report to generate
            
        Returns:
            Action result with formatted report
        """
        action = self.execute_action(
            ActionType.WRITE_CHECK_REPORT,
            {
                'check_results': check_results,
                'project_name': project_name,
                'domain': domain,
                'report_type': report_type
            }
        )
        return action.output_data

