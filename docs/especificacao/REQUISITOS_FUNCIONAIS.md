# Requisitos Funcionais (RF) — SGOS

## RF001 — Cadastro de usuário
O sistema deve permitir cadastro de usuário informando dados pessoais e departamento.

## RF002 — Login (JWT)
O sistema deve permitir autenticação via usuário e senha, retornando tokens JWT (access/refresh).

## RF003 — Logout
O sistema deve permitir logout invalidando o refresh token e removendo credenciais locais.

## RF004 — Cadastrar cliente
O sistema deve permitir cadastrar clientes com nome, email, telefone e endereço.

## RF005 — Editar cliente
O sistema deve permitir editar dados de cliente.

## RF006 — Excluir cliente
O sistema deve permitir excluir cliente, respeitando RN001.

## RF007 — Abrir chamado (criar OS)
O sistema deve permitir abrir uma OS vinculada a um cliente, com:
- título e descrição
- tipo, categoria, prioridade, urgência
- departamento (obrigatório)

## RF008 — Avançar status da OS
O sistema deve permitir avançar o status de uma OS seguindo RN004.

## RF009 — Detalhar OS
O sistema deve permitir consultar uma OS com seus dados, histórico de status, iterações e anexos.

## RF010 — Listar e pesquisar OS
O sistema deve permitir listar OS com paginação e permitir pesquisa por termos e filtros.

## RF011 — Iterações (comentários)
O sistema deve permitir:
- listar iterações de uma OS
- adicionar iteração (se OS não estiver encerrada)

## RF012 — Anexos
O sistema deve permitir enviar anexos para uma OS (se OS não estiver encerrada).

## RF013 — Painel Kanban
O sistema deve exibir um painel Kanban com colunas de status e permitir:
- busca por texto
- filtros por prioridade
- drag-and-drop para avanço de status (respeitando RN004)

## RF014 — Meus Chamados
O sistema deve oferecer uma visão “Meus Chamados” com:
- filtro por chamados atribuídos / criados
- fila de trabalho (top 10)
- prioridade do dia (críticos e altos)
- indicadores pessoais (KPIs)
- histórico recente

## RF015 — Atribuir OS ao técnico
O sistema deve permitir atribuição de técnico à OS:
- técnico atribuir para si (quando permitido)
- admin atribuir a um técnico do mesmo departamento

## RF016 — Gestão de técnicos (admin)
O sistema deve permitir ao admin:
- listar técnicos
- cadastrar técnico
- ativar/desativar técnico

