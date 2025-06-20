"""
MARE CLI - Implementação do Agente Collector
Agente responsável por coletar requisitos através de questionamento e rascunhos
"""

from typing import Any, Dict, List
from mare.agents.base import AbstractAgent, AgentRole, ActionType, AgentConfig


class CollectorAgent(AbstractAgent):
    """
    Implementação do Agente Collector.
    
    Este agente é responsável por:
    - Propor perguntas para esclarecer requisitos (ProposeQuestion)
    - Escrever rascunhos de requisitos baseados em informações coletadas (WriteReqDraft)
    """
    
    def __init__(self, config: AgentConfig):
        """Inicializa o Agente Collector."""
        # Garante que o papel está definido corretamente
        config.role = AgentRole.COLLECTOR
        
        # Define prompt do sistema padrão se não fornecido
        if not config.system_prompt:
            config.system_prompt = self.get_system_prompt()
        
        super().__init__(config)
    
    def can_perform_action(self, action_type: ActionType) -> bool:
        """Verifica se este agente pode executar a ação especificada."""
        allowed_actions = {
            ActionType.PROPOSE_QUESTION,
            ActionType.WRITE_REQ_DRAFT
        }
        return action_type in allowed_actions
    
    def get_system_prompt(self) -> str:
        """Obtém o prompt do sistema para o Agente Collector."""
        return """Você é um coletor de requisitos experiente em um processo de engenharia de software. Seu papel é:

1. Analisar user stories e requisitos iniciais para identificar lacunas e ambiguidades
2. Propor perguntas estratégicas que ajudem a esclarecer e refinar requisitos
3. Escrever rascunhos de requisitos abrangentes baseados em informações coletadas
4. Garantir que os requisitos sejam completos, claros e acionáveis

Diretrizes para questionamento:
- Faça perguntas específicas e direcionadas que abordem lacunas no entendimento
- Foque em esclarecer requisitos funcionais e não-funcionais
- Identifique casos extremos e cenários excepcionais
- Explore fluxos de trabalho do usuário e processos de negócio
- Esclareça requisitos de dados e interfaces do sistema

Diretrizes para rascunhos de requisitos:
- Escreva declarações de requisitos claras e não ambíguas
- Use formato estruturado com identificadores únicos
- Inclua critérios de aceitação quando apropriado
- Organize requisitos logicamente por funcionalidade ou componente
- Garanta rastreabilidade às user stories originais

Seu objetivo é transformar necessidades de alto nível dos usuários em requisitos detalhados e implementáveis."""
    
    def _execute_specific_action(
        self, 
        action_type: ActionType, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa uma implementação de ação específica."""
        
        if action_type == ActionType.PROPOSE_QUESTION:
            return self._propose_question(input_data)
        elif action_type == ActionType.WRITE_REQ_DRAFT:
            return self._write_req_draft(input_data)
        else:
            raise ValueError(f"Tipo de ação não suportado: {action_type}")
    
    def _propose_question(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Propõe perguntas para esclarecer requisitos.
        
        Args:
            input_data: Deve conter 'user_stories' ou 'requirements'
            
        Returns:
            Dicionário contendo perguntas propostas
        """
        user_stories = input_data.get('user_stories', '')
        requirements = input_data.get('requirements', '')
        domain = input_data.get('domain', 'sistema de software geral')
        focus_area = input_data.get('focus_area', 'geral')
        
        prompt_template = """Analise as seguintes user stories e requisitos para identificar áreas que precisam de esclarecimento. Proponha perguntas específicas e estratégicas que ajudem a refinar e completar os requisitos.

User Stories: {user_stories}
Requisitos Atuais: {requirements}
Domínio: {domain}
Área de Foco: {focus_area}

Por favor forneça:
1. 3-5 perguntas específicas que abordem as lacunas ou ambiguidades mais importantes
2. Para cada pergunta, explique por que é importante e que informação ajudará a esclarecer
3. Priorize perguntas que terão maior impacto no design e implementação do sistema
4. Considere requisitos funcionais, requisitos não-funcionais, restrições e casos extremos

Formate sua resposta como:
Pergunta 1: [pergunta]
Justificativa: [por que esta pergunta é importante]

Pergunta 2: [pergunta]
Justificativa: [por que esta pergunta é importante]

etc."""
        
        prompt = self._format_prompt(prompt_template, {
            'user_stories': user_stories,
            'requirements': requirements,
            'domain': domain,
            'focus_area': focus_area
        })
        
        response = self._generate_response(prompt)
        
        return {
            'questions': response,
            'focus_area': focus_area,
            'analysis_basis': 'user_stories_and_requirements',
            'question_count': self._extract_question_count(response)
        }
    
    def _write_req_draft(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Escreve rascunhos de requisitos baseados nas informações coletadas.
        
        Args:
            input_data: Deve conter 'user_stories', 'qa_pairs', etc.
            
        Returns:
            Dicionário contendo rascunho de requisitos
        """
        user_stories = input_data.get('user_stories', '')
        qa_pairs = input_data.get('qa_pairs', '')
        domain = input_data.get('domain', 'sistema de software geral')
        additional_context = input_data.get('additional_context', '')
        
        prompt_template = """Com base nas user stories e pares de pergunta-resposta, escreva um rascunho abrangente de requisitos. Transforme as necessidades de alto nível em requisitos detalhados e implementáveis.

User Stories: {user_stories}

Pares Pergunta-Resposta: {qa_pairs}

Domínio: {domain}

Contexto Adicional: {additional_context}

Por favor forneça:
1. Requisitos Funcionais (numerados RF-001, RF-002, etc.)
   - Declarações de requisitos claras e testáveis
   - Critérios de aceitação para cada requisito
   - Nível de prioridade (Alta/Média/Baixa)

2. Requisitos Não-Funcionais (numerados RNF-001, RNF-002, etc.)
   - Performance, segurança, usabilidade, etc.
   - Critérios mensuráveis quando possível

3. Restrições e Suposições do Sistema
   - Restrições técnicas
   - Restrições de negócio
   - Principais suposições feitas

4. Requisitos de Dados
   - Principais entidades de dados e atributos
   - Regras de validação de dados
   - Relacionamentos de dados

Formate cada requisito claramente com:
- ID único
- Título
- Descrição
- Critérios de Aceitação
- Prioridade
- Origem (de qual user story ou Q&A deriva)"""
        
        prompt = self._format_prompt(prompt_template, {
            'user_stories': user_stories,
            'qa_pairs': qa_pairs,
            'domain': domain,
            'additional_context': additional_context
        })
        
        response = self._generate_response(prompt)
        
        return {
            'requirements_draft': response,
            'domain': domain,
            'source_stories': user_stories,
            'qa_basis': qa_pairs,
            'draft_type': 'comprehensive_requirements'
        }
    
    def _extract_question_count(self, questions_text: str) -> int:
        """Extract the number of questions from the response."""
        # Simple heuristic to count questions
        return questions_text.count('Question ')
    
    def analyze_and_question(
        self, 
        user_stories: str, 
        domain: str = "general software system",
        focus_area: str = "general"
    ) -> Dict[str, Any]:
        """
        Convenience method to analyze user stories and propose questions.
        
        Args:
            user_stories: User stories to analyze
            domain: Domain context
            focus_area: Specific area to focus on
            
        Returns:
            Action result with proposed questions
        """
        action = self.execute_action(
            ActionType.PROPOSE_QUESTION,
            {
                'user_stories': user_stories,
                'domain': domain,
                'focus_area': focus_area
            }
        )
        return action.output_data
    
    def draft_requirements(
        self, 
        user_stories: str,
        qa_pairs: str = "",
        domain: str = "general software system",
        additional_context: str = ""
    ) -> Dict[str, Any]:
        """
        Convenience method to draft requirements.
        
        Args:
            user_stories: Source user stories
            qa_pairs: Question-answer pairs for clarification
            domain: Domain context
            additional_context: Any additional context
            
        Returns:
            Action result with requirements draft
        """
        action = self.execute_action(
            ActionType.WRITE_REQ_DRAFT,
            {
                'user_stories': user_stories,
                'qa_pairs': qa_pairs,
                'domain': domain,
                'additional_context': additional_context
            }
        )
        return action.output_data

