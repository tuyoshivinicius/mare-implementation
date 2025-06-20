"""
MARE CLI - Implementação do Agente Stakeholder
Agente responsável por expressar necessidades dos stakeholders e responder perguntas
"""

from typing import Any, Dict, List
from mare.agents.base import AbstractAgent, AgentRole, ActionType, AgentConfig


class StakeholderAgent(AbstractAgent):
    """
    Implementação do Agente Stakeholder.
    
    Este agente representa stakeholders e é responsável por:
    - Expressar user stories e requisitos (SpeakUserStories)
    - Responder perguntas de outros agentes (AnswerQuestion)
    """
    
    def __init__(self, config: AgentConfig):
        """Inicializa o Agente Stakeholder."""
        # Garante que o papel está definido corretamente
        config.role = AgentRole.STAKEHOLDER
        
        # Define prompt do sistema padrão se não fornecido
        if not config.system_prompt:
            config.system_prompt = self.get_system_prompt()
        
        super().__init__(config)
    
    def can_perform_action(self, action_type: ActionType) -> bool:
        """Verifica se este agente pode executar a ação especificada."""
        allowed_actions = {
            ActionType.SPEAK_USER_STORIES,
            ActionType.ANSWER_QUESTION
        }
        return action_type in allowed_actions
    
    def get_system_prompt(self) -> str:
        """Obtém o prompt do sistema para o Agente Stakeholder."""
        return """Você é um representante experiente de stakeholders em um processo de engenharia de requisitos de software. Seu papel é:

1. Expressar necessidades e requisitos dos usuários de forma clara e abrangente
2. Fornecer user stories detalhadas que capturem a essência do que os usuários desejam
3. Responder perguntas de outros membros da equipe para esclarecer requisitos
4. Pensar na perspectiva dos usuários finais e stakeholders do negócio

Diretrizes:
- Seja específico e detalhado em suas descrições
- Considere diferentes tipos de usuários e suas necessidades variadas
- Inclua requisitos funcionais e não-funcionais quando relevante
- Forneça contexto e justificativa para suas declarações
- Seja consistente com requisitos previamente declarados"""
    
    def _execute_specific_action(
        self, 
        action_type: ActionType, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executa uma ação específica do agente."""
        if action_type == ActionType.SPEAK_USER_STORIES:
            return self._speak_user_stories(input_data)
        elif action_type == ActionType.ANSWER_QUESTION:
            return self._answer_question(input_data)
        else:
            raise ValueError(f"Ação não suportada: {action_type}")
    
    def _speak_user_stories(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Expressa user stories baseadas na ideia do sistema e requisitos iniciais.
        
        Args:
            input_data: Deve conter 'system_idea' e opcionalmente 'rough_requirements' e 'domain'
            
        Returns:
            Dicionário contendo user stories e metadados
        """
        system_idea = input_data.get('system_idea', '')
        rough_requirements = input_data.get('rough_requirements', '')
        domain = input_data.get('domain', 'sistema de software geral')
        
        prompt_template = """Com base na seguinte ideia de sistema e requisitos, por favor expresse user stories detalhadas que capturem o que stakeholders e usuários finais precisam deste sistema.

Ideia do Sistema: {system_idea}
Requisitos Iniciais: {rough_requirements}
Domínio: {domain}

Por favor forneça:
1. Um conjunto de user stories abrangentes no formato "Como [tipo de usuário], eu quero [objetivo] para que [benefício]"
2. Inclua diferentes tipos de usuários (usuários primários, administradores, etc.)
3. Cubra aspectos funcionais e não-funcionais quando relevante
4. Forneça contexto e justificativa para cada story

Foque em ser específico, acionável e centrado no usuário. Considere a jornada completa do usuário e diferentes cenários."""
        
        prompt = self._format_prompt(prompt_template, {
            'system_idea': system_idea,
            'rough_requirements': rough_requirements,
            'domain': domain
        })
        
        response = self._generate_response(prompt)
        
        return {
            'user_stories': response,
            'system_idea': system_idea,
            'domain': domain,
            'stakeholder_perspective': 'primary_stakeholder'
        }
    
    def _answer_question(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Responde perguntas de outros agentes para esclarecer requisitos.
        
        Args:
            input_data: Deve conter 'question' e opcionalmente 'context'
            
        Returns:
            Dicionário contendo a resposta
        """
        question = input_data.get('question', '')
        context = input_data.get('context', '')
        previous_stories = input_data.get('previous_stories', '')
        
        if not question:
            raise ValueError("Pergunta é obrigatória para a ação AnswerQuestion")
        
        prompt_template = """Você está sendo questionado para esclarecer requisitos do sistema. Por favor forneça uma resposta detalhada e útil baseada em seu entendimento das necessidades dos stakeholders.

Pergunta: {question}

Contexto: {context}

User Stories/Requisitos Anteriores: {previous_stories}

Por favor forneça:
1. Uma resposta clara e direta à pergunta
2. Contexto adicional ou detalhes que possam ser úteis
3. Quaisquer suposições que você esteja fazendo
4. Requisitos relacionados ou considerações que possam ser relevantes

Seja específico e garanta que sua resposta seja consistente com quaisquer requisitos previamente declarados."""
        
        prompt = self._format_prompt(prompt_template, {
            'question': question,
            'context': context,
            'previous_stories': previous_stories
        })
        
        response = self._generate_response(prompt)
        
        return {
            'answer': response,
            'question': question,
            'context': context,
            'stakeholder_perspective': 'clarification_provided'
        }
    
    def express_initial_requirements(
        self, 
        system_idea: str, 
        domain: str = "general software system"
    ) -> Dict[str, Any]:
        """
        Convenience method to express initial requirements.
        
        Args:
            system_idea: High-level description of the system
            domain: Domain or industry context
            
        Returns:
            Action result with user stories
        """
        action = self.execute_action(
            ActionType.SPEAK_USER_STORIES,
            {
                'system_idea': system_idea,
                'domain': domain
            }
        )
        return action.output_data
    
    def respond_to_question(
        self, 
        question: str, 
        context: str = "",
        previous_stories: str = ""
    ) -> Dict[str, Any]:
        """
        Convenience method to respond to questions.
        
        Args:
            question: The question to answer
            context: Additional context for the question
            previous_stories: Previously stated requirements/stories
            
        Returns:
            Action result with answer
        """
        action = self.execute_action(
            ActionType.ANSWER_QUESTION,
            {
                'question': question,
                'context': context,
                'previous_stories': previous_stories
            }
        )
        return action.output_data

