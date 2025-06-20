Requisitos Funcionais:

RF-001
Título: Visualização de Tarefas
Descrição: O sistema deve permitir que o usuário primário visualize todas as suas tarefas em uma lista, fornecendo uma visão geral do que precisa ser feito.
Critérios de Aceitação: O usuário pode acessar uma lista de tarefas com informações básicas (título, data de vencimento, prioridade) e opção de detalhes.
Prioridade: Alta
Origem: User Story 1

RF-002
Título: Adição de Detalhes às Tarefas
Descrição: O sistema deve possibilitar que o usuário adicione detalhes às tarefas, incluindo data de vencimento, prioridade e descrição.
Critérios de Aceitação: O usuário pode editar uma tarefa para incluir data de vencimento, prioridade e descrição, com validação de campos obrigatórios.
Prioridade: Alta
Origem: User Story 2

RF-003
Título: Notificações de Tarefas Próximas do Vencimento
Descrição: O sistema deve enviar notificações ou lembretes ao usuário primário sobre tarefas próximas da data de vencimento.
Critérios de Aceitação: O usuário recebe notificações em tempo hábil (configurável) sobre tarefas com prazo próximo, com opção de visualizar detalhes da tarefa.
Prioridade: Alta
Origem: User Story 3

Requisitos Não-Funcionais:

RNF-001
Título: Segurança de Dados
Descrição: O sistema deve garantir a segurança dos dados dos usuários, protegendo informações confidenciais e pessoais.
Critérios: Todos os dados do sistema devem ser criptografados em repouso e em trânsito.
Prioridade: Alta

RNF-002
Título: Desempenho do Sistema
Descrição: O sistema deve ter um desempenho responsivo e eficiente, mesmo com um grande volume de tarefas e usuários.
Critérios: O tempo de resposta para a visualização de tarefas e notificações deve ser inferior a 2 segundos, independentemente da carga do sistema.
Prioridade: Alta

Restrições e Suposições do Sistema:

- Restrição Técnica: O sistema será desenvolvido utilizando tecnologias web e mobile.
- Restrição de Negócio: O sistema deve estar em conformidade com regulamentações de proteção de dados.
- Suposição: Os usuários terão conexão com a internet para receber notificações e atualizar tarefas em tempo real.

Requisitos de Dados:

Entidade: Tarefa
Atributos: ID, Título, Descrição, Data de Vencimento, Prioridade, Responsável, Categoria, Status
Regras de Validação: Título e Data de Vencimento obrigatórios; Prioridade deve ser um valor válido; Data de Vencimento não pode ser no passado.
Relacionamentos: Uma tarefa pode ter um ou mais responsáveis atribuídos.