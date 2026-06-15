# Requisitos Funcionais - SGOS

## Objetivo
Este documento descreve os requisitos funcionais que definem o comportamento esperado do SGOS.

## RF01 - Autenticacao
O sistema deve permitir autenticar usuarios por login e senha.

## RF02 - Cadastro publico de cliente com acesso
O sistema deve permitir cadastrar cliente juntamente com seu usuario e senha de acesso.

## RF03 - Identificacao do perfil
O sistema deve identificar o perfil do usuario autenticado e adaptar permissoes, menu e acoes disponiveis.

## RF04 - Cadastro de clientes
O sistema deve permitir cadastrar clientes com:
- nome
- telefone
- email
- endereco
- departamento cadastral
- usuario de acesso
- senha de acesso

## RF05 - Edicao de clientes
O sistema deve permitir editar os dados do cliente e o acesso vinculado.

## RF06 - Listagem de clientes
O sistema deve permitir listar clientes, pesquisar por texto e filtrar por departamento.

## RF07 - Exclusao de clientes
O sistema deve permitir excluir cliente apenas quando nao houver chamado ativo.

## RF08 - Cadastro de usuarios internos
O sistema deve permitir ao administrador criar usuarios internos dos tipos `admin` e `tecnico`.

## RF09 - Edicao e desativacao de usuarios internos
O sistema deve permitir ao administrador atualizar e ativar/desativar usuarios internos.

## RF10 - Cadastro de tabelas auxiliares
O sistema deve permitir ao administrador criar, editar, ativar e inativar:
- departamentos
- tipos
- categorias
- prioridades
- urgencias

## RF11 - Abertura de chamado por usuario interno
O sistema deve permitir a usuarios internos abrir chamado com todos os campos operacionais previstos.

## RF12 - Abertura de chamado por cliente
O sistema deve permitir ao cliente abrir chamado com:
- cliente vinculado automaticamente
- departamento de destino escolhido pelo cliente
- tipo de chamado
- categoria / assunto
- titulo / resumo
- descricao detalhada
- anexos opcionais

## RF13 - Consulta de chamados
O sistema deve permitir consultar chamados com filtros por status, cliente, departamento e escopo do usuario.

## RF14 - Visualizacao detalhada do chamado
O sistema deve apresentar os dados completos do chamado, incluindo historico, iteracoes e anexos.

## RF15 - Kanban operacional
O sistema deve apresentar quadro Kanban para operacao interna, agrupando chamados por status.

## RF16 - Visao Meus Chamados
O sistema deve apresentar a visao "Meus Chamados" adaptada ao perfil do usuario.

## RF17 - Avanco de status
O sistema deve permitir avancar o status do chamado respeitando a ordem definida no processo.

## RF18 - Registro do servico executado
O sistema deve exigir descricao obrigatoria do servico executado quando o chamado sair de `em_andamento`.

## RF19 - Atribuicao de tecnico
O sistema deve permitir atribuicao de tecnico ao chamado conforme o perfil do usuario.

## RF20 - Registro de iteracoes
O sistema deve permitir registrar iteracoes textuais em chamados.

## RF21 - Upload de anexos
O sistema deve permitir anexar arquivos ao chamado.

## RF22 - Dashboard
O sistema deve exibir indicadores e resumos adequados ao perfil autenticado.

## RF23 - Controle de acesso por interface
O sistema deve adaptar menu lateral, botoes e acoes conforme o perfil do usuario.

## RF24 - Controle de acesso por backend
O backend deve validar as permissoes e restricoes de negocio independentemente do comportamento do frontend.

## RF25 - Auditoria basica
O sistema deve manter historico minimo de mudanca de status e registros associados ao chamado.
