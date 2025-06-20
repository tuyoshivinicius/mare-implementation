1. RELACIONAMENTOS DE ASSOCIAÇÃO
- Entidade Origem: Usuário Comum
- Entidade Destino: Tarefa
- Tipo de Relacionamento: Associação
- Nome do Relacionamento: cria
- Cardinalidade: 1:muitos
- Descrição: Um usuário comum pode criar várias tarefas

- Entidade Origem: Administrador
- Entidade Destino: Tarefa
- Tipo de Relacionamento: Associação
- Nome do Relacionamento: atribui
- Cardinalidade: 1:muitos
- Descrição: Um administrador pode atribuir várias tarefas aos usuários

2. RELACIONAMENTOS DE COMPOSIÇÃO
- Entidade Origem: Módulo de Gerenciamento de Tarefas
- Entidade Destino: Tarefa
- Tipo de Relacionamento: Composição
- Nome do Relacionamento: contém
- Cardinalidade: 1:muitos
- Descrição: O Módulo de Gerenciamento de Tarefas contém várias tarefas

3. RELACIONAMENTOS DE DEPENDÊNCIA
- Entidade Origem: Módulo de Segurança de Dados
- Entidade Destino: Tarefa
- Tipo de Relacionamento: Dependência
- Nome do Relacionamento: protege
- Força: forte
- Descrição: O Módulo de Segurança de Dados protege os dados das tarefas

4. RELACIONAMENTOS DE HERANÇA
- Nenhum relacionamento de herança relevante identificado a partir dos requisitos

5. RELACIONAMENTOS DE FLUXO
- Entidade Origem: Usuário Comum
- Entidade Destino: Criação de Tarefa
- Tipo de Relacionamento: Fluxo
- Tipo de Fluxo: controle
- Conteúdo do Fluxo: Comando para criar tarefa
- Direção: unidirecional
- Descrição: O Usuário Comum envia um comando para o processo de Criação de Tarefa

- Entidade Origem: Administrador
- Entidade Destino: Atribuição de Tarefa
- Tipo de Relacionamento: Fluxo
- Tipo de Fluxo: controle
- Conteúdo do Fluxo: Comando para atribuir tarefa
- Direção: unidirecional
- Descrição: O Administrador envia um comando para o processo de Atribuição de Tarefa