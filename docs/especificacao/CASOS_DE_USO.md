# Casos de Uso (UC) — SGOS

## Atores
- Visitante: usuário não autenticado.
- Usuário: autenticado (funcionário/técnico).
- Admin: usuário com permissão administrativa (superuser).

## UC01 — Autenticar
- Ator: Visitante
- Objetivo: Entrar no sistema.
- Fluxo principal:
  1. Informar usuário e senha.
  2. Sistema autentica e armazena tokens JWT.
  3. Sistema carrega dados do usuário.

## UC02 — Cadastrar cliente
- Ator: Usuário
- Objetivo: Criar um novo cliente.
- Pós-condição: Cliente cadastrado.

## UC03 — Abrir chamado (OS)
- Ator: Usuário
- Objetivo: Criar uma OS para um cliente.
- Regras:
  - Departamento é obrigatório.
  - Usuário não-admin só abre OS no próprio departamento.

## UC04 — Visualizar Kanban
- Ator: Usuário
- Objetivo: Acompanhar OS por status e prioridade.
- Regras:
  - Usuário não-admin só visualiza OS do seu departamento.

## UC05 — Avançar status
- Ator: Usuário
- Objetivo: Avançar o status da OS.
- Fluxo principal:
  1. Usuário aciona avanço (botão ou drag-and-drop).
  2. Sistema valida RN004 (não retroceder).
  3. Se status atual for `em_andamento`, sistema solicita descrição do serviço.
  4. Sistema grava histórico e atualiza status.

## UC06 — Atribuir chamado ao técnico
- Ator: Usuário / Admin
- Objetivo: Definir responsável pelo atendimento.
- Regras:
  - Técnico deve ser do mesmo departamento da OS.
  - Usuário (técnico) pode atribuir para si quando permitido.
  - Admin pode atribuir qualquer técnico do mesmo departamento.

## UC07 — Registrar iteração
- Ator: Usuário
- Objetivo: Registrar comentário/evolução na OS.
- Regra: OS encerrada não permite iteração.

## UC08 — Gerenciar técnicos (admin)
- Ator: Admin
- Objetivo: Cadastrar e gerenciar técnicos.
- Fluxo principal:
  1. Admin acessa painel de técnicos.
  2. Admin cadastra novo técnico, define departamento e senha.
  3. Admin ativa/desativa técnico.

## UC09 — Meus Chamados
- Ator: Usuário
- Objetivo: Visualizar trabalho pessoal.
- Funcionalidades:
  - abas Atribuídos / Criados
  - fila de trabalho
  - prioridade do dia
  - KPIs pessoais e histórico recente

