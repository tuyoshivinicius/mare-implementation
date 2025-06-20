RELACIONAMENTOS DE ASSOCIAÇÃO:

1. Entidade Origem: Usuário Primário
   - Entidade Destino: Tarefa
   - Tipo de Relacionamento: Associação
   - Nome do Relacionamento: "cria"
   - Cardinalidade: 1:muitos
   - Descrição: O usuário primário cria várias tarefas.

2. Entidade Origem: Usuário Primário
   - Entidade Destino: Tarefa
   - Tipo de Relacionamento: Associação
   - Nome do Relacionamento: "visualiza"
   - Cardinalidade: 1:muitos
   - Descrição: O usuário primário visualiza várias tarefas.

3. Entidade Origem: Usuário Primário
   - Entidade Destino: Sistema de Gerenciamento de Tarefas
   - Tipo de Relacionamento: Associação
   - Nome do Relacionamento: "interage com"
   - Cardinalidade: 1:1
   - Descrição: O usuário primário interage com o sistema de gerenciamento de tarefas.

RELACIONAMENTOS DE COMPOSIÇÃO:

1. Entidade Origem: Sistema de Gerenciamento de Tarefas
   - Entidade Destino: Tarefa
   - Tipo de Relacionamento: Composição
   - Nome do Relacionamento: "contém"
   - Cardinalidade: 1:muitos
   - Descrição: O sistema de gerenciamento de tarefas contém várias tarefas.

RELACIONAMENTOS DE DEPENDÊNCIA:

1. Entidade Origem: Notificações de Tarefas Próximas do Vencimento
   - Entidade Destino: Tarefa
   - Tipo de Relacionamento: Dependência
   - Nome do Relacionamento: "depende de"
   - Força: Forte
   - Descrição: O processo de notificações de tarefas próximas do vencimento depende das tarefas existentes.

2. Entidade Origem: Adição de Detalhes às Tarefas
   - Entidade Destino: Tarefa
   - Tipo de Relacionamento: Dependência
   - Nome do Relacionamento: "modifica"
   - Força: Forte
   - Descrição: O processo de adição de detalhes às tarefas modifica a entidade tarefa.

RELACIONAMENTOS DE FLUXO:

1. Entidade Origem: Usuário Primário
   - Entidade Destino: Visualização de Tarefas
   - Tipo de Relacionamento: Fluxo
   - Tipo de Fluxo: Controle
   - Conteúdo do Fluxo: Solicitação de visualização de tarefas
   - Direção: Unidirecional
   - Descrição: O usuário primário envia uma solicitação para visualizar tarefas, iniciando o processo de visualização de tarefas.

2. Entidade Origem: Notificações de Tarefas Próximas do Vencimento
   - Entidade Destino: Usuário Primário
   - Tipo de Relacionamento: Fluxo
   - Tipo de Fluxo: Mensagem
   - Conteúdo do Fluxo: Notificações de tarefas
   - Direção: Unidirecional
   - Descrição: O processo de notificações de tarefas próximas do vencimento envia notificações para o usuário primário.