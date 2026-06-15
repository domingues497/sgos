# Diagramas de Atividade - Base de Fluxos

## Objetivo
Este documento organiza os fluxos que devem ser convertidos em diagramas de atividade.

## Fluxo 1 - Abertura de chamado pelo cliente
### Inicio
Cliente autenticado acessa a tela de abertura.

### Sequencia
1. Sistema identifica o cliente vinculado ao usuario.
2. Sistema exibe formulario reduzido para cliente.
3. Cliente escolhe o departamento de destino.
4. Cliente informa tipo de chamado.
5. Cliente informa categoria / assunto.
6. Cliente informa titulo / resumo.
7. Cliente informa descricao detalhada.
8. Cliente anexa arquivos, se desejar.
9. Sistema valida os dados obrigatorios.
10. Sistema valida que o chamado pertence ao cliente autenticado.
11. Sistema cria a ordem de servico com status `aberta`.
12. Sistema registra historico inicial.
13. Sistema retorna confirmacao de sucesso.

### Decisoes importantes
- cliente vinculado existe?
- departamento foi informado?
- campos obrigatorios foram preenchidos?

### Fim
Chamado criado e disponivel para acompanhamento.

## Fluxo 2 - Abertura de chamado por usuario interno
### Inicio
Administrador ou tecnico autenticado acessa a tela de abertura.

### Sequencia
1. Usuario interno acessa o formulario completo.
2. Usuario seleciona cliente.
3. Usuario informa departamento, tipo, categoria, prioridade e urgencia conforme regras do perfil.
4. Usuario informa titulo e descricao.
5. Usuario anexa arquivos, se desejar.
6. Sistema valida os dados.
7. Sistema cria o chamado.
8. Sistema registra historico inicial.

### Fim
Chamado criado para tratamento operacional.

## Fluxo 3 - Atribuicao de tecnico pelo administrador
### Inicio
Administrador acessa o detalhamento de um chamado.

### Sequencia
1. Sistema exibe os dados do chamado.
2. Administrador escolhe um tecnico.
3. Sistema valida se o tecnico pode ser atribuido.
4. Sistema grava a atribuicao.
5. Sistema atualiza a visualizacao do chamado.

### Decisoes
- chamado existe?
- tecnico selecionado e valido?
- usuario possui permissao de atribuicao?

### Fim
Chamado atribuido.

## Fluxo 4 - Avanco de status do chamado
### Inicio
Administrador ou tecnico executa acao de avancar status.

### Sequencia
1. Sistema recupera o status atual do chamado.
2. Sistema verifica se ha proximo status disponivel.
3. Se status atual for `em_andamento`, sistema exige descricao do servico executado.
4. Sistema grava o novo status.
5. Sistema registra historico de status.
6. Sistema atualiza o detalhamento do chamado.

### Decisoes
- chamado pode avancar?
- usuario possui permissao para atuar nesse chamado?
- existe observacao obrigatoria?

### Fim
Chamado atualizado no fluxo.

## Fluxo 5 - Acompanhamento de chamados pelo cliente
### Inicio
Cliente autenticado acessa Dashboard ou Meus Chamados.

### Sequencia
1. Sistema identifica o cliente vinculado.
2. Sistema consulta apenas chamados do proprio cliente.
3. Sistema exibe lista, status e atualizacoes recentes.
4. Cliente acessa o detalhamento de um chamado.
5. Sistema exibe historico, iteracoes e anexos disponiveis.

### Decisoes
- usuario e cliente?
- chamado pertence ao cliente autenticado?

### Fim
Cliente acompanha o progresso do atendimento.

## Fluxo 6 - Manutencao de cadastros auxiliares
### Inicio
Administrador acessa a area de cadastros.

### Sequencia
1. Sistema exibe categorias de cadastros auxiliares.
2. Administrador escolhe a categoria desejada.
3. Administrador cria, edita, ativa ou inativa um item.
4. Sistema valida unicidade e consistencia.
5. Sistema grava o cadastro.
6. Sistema reflete o item nos formularios operacionais.

### Fim
Cadastro auxiliar atualizado.

## Fluxo 7 - Cadastro de cliente com acesso
### Inicio
Administrador acessa a tela de clientes.

### Sequencia
1. Administrador informa dados do cliente.
2. Administrador informa usuario e senha de acesso.
3. Sistema cria o usuario vinculado.
4. Sistema cria o cliente associado ao usuario.
5. Sistema confirma o cadastro.

### Decisoes
- usuario de acesso ja existe?
- email ja existe?
- departamento cadastral foi informado?

### Fim
Cliente com acesso criado.

## Observacoes para desenho
- Cada fluxo deve ser desenhado com swimlanes quando fizer sentido, separando `Usuario`, `Sistema` e, se desejado, `Banco/API`.
- Os pontos de validacao devem ser representados por losangos de decisao.
- Os fluxos 1, 3, 4 e 5 sao os mais importantes e devem ser priorizados na entrega.
