"""
MARE CLI - Implementação do Agente Modeler
Agente responsável por extrair entidades e relacionamentos dos requisitos
"""

from typing import Any, Dict, List
from mare.agents.base import AbstractAgent, AgentRole, ActionType, AgentConfig


class ModelerAgent(AbstractAgent):
    """
    Implementação do Agente Modeler.
    
    Este agente é responsável por:
    - Extrair entidades dos requisitos (ExtractEntity)
    - Extrair relacionamentos entre entidades (ExtractRelation)
    """
    
    def __init__(self, config: AgentConfig):
        """Inicializa o Agente Modeler."""
        # Garante que o papel está definido corretamente
        config.role = AgentRole.MODELER
        
        # Define prompt do sistema padrão se não fornecido
        if not config.system_prompt:
            config.system_prompt = self.get_system_prompt()
        
        super().__init__(config)
    
    def can_perform_action(self, action_type: ActionType) -> bool:
        """Verifica se este agente pode executar a ação especificada."""
        allowed_actions = {
            ActionType.EXTRACT_ENTITY,
            ActionType.EXTRACT_RELATION
        }
        return action_type in allowed_actions
    
    def get_system_prompt(self) -> str:
        """Obtém o prompt do sistema para o Agente Modeler."""
        return """Você é um modelador de requisitos experiente especializado em extrair informações estruturadas de documentos de requisitos. Seu papel é:

1. Identificar e extrair entidades-chave (atores, sistemas, objetos de dados, processos) dos requisitos
2. Determinar relacionamentos entre entidades (associações, dependências, composições)
3. Criar modelos estruturados que representem a arquitetura conceitual do sistema
4. Garantir completude e consistência no modelo extraído

Diretrizes para extração de entidades:
- Identifique diferentes tipos de entidades: Atores (usuários, sistemas externos), Objetos de Dados (entidades, arquivos, bancos de dados), Processos (funções, serviços, fluxos de trabalho), Componentes do Sistema
- Para cada entidade, determine: Nome, Tipo, Descrição, Atributos, Restrições
- Considere tanto entidades explícitas mencionadas nos requisitos quanto implícitas que são necessárias

Diretrizes para extração de relacionamentos:
- Identifique tipos de relacionamento: Associação (usa, interage com), Composição (contém, consiste de), Dependência (depende de, requer), Herança (é um tipo de), Fluxo (fluxo de dados, fluxo de controle)
- Para cada relacionamento, especifique: Entidade origem, Entidade destino, Tipo de relacionamento, Cardinalidade, Descrição
- Considere tanto relacionamentos diretos quanto relacionamentos derivados

Sua saída deve ser estruturada, precisa e adequada para criar modelos e diagramas do sistema."""
    
    def _execute_specific_action(
        self, 
        action_type: ActionType, 
        input_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a specific action implementation."""
        
        if action_type == ActionType.EXTRACT_ENTITY:
            return self._extract_entity(input_data)
        elif action_type == ActionType.EXTRACT_RELATION:
            return self._extract_relation(input_data)
        else:
            raise ValueError(f"Unsupported action type: {action_type}")
    
    def _extract_entity(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract entities from requirements.
        
        Args:
            input_data: Should contain 'requirements_draft' or 'requirements'
            
        Returns:
            Dictionary containing extracted entities
        """
        requirements = input_data.get('requirements_draft', input_data.get('requirements', ''))
        domain = input_data.get('domain', 'general software system')
        focus_type = input_data.get('focus_type', 'all')  # all, actors, data, processes, systems
        
        prompt_template = """Analise os seguintes requisitos e extraia todas as entidades relevantes. Foque em identificar os componentes-chave que farão parte do modelo do sistema.

Requisitos: {requirements}
Domínio: {domain}
Tipo de Foco: {focus_type}

Por favor extraia entidades nas seguintes categorias:

1. ATORES (Usuários, Sistemas Externos, Stakeholders)
   - Nome: [nome da entidade]
   - Tipo: Ator
   - Descrição: [breve descrição]
   - Atributos: [características principais]
   - Papel: [o que fazem no sistema]

2. OBJETOS DE DADOS (Entidades, Arquivos, Bancos de Dados, Informações)
   - Nome: [nome da entidade]
   - Tipo: Objeto de Dados
   - Descrição: [o que representa]
   - Atributos: [campos/propriedades principais de dados]
   - Restrições: [regras de validação, regras de negócio]

3. PROCESSOS (Funções, Serviços, Fluxos de Trabalho, Operações)
   - Nome: [nome da entidade]
   - Tipo: Processo
   - Descrição: [o que faz]
   - Entradas: [o que recebe como entrada]
   - Saídas: [o que produz]
   - Gatilhos: [o que o inicia]

4. COMPONENTES DO SISTEMA (Módulos, Serviços, Interfaces)
   - Nome: [nome da entidade]
   - Tipo: Componente do Sistema
   - Descrição: [seu propósito e funcionalidade]
   - Responsabilidades: [pelo que é responsável]
   - Interfaces: [como se conecta a outros componentes]

Para cada entidade, certifique-se de fornecer:
- Um nome único e descritivo
- Categorização clara
- Descrição abrangente
- Atributos ou propriedades relevantes
- Quaisquer restrições ou regras de negócio

Foque em entidades que são essenciais para entender e implementar o sistema."""
        
        prompt = self._format_prompt(prompt_template, {
            'requirements': requirements,
            'domain': domain,
            'focus_type': focus_type
        })
        
        response = self._generate_response(prompt)
        
        return {
            'entities': response,
            'domain': domain,
            'focus_type': focus_type,
            'extraction_basis': 'requirements_analysis',
            'entity_categories': ['actors', 'data_objects', 'processes', 'system_components']
        }
    
    def _extract_relation(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extrai relacionamentos entre entidades.
        
        Args:
            input_data: Deve conter 'entities' e 'requirements'
            
        Returns:
            Dicionário contendo relacionamentos extraídos
        """
        entities = input_data.get('entities', '')
        requirements = input_data.get('requirements', '')
        domain = input_data.get('domain', 'general software system')
        relationship_types = input_data.get('relationship_types', 'all')
        
        prompt_template = """Com base nas entidades extraídas e requisitos, identifique e extraia relacionamentos entre entidades. Foque em criar um modelo de relacionamento abrangente.

Entidades Extraídas: {entities}

Requisitos: {requirements}

Domínio: {domain}

Tipos de Relacionamento para Focar: {relationship_types}

Por favor identifique relacionamentos nas seguintes categorias:

1. RELACIONAMENTOS DE ASSOCIAÇÃO (usa, interage com, acessa)
   - Entidade Origem: [nome da entidade]
   - Entidade Destino: [nome da entidade]
   - Tipo de Relacionamento: Associação
   - Nome do Relacionamento: [relacionamento específico, ex: "usa", "gerencia", "visualiza"]
   - Cardinalidade: [1:1, 1:muitos, muitos:muitos]
   - Descrição: [como estão relacionados]

2. RELACIONAMENTOS DE COMPOSIÇÃO (contém, consiste de, inclui)
   - Entidade Origem: [entidade contêiner]
   - Entidade Destino: [entidade contida]
   - Tipo de Relacionamento: Composição
   - Nome do Relacionamento: [ex: "contém", "inclui"]
   - Cardinalidade: [quantos do destino na origem]
   - Descrição: [natureza da contenção]

3. RELACIONAMENTOS DE DEPENDÊNCIA (depende de, requer, precisa)
   - Entidade Origem: [entidade dependente]
   - Entidade Destino: [entidade de dependência]
   - Tipo de Relacionamento: Dependência
   - Nome do Relacionamento: [ex: "depende de", "requer"]
   - Força: [forte, fraca]
   - Descrição: [natureza da dependência]

4. RELACIONAMENTOS DE HERANÇA (é um tipo de, especializa)
   - Entidade Origem: [entidade especializada]
   - Entidade Destino: [entidade geral]
   - Tipo de Relacionamento: Herança
   - Nome do Relacionamento: "é um tipo de"
   - Descrição: [como origem especializa destino]

5. RELACIONAMENTOS DE FLUXO (fluxo de dados, fluxo de controle, comunicação)
   - Entidade Origem: [origem]
   - Entidade Destino: [destino]
   - Tipo de Relacionamento: Fluxo
   - Tipo de Fluxo: [dados, controle, mensagem]
   - Conteúdo do Fluxo: [o que flui entre eles]
   - Direção: [unidirecional, bidirecional]

Para cada relacionamento, forneça:
- Identificação clara das entidades origem e destino
- Tipo e nome específico do relacionamento
- Cardinalidade ou multiplicidade quando aplicável
- Descrição da natureza e propósito do relacionamento
- Quaisquer restrições ou condições no relacionamento

Garanta que os relacionamentos sejam consistentes com os requisitos e façam sentido lógico no contexto do domínio."""
        
        prompt = self._format_prompt(prompt_template, {
            'entities': entities,
            'requirements': requirements,
            'domain': domain,
            'relationship_types': relationship_types
        })
        
        response = self._generate_response(prompt)
        
        return {
            'relationships': response,
            'domain': domain,
            'relationship_types': relationship_types,
            'source_entities': entities,
            'relationship_categories': ['association', 'composition', 'dependency', 'inheritance', 'flow']
        }
    
    def extract_system_entities(
        self, 
        requirements: str, 
        domain: str = "general software system",
        focus_type: str = "all"
    ) -> Dict[str, Any]:
        """
        Convenience method to extract entities from requirements.
        
        Args:
            requirements: Requirements text to analyze
            domain: Domain context
            focus_type: Type of entities to focus on
            
        Returns:
            Action result with extracted entities
        """
        action = self.execute_action(
            ActionType.EXTRACT_ENTITY,
            {
                'requirements': requirements,
                'domain': domain,
                'focus_type': focus_type
            }
        )
        return action.output_data
    
    def extract_entity_relationships(
        self, 
        entities: str,
        requirements: str,
        domain: str = "general software system",
        relationship_types: str = "all"
    ) -> Dict[str, Any]:
        """
        Convenience method to extract relationships between entities.
        
        Args:
            entities: Previously extracted entities
            requirements: Source requirements
            domain: Domain context
            relationship_types: Types of relationships to focus on
            
        Returns:
            Action result with extracted relationships
        """
        action = self.execute_action(
            ActionType.EXTRACT_RELATION,
            {
                'entities': entities,
                'requirements': requirements,
                'domain': domain,
                'relationship_types': relationship_types
            }
        )
        return action.output_data
    
    def create_complete_model(
        self, 
        requirements: str, 
        domain: str = "general software system"
    ) -> Dict[str, Any]:
        """
        Create a complete model by extracting both entities and relationships.
        
        Args:
            requirements: Requirements to model
            domain: Domain context
            
        Returns:
            Dictionary with both entities and relationships
        """
        # First extract entities
        entities_result = self.extract_system_entities(requirements, domain)
        
        # Then extract relationships based on the entities
        relationships_result = self.extract_entity_relationships(
            entities_result['entities'], 
            requirements, 
            domain
        )
        
        return {
            'entities': entities_result,
            'relationships': relationships_result,
            'domain': domain,
            'model_type': 'complete_system_model'
        }

