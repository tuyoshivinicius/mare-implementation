1. ATORES
- Nome: Usuário Comum
  - Tipo: Ator
  - Descrição: Usuário com permissões padrão no sistema
  - Atributos: ID de usuário, nome, email
  - Papel: Cria tarefas, visualiza suas próprias tarefas

- Nome: Administrador
  - Tipo: Ator
  - Descrição: Usuário com permissões avançadas no sistema
  - Atributos: ID de administrador, nome, email
  - Papel: Atribui tarefas a usuários, gerencia todas as tarefas, tem acesso a todos os dados de tarefas

2. OBJETOS DE DADOS
- Nome: Tarefa
  - Tipo: Objeto de Dados
  - Descrição: Representa uma tarefa atribuída a um usuário
  - Atributos: ID, Título, Descrição, Prioridade, Data de Criação, Data de Vencimento, Responsável
  - Restrições: Título obrigatório, Prioridade deve ser alta, média ou baixa, Data de Vencimento deve ser futura

3. PROCESSOS
- Nome: Criação de Tarefa
  - Tipo: Processo
  - Descrição: Permite aos usuários criar novas tarefas
  - Entradas: Título, Descrição, Prioridade
  - Saídas: Tarefa criada
  - Gatilhos: Ação do usuário para criar uma tarefa

- Nome: Atribuição de Tarefa
  - Tipo: Processo
  - Descrição: Permite ao administrador atribuir tarefas a usuários
  - Entradas: Tarefa, Usuário
  - Saídas: Tarefa atribuída
  - Gatilhos: Ação do administrador para atribuir uma tarefa

4. COMPONENTES DO SISTEMA
- Nome: Módulo de Gerenciamento de Tarefas
  - Tipo: Componente do Sistema
  - Descrição: Gerencia a criação, atribuição e visualização de tarefas
  - Responsabilidades: Manter a integridade e segurança das tarefas
  - Interfaces: Interface de usuário para criação e visualização de tarefas, Interface administrativa para atribuição de tarefas

- Nome: Módulo de Segurança de Dados
  - Tipo: Componente do Sistema
  - Descrição: Protege os dados dos usuários e realiza backups regulares
  - Responsabilidades: Criptografia de dados, restrição de acesso, backup de dados
  - Interfaces: Interface com o banco de dados