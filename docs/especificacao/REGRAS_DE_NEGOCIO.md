# Regras de Negócio (RN) — SGOS

## RN001 — Exclusão de cliente com OS ativa
Um cliente não pode ser excluído se possuir ordem de serviço com status diferente de `encerrada`.

## RN002 — Cliente obrigatório na abertura de OS
Toda ordem de serviço deve estar vinculada a um cliente existente.

## RN003 — Status inicial e data de abertura
Toda OS nasce com status `aberta` e a data de abertura (`aberta_em`) é registrada pelo sistema.

## RN004 — Workflow de status sem retroceder
A OS só pode avançar seguindo a sequência:
`aberta → aguardando → em_andamento → em_avaliacao → encerrada`.
Não é permitido retroceder status.

## RN005 — Autenticação obrigatória
Todas as rotas da API exigem autenticação via JWT, exceto:
- `/api/auth/register/`
- `/api/auth/login/`

## RN006 — Restrições para OS encerrada
Uma OS com status `encerrada`:
- não pode ser editada
- não pode receber iterações
- não pode receber anexos
Somente OS encerrada pode ser excluída.

## RN007 — Identidade única de usuário
O campo `username` deve ser único.

## RN008 — Departamento obrigatório na OS
Toda OS deve possuir um `departamento` e ele deve ser um único departamento por OS.

## RN009 — Visibilidade por departamento (técnicos)
Usuários não-admin:
- só visualizam OS do próprio departamento
- só podem acessar detalhes de OS do próprio departamento

## RN010 — Abertura de OS por departamento (técnicos)
Usuários não-admin só podem criar OS no próprio departamento.

## RN011 — Atribuição de técnico
- A OS pode ter um técnico atribuído (`atribuido_para`).
- Ao entrar em `em_andamento`, se não houver técnico atribuído e o usuário não for admin, a OS é atribuída automaticamente ao usuário que executou o avanço.
- Atribuições devem respeitar o departamento: o técnico atribuído deve pertencer ao mesmo departamento da OS.

## RN012 — Descrição do serviço ao sair de Em Andamento
Para avançar uma OS quando ela está em `em_andamento`, é obrigatória a descrição do serviço executado (registrada em `observacao` no histórico de status).

## RN013 — Administração de técnicos
A gestão de técnicos (listar/criar/ativar/desativar) é restrita a usuários admin (superuser).

