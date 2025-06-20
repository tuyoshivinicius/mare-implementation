ATORES:

1. Nome: Usuário Primário
   - Tipo: Ator
   - Descrição: O principal usuário do sistema, que cria, visualiza e recebe notificações sobre tarefas.
   - Atributos: Nome do usuário, senha, email.
   - Papel: Cria e gerencia tarefas, recebe notificações de tarefas próximas ao vencimento.

OBJETOS DE DADOS:

1. Nome: Tarefa
   - Tipo: Objeto de Dados
   - Descrição: Representa uma tarefa criada pelo usuário primário.
   - Atributos: ID, Título, Descrição, Data de Vencimento, Prioridade, Responsável, Categoria, Status.
   - Restrições: Título e Data de Vencimento são campos obrigatórios. Prioridade deve ser um valor válido. Data de Vencimento não pode ser no passado.

PROCESSOS:

1. Nome: Visualização de Tarefas
   - Tipo: Processo
   - Descrição: Processo que permite ao usuário visualizar todas as suas tarefas.
   - Entradas: Solicitação do usuário.
   - Saídas: Lista de tarefas com informações básicas e opção de detalhes.
   - Gatilhos: Quando o usuário acessa a lista de tarefas.

2. Nome: Adição de Detalhes às Tarefas
   - Tipo: Processo
   - Descrição: Processo que permite ao usuário adicionar detalhes às tarefas.
   - Entradas: Informações de tarefas fornecidas pelo usuário.
   - Saídas: Tarefa atualizada com novos detalhes.
   - Gatilhos: Quando o usuário escolhe editar uma tarefa.

3. Nome: Notificações de Tarefas Próximas do Vencimento
   - Tipo: Processo
   - Descrição: Processo que envia notificações para o usuário sobre tarefas próximas da data de vencimento.
   - Entradas: Configurações de notificação, lista de tarefas.
   - Saídas: Notificações de tarefas.
   - Gatilhos: Quando uma tarefa está próxima do vencimento.

COMPONENTES DO SISTEMA:

1. Nome: Sistema de Gerenciamento de Tarefas
   - Tipo: Componente do Sistema
   - Descrição: Sistema que permite ao usuário criar, visualizar e receber notificações sobre tarefas.
   - Responsabilidades: Manter a segurança dos dados do usuário, garantir o desempenho responsivo e eficiente do sistema.
   - Interfaces: Interface de usuário para criação e visualização de tarefas, interface de notificação para enviar alertas ao usuário.