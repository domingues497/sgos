# Requisitos Não Funcionais (RNF) — SGOS

## RNF001 — Segurança (autenticação)
- A API deve exigir autenticação JWT em todas as rotas protegidas.
- Tokens devem expirar e suportar renovação via refresh token.

## RNF002 — Segurança (autorização)
- Operações administrativas devem ser restritas a usuários admin (superuser).
- Usuários não-admin devem acessar apenas dados do próprio departamento.

## RNF003 — Integridade dos dados
- O sistema deve garantir consistência do workflow de status (sem retroceder).
- O sistema deve garantir que OS tenha departamento obrigatório.

## RNF004 — Usabilidade
- Interface deve permitir operação por Kanban (arrastar/avançar) e por modal.
- Ao sair de “Em Andamento”, o sistema deve solicitar descrição do serviço em interface dedicada.

## RNF005 — Performance
- Listagens devem ser paginadas.
- Consultas devem usar select_related/prefetch_related quando aplicável.

## RNF006 — Compatibilidade
- Frontend deve funcionar em navegadores modernos, sem dependência de build.
- Backend deve funcionar em ambiente Windows (PowerShell/Python).

## RNF007 — Observabilidade
- Erros de API devem retornar mensagens claras e status HTTP apropriado.

## RNF008 — Manutenibilidade
- CSS deve permanecer centralizado em arquivo único.
- Chamadas à API devem ser centralizadas em um único cliente JS.

