Requisitos Funcionais:

RF-001
Título: Criar Tarefa
Descrição: O sistema deve permitir aos usuários comuns criar novas tarefas, inserindo título, descrição e atribuindo uma prioridade.
Critérios de Aceitação:
1. O usuário deve ser capaz de preencher o título e descrição da tarefa.
2. Deve ser possível selecionar a prioridade da tarefa entre alta, média ou baixa.
3. Após a criação, a tarefa deve ser exibida na lista de tarefas do usuário.
Prioridade: Alta
Origem: User Story - Como usuário comum, quero poder atribuir prioridades às tarefas que crio.

RF-002
Título: Atribuir Tarefa a Usuário
Descrição: O administrador deve poder atribuir tarefas a usuários específicos, definindo claramente o responsável por cada tarefa.
Critérios de Aceitação:
1. O administrador deve poder selecionar um usuário da lista para atribuir a tarefa.
2. Após a atribuição, o responsável pela tarefa deve receber uma notificação.
3. A tarefa atribuída deve ser visível apenas para o usuário responsável e o administrador.
Prioridade: Alta
Origem: User Story - Como administrador, quero ter a capacidade de atribuir tarefas a usuários específicos.

Requisitos Não-Funcionais:

RNF-001
Título: Segurança dos Dados
Descrição: O sistema deve garantir a segurança dos dados dos usuários, utilizando criptografia para proteção e realizando backups regulares.
Critérios de Aceitação:
1. Todos os dados dos usuários devem ser armazenados de forma criptografada.
2. Deve haver um procedimento automático de backup diário dos dados do sistema.
3. Acesso aos dados sensíveis deve ser restrito apenas a usuários autorizados.
Prioridade: Alta

Restrições e Suposições do Sistema:

Restrição Técnica: O sistema deve ser desenvolvido utilizando tecnologias que suportem a responsividade em diversos dispositivos, como HTML5 e CSS3.
Restrição de Negócio: O sistema deve cumprir com as regulamentações de proteção de dados vigentes em relação à privacidade dos usuários.
Suposição: Os administradores terão permissões especiais para atribuir e gerenciar tarefas, enquanto os usuários comuns terão acesso restrito a suas próprias tarefas.

Requisitos de Dados:

Entidade: Tarefa
Atributos: ID, Título, Descrição, Prioridade, Data de Criação, Data de Vencimento, Responsável
Regras de Validação: Título obrigatório, Prioridade deve ser uma das opções válidas, Data de Vencimento deve ser futura
Relacionamentos: Uma tarefa pode ter um único responsável, mas um usuário pode ser responsável por várias tarefas.