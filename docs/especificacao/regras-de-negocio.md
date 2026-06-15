# Regras de Negocio - SGOS

## Objetivo
Este documento consolida as regras de negocio do SGOS e deve ser usado como referencia principal para validacoes do sistema, descricao funcional e desenho dos diagramas.

## RN01 - Cliente com acesso vinculado
Todo cliente deve possuir um usuario de acesso vinculado.

## RN02 - Cliente e acesso sao um unico fluxo de cadastro
O cadastro de cliente e o cadastro do acesso do cliente pertencem ao mesmo processo de negocio. Nao deve existir fluxo separado para criar usuario cliente fora da rotina de clientes.

## RN03 - Cliente abre chamado apenas para si mesmo
Quando o usuario autenticado for do tipo `somente_cliente`, o chamado deve ser criado obrigatoriamente para o cliente vinculado ao usuario logado.

## RN04 - Chamado pertence a um unico departamento
Toda ordem de servico deve possuir exatamente um departamento de destino.

## RN05 - Cliente escolhe o departamento de destino
Ao abrir um chamado, o cliente deve selecionar para qual setor o chamado sera encaminhado.

## RN06 - Tecnico opera por departamento
Usuario tecnico visualiza e atua apenas em chamados do proprio departamento.

## RN07 - Administrador possui visao global
Usuario administrador pode visualizar chamados de todos os departamentos e atuar na distribuicao operacional.

## RN08 - Atribuicao de tecnico
Um chamado pode ser atribuido a um tecnico.

Regras complementares:
- administrador pode atribuir chamado a qualquer tecnico
- tecnico nao pode atribuir chamado livremente para terceiros fora das regras internas
- cliente nao participa da atribuicao

## RN09 - Fluxo sequencial de status
O chamado deve seguir a sequencia:

1. `aberta`
2. `aguardando`
3. `em_andamento`
4. `em_avaliacao`
5. `encerrada`

## RN10 - Servico executado obrigatorio
Para sair do status `em_andamento`, e obrigatorio informar a descricao do servico executado.

## RN11 - Cliente nao define prioridade nem urgencia
O cliente nao pode definir prioridade nem urgencia ao abrir chamado. Esses campos pertencem a classificacao interna do atendimento.

## RN12 - Cliente informa apenas dados da solicitacao
Na abertura feita por cliente, os dados de negocio sao:
- cliente vinculado
- departamento de destino
- tipo de chamado
- categoria / assunto
- titulo / resumo
- descricao detalhada
- anexos opcionais

## RN13 - Exclusao de cliente com OS ativa
Cliente nao pode ser excluido se possuir ao menos um chamado com status diferente de `encerrada`.

## RN14 - Exclusao de chamado encerrado
Somente chamado encerrado pode ser removido conforme a politica do sistema.

## RN15 - Cadastros auxiliares sao administraveis
Somente administrador pode manter:
- departamentos
- tipos de chamado
- categorias / assuntos
- prioridades
- urgencias

## RN16 - Usuarios internos sao administraveis
Somente administrador pode criar e manter usuarios internos dos tipos:
- administrador
- tecnico

## RN17 - Cliente nao acessa rotinas internas
Usuario cliente nao acessa:
- cadastros administrativos
- lista administrativa de clientes
- kanban operacional interno
- atribuicao de tecnico
- avancos de status

## RN18 - Historico obrigatorio
Alteracoes relevantes do chamado devem ser rastreaveis por historico de status, iteracoes ou anexos.

## RN19 - Numero do chamado deve ser unico
Cada ordem de servico deve possuir identificador unico e sequencial.

## RN20 - Um cliente possui varios chamados
Um cliente pode abrir varios chamados ao longo do tempo, mas cada chamado pertence a um unico cliente.

## RN21 - Um chamado pode possuir anexos
Um chamado pode possuir zero, um ou varios anexos.

## RN22 - Um chamado pode possuir iteracoes
Um chamado pode possuir zero, uma ou varias iteracoes ao longo do atendimento.
