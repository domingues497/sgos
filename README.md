# SGOS - Especificacao Base do Sistema

Este `README.md` deve ser usado como documento-base para o programador produzir a documentacao formal do projeto.

O objetivo deste material e consolidar:

- contexto do produto
- escopo funcional
- atores
- regras de negocio
- requisitos funcionais
- requisitos nao funcionais
- entidades de dominio e relacionamentos
- fluxos principais
- insumos para diagrama de classes
- insumos para casos de uso
- insumos para diagramas de atividade

Este arquivo nao deve ser tratado como guia de instalacao. Ele deve ser tratado como referencia de analise e especificacao.

---

## 1. Visao Geral

### 1.1 Nome do sistema

SGOS - Sistema de Gestao de Ordens de Servico / Chamados.

### 1.2 Objetivo do sistema

O SGOS tem como finalidade registrar, classificar, encaminhar, acompanhar e encerrar chamados de atendimento entre clientes e equipe interna.

O sistema deve permitir:

- abertura estruturada de chamados
- distribuicao por departamento
- atribuicao para tecnicos
- acompanhamento do ciclo de vida do chamado
- registro de historico, iteracoes e anexos
- segregacao de acesso por perfil de usuario

### 1.3 Problema que o sistema resolve

O sistema centraliza o atendimento e reduz perda de contexto operacional ao substituir controles dispersos por um fluxo unico, auditavel e orientado por regras.

### 1.4 Escopo de negocio

O SGOS cobre:

- cadastro e manutencao de clientes
- cadastro e manutencao de usuarios internos
- cadastro de tabelas de apoio
- abertura de chamados
- tratamento operacional por status
- acompanhamento pelo cliente
- controle por departamento
- historico de mudancas e interacoes
- anexacao de arquivos

O SGOS nao cobre, neste escopo:

- faturamento
- SLA contratual com penalidade financeira automatica
- integracao operacional completa com ERP
- notificacoes por e-mail ou WhatsApp como requisito obrigatorio

---

## 2. Objetivo da Documentacao Formal

Com base neste `README.md`, o programador deve ser capaz de produzir:

- documento de regras de negocio
- documento de requisitos funcionais
- documento de requisitos nao funcionais
- documento de casos de uso
- diagrama de classes
- diagrama de atividades
- diagrama do banco de dados

Se houver divergencia entre interpretacao visual do frontend e as regras abaixo, a documentacao formal deve priorizar as regras descritas neste arquivo.

---

## 3. Atores do Sistema

### 3.1 Administrador

Usuario interno com permissao total de gestao.

Responsabilidades:

- gerenciar usuarios internos
- gerenciar cadastros auxiliares
- visualizar chamados de todos os departamentos
- atribuir chamado a qualquer tecnico
- acompanhar operacao de forma global

### 3.2 Tecnico

Usuario interno operacional vinculado a um departamento.

Responsabilidades:

- visualizar chamados do proprio departamento
- assumir ou receber atribuicao de chamados
- atualizar o progresso do atendimento
- registrar iteracoes
- informar servico executado ao sair de `em_andamento`

### 3.3 Cliente

Usuario externo vinculado ao proprio cadastro de cliente.

Responsabilidades:

- abrir chamado para si mesmo
- escolher o departamento de destino do chamado
- informar dados da solicitacao
- anexar arquivos
- acompanhar o andamento dos seus proprios chamados

Restricoes:

- nao pode abrir chamado para outro cliente
- nao pode atribuir tecnico
- nao pode avancar status operacional
- nao pode definir prioridade nem urgencia
- nao acessa rotinas administrativas

---

## 4. Glossario de Dominio

- `Cliente`: entidade de negocio que representa a organizacao, pessoa ou unidade solicitante do atendimento. No sistema, o cliente possui um usuario de acesso vinculado.
- `Usuario`: identidade autenticavel do sistema.
- `PerfilUsuario`: classificacao do usuario como `admin`, `tecnico` ou `somente_cliente`.
- `Departamento`: setor de destino ou setor responsavel pelo atendimento.
- `Tipo de Chamado`: classificacao macro do chamado, ex.: incidente, solicitacao.
- `Categoria / Assunto`: classificacao detalhada do tema.
- `Prioridade`: nivel de importancia operacional definido internamente.
- `Urgencia`: nivel de rapidez operacional definido internamente.
- `Ordem de Servico` ou `Chamado`: registro principal do atendimento.
- `Iteracao`: comentario, atualizacao ou comunicacao adicional vinculada ao chamado.
- `HistoricoStatus`: trilha de auditoria das mudancas de status.
- `Anexo`: arquivo enviado no contexto de um chamado.

---

## 5. Perfis e Politica de Acesso

### 5.1 Tipos de usuario

O sistema possui tres tipos de usuario:

- `admin`
- `tecnico`
- `somente_cliente`

### 5.2 Regras de visibilidade

- Administrador pode visualizar todos os chamados.
- Tecnico visualiza apenas chamados do seu departamento.
- Cliente visualiza apenas chamados vinculados ao seu proprio cadastro.

### 5.3 Regras de navegacao

- Administrador acessa telas administrativas e operacionais.
- Tecnico acessa telas operacionais internas.
- Cliente acessa apenas telas de acompanhamento e abertura do proprio chamado.

### 5.4 Regras de atribuicao

- Administrador pode atribuir chamado a qualquer tecnico.
- Tecnico comum so opera dentro do proprio departamento.
- Cliente nao participa da atribuicao de tecnico.

---

## 6. Regras de Negocio

As regras abaixo devem ser numeradas na documentacao formal e mantidas como referencia principal.

### RN01 - Cliente com acesso vinculado

Todo cliente deve possuir um usuario de acesso vinculado.

### RN02 - Cliente e acesso sao um unico fluxo de cadastro

O cadastro de cliente e o cadastro do acesso do cliente fazem parte do mesmo processo de negocio. Nao deve existir um segundo fluxo administrativo para criar "usuario cliente" separado do cadastro de cliente.

### RN03 - Cliente abre chamado apenas para si mesmo

Quando o usuario autenticado for do tipo `somente_cliente`, o chamado obrigatoriamente deve ser criado para o cliente vinculado ao usuario logado.

### RN04 - Chamado pertence a um unico departamento

Toda ordem de servico deve possuir exatamente um departamento de destino.

### RN05 - Cliente escolhe o departamento de destino

Ao abrir um chamado, o usuario cliente deve selecionar para qual setor o chamado sera encaminhado. Esse departamento nao precisa coincidir com o departamento cadastrado no perfil interno de outros usuarios.

### RN06 - Tecnico opera por departamento

Usuario tecnico so pode visualizar e atuar em chamados pertencentes ao seu proprio departamento.

### RN07 - Administrador possui visao global

Usuario administrador pode visualizar chamados de todos os departamentos e gerenciar a distribuicao operacional.

### RN08 - Atribuicao de tecnico

Um chamado pode ser atribuido a um tecnico.

Regras:

- administrador pode atribuir para qualquer tecnico
- tecnico nao atribui para terceiros fora das regras operacionais previstas
- cliente nao pode atribuir tecnico

### RN09 - Fluxo sequencial de status

O ciclo de vida do chamado deve seguir a sequencia:

1. `aberta`
2. `aguardando`
3. `em_andamento`
4. `em_avaliacao`
5. `encerrada`

Nao e permitido saltar etapas fora da regra definida.

### RN10 - Servico executado obrigatorio

Para sair do status `em_andamento`, e obrigatorio registrar a descricao do servico executado.

### RN11 - Cliente nao define classificacao operacional interna

O usuario cliente nao pode definir:

- prioridade
- urgencia

Esses atributos pertencem a classificacao interna do atendimento.

### RN12 - Cliente informa somente dados da solicitacao

Na abertura do chamado pelo cliente, os dados esperados sao:

- cliente vinculado
- departamento de destino
- tipo de chamado
- categoria / assunto
- titulo / resumo
- descricao detalhada
- anexos opcionais

### RN13 - Exclusao de cliente com OS ativa

Cliente nao pode ser excluido se possuir ordem de servico com status diferente de `encerrada`.

### RN14 - Exclusao de chamado encerrado

Somente chamado encerrado pode ser removido, conforme politica do sistema.

### RN15 - Cadastros auxiliares sao administraveis

Os seguintes cadastros devem ser mantidos por administradores:

- departamentos
- tipos de chamado
- categorias / assuntos
- prioridades
- urgencias

### RN16 - Usuarios internos sao administraveis

Somente administradores podem criar e manter usuarios internos dos tipos:

- administrador
- tecnico

### RN17 - Cliente nao acessa rotinas internas

Usuario cliente nao acessa:

- cadastros administrativos
- lista administrativa de clientes
- kanban operacional interno
- atribuicao de tecnico
- avancos de status

### RN18 - Historico obrigatorio

Toda alteracao relevante no chamado deve ser rastreavel por historico de status, iteracoes ou anexos.

### RN19 - Numero do chamado deve ser unico

Cada ordem de servico deve possuir um identificador unico e sequencial.

### RN20 - Um cliente possui multiplos chamados

Um cliente pode abrir varios chamados ao longo do tempo, mas cada chamado pertence a um unico cliente.

### RN21 - Um chamado pode ter zero ou muitos anexos

Arquivos anexados sao opcionais e pertencem a um unico chamado.

### RN22 - Um chamado pode ter zero ou muitas iteracoes

Interacoes sao utilizadas para complementar contexto, atualizacoes e comunicacao.

---

## 7. Requisitos Funcionais

Os requisitos abaixo devem ser usados como base para documento formal e rastreabilidade.

### RF01 - Autenticacao

O sistema deve permitir autenticar usuarios por login e senha.

### RF02 - Cadastro publico de cliente com acesso

O sistema deve permitir cadastrar cliente com credenciais de acesso.

### RF03 - Login e identificacao do perfil

O sistema deve identificar o perfil do usuario autenticado e ajustar as permissoes e navegacao.

### RF04 - Cadastro de clientes

O sistema deve permitir cadastrar clientes com:

- nome
- telefone
- email
- endereco
- departamento cadastral
- usuario de acesso
- senha de acesso

### RF05 - Edicao de clientes

O sistema deve permitir editar os dados do cliente e seu acesso vinculado.

### RF06 - Listagem de clientes

O sistema deve permitir listar clientes, pesquisar e filtrar por departamento.

### RF07 - Exclusao de clientes

O sistema deve permitir excluir cliente apenas quando nao houver OS ativa.

### RF08 - Cadastro de usuarios internos

O sistema deve permitir ao administrador criar usuarios internos dos tipos `admin` e `tecnico`.

### RF09 - Edicao e desativacao de usuarios internos

O sistema deve permitir ao administrador atualizar e ativar/desativar usuarios internos.

### RF10 - Cadastro de tabelas auxiliares

O sistema deve permitir ao administrador criar, editar, ativar e inativar:

- departamentos
- tipos
- categorias
- prioridades
- urgencias

### RF11 - Abertura de chamado por usuario interno

O sistema deve permitir a usuarios internos abrir chamado informando todos os campos operacionais previstos.

### RF12 - Abertura de chamado por cliente

O sistema deve permitir ao usuario cliente abrir chamado com os seguintes dados:

- cliente fixo do usuario logado
- departamento de destino escolhido pelo usuario
- tipo de chamado
- categoria / assunto
- titulo / resumo
- descricao detalhada
- anexos opcionais

### RF13 - Consulta de chamados

O sistema deve permitir consultar chamados com filtros por status, cliente, departamento e escopo do usuario.

### RF14 - Visualizacao detalhada do chamado

O sistema deve apresentar dados completos do chamado, incluindo historico, iteracoes e anexos.

### RF15 - Kanban operacional

O sistema deve apresentar um quadro Kanban para operacao interna, agrupando chamados por status.

### RF16 - Visao Meus Chamados

O sistema deve apresentar uma visao "Meus Chamados" adaptada ao perfil:

- tecnico: chamados atribuidos e operacao do proprio contexto
- admin: visao ampliada de acompanhamento
- cliente: acompanhamento apenas dos proprios chamados

### RF17 - Avanco de status

O sistema deve permitir avancar o status do chamado de forma controlada e sequencial.

### RF18 - Registro do servico executado

O sistema deve exigir descricao obrigatoria quando o chamado sair de `em_andamento`.

### RF19 - Atribuicao de tecnico

O sistema deve permitir atribuicao de tecnico ao chamado conforme regras de perfil.

### RF20 - Registro de iteracoes

O sistema deve permitir registrar iteracoes textuais em chamados.

### RF21 - Upload de anexos

O sistema deve permitir anexar arquivos ao chamado.

### RF22 - Dashboard

O sistema deve exibir indicadores e resumos conforme o perfil do usuario.

### RF23 - Controle de acesso por interface

O sistema deve adaptar o menu lateral, botoes e acoes conforme o perfil do usuario.

### RF24 - Controle de acesso por backend

O backend deve validar as regras de permissao independentemente da interface.

### RF25 - Auditoria basica

O sistema deve manter historico minimo de alteracao de status e registros adicionais do chamado.

---

## 8. Requisitos Nao Funcionais

### RNF01 - Arquitetura

O sistema deve operar com frontend web e backend baseado em API REST.

### RNF02 - Seguranca

Autenticacao deve ser baseada em token JWT ou mecanismo equivalente de sessao autenticada.

### RNF03 - Controle de autorizacao

As regras de acesso devem ser aplicadas no backend, nao apenas na interface.

### RNF04 - Rastreabilidade

Operacoes relevantes devem possuir trilha minima de auditoria.

### RNF05 - Usabilidade

As telas devem ser responsivas, com linguagem visual consistente e adequada a cada perfil.

### RNF06 - Manutenibilidade

Cadastros auxiliares nao devem ser hardcoded no frontend; devem ser administraveis.

### RNF07 - Integridade dos dados

Relacionamentos entre cliente, usuario, chamado e departamento devem ser consistentes e protegidos por validacoes.

### RNF08 - Escalabilidade funcional

O sistema deve permitir evolucao de novos tipos de cadastro, perfis e relatorios sem reestruturar o dominio principal.

### RNF09 - Portabilidade

O sistema deve poder operar em ambiente local e em ambiente de nuvem.

### RNF10 - Performance percebida

Consultas principais devem suportar listagem paginada e filtros para evitar degradacao perceptivel da interface.

### RNF11 - Compatibilidade web

As telas devem funcionar em navegadores modernos com interface web padrao.

### RNF12 - Padronizacao documental

Os nomes das entidades, regras e fluxos devem ser mantidos de forma consistente entre codigo, documentacao e diagramas.

---

## 9. Entidades de Dominio

Esta secao deve servir diretamente como base para o diagrama de classes.

### 9.1 Entidade Usuario

Representa a conta autenticavel do sistema.

Atributos relevantes:

- id
- username
- first_name
- last_name
- email
- is_active
- is_superuser

Relacionamentos:

- 1:1 com `PerfilUsuario`
- 1:1 opcional com `Cliente` quando o usuario for cliente
- 1:N com `OrdemServico` como `criado_por`
- 1:N com `OrdemServico` como `atribuido_para`
- 1:N com `Iteracao` como `criado_por`
- 1:N com `Anexo` como `enviado_por`
- 1:N com `HistoricoStatus` como `alterado_por`

### 9.2 Entidade PerfilUsuario

Responsavel por classificar o tipo do usuario.

Atributos relevantes:

- tipo
- departamento

Tipos permitidos:

- admin
- tecnico
- somente_cliente

Relacionamentos:

- 1:1 com `Usuario`
- N:1 com `Departamento`

### 9.3 Entidade Cliente

Representa o solicitante de negocio.

Atributos relevantes:

- nome
- email
- telefone
- endereco
- departamento cadastral

Relacionamentos:

- 1:1 com `Usuario`
- N:1 com `Departamento`
- 1:N com `OrdemServico`

### 9.4 Entidade OrdemServico

Entidade central do sistema.

Atributos relevantes:

- numero
- titulo
- descricao
- status
- etapa
- aberta_em
- status_alterado_em
- valor_total

Relacionamentos:

- N:1 com `Cliente`
- N:1 com `Usuario` como `criado_por`
- N:1 com `Usuario` como `atribuido_para`
- N:1 com `Departamento`
- N:1 com `Tipo`
- N:1 com `Categoria`
- N:1 com `Prioridade`
- N:1 com `Urgencia`
- 1:N com `HistoricoStatus`
- 1:N com `HistoricoEtapa`
- 1:N com `Iteracao`
- 1:N com `Anexo`

### 9.5 Entidade HistoricoStatus

Registra as mudancas de status do chamado.

Atributos relevantes:

- status_anterior
- status_novo
- alterado_em
- observacao

Relacionamentos:

- N:1 com `OrdemServico`
- N:1 com `Usuario`

### 9.6 Entidade HistoricoEtapa

Registra mudancas de etapa interna do atendimento.

### 9.7 Entidade Iteracao

Registra comentarios e interacoes sobre o chamado.

### 9.8 Entidade Anexo

Registra arquivos enviados no contexto do chamado.

### 9.9 Entidades de apoio

As entidades abaixo funcionam como tabelas de dominio parametrizavel:

- `OpcaoDepartamento`
- `OpcaoTipo`
- `OpcaoCategoria`
- `OpcaoPrioridade`
- `OpcaoUrgencia`

Essas entidades possuem ao menos:

- nome
- ativo
- timestamps

`Prioridade` e `Urgencia` possuem tambem:

- nivel

---

## 10. Relacionamentos Principais Para Diagrama de Classes

Use os relacionamentos abaixo como guia direto do diagrama:

- `Usuario` 1:1 `PerfilUsuario`
- `Usuario` 1:1 `Cliente` quando perfil for cliente
- `Cliente` 1:N `OrdemServico`
- `OrdemServico` N:1 `Departamento`
- `OrdemServico` N:1 `Tipo`
- `OrdemServico` N:1 `Categoria`
- `OrdemServico` N:1 `Prioridade`
- `OrdemServico` N:1 `Urgencia`
- `OrdemServico` N:1 `Usuario` como criador
- `OrdemServico` N:1 `Usuario` como tecnico atribuido
- `OrdemServico` 1:N `HistoricoStatus`
- `OrdemServico` 1:N `HistoricoEtapa`
- `OrdemServico` 1:N `Iteracao`
- `OrdemServico` 1:N `Anexo`

Observacao importante:

- `Cliente` e `Usuario` nao sao a mesma entidade conceitual no banco, mas fazem parte do mesmo fluxo de negocio quando o ator e cliente.
- Na documentacao de negocio, o programador pode representar que "cada cliente possui um acesso vinculado".

---

## 11. Ciclo de Vida do Chamado

### 11.1 Estados principais

Estados:

1. `aberta`
2. `aguardando`
3. `em_andamento`
4. `em_avaliacao`
5. `encerrada`

### 11.2 Regras do ciclo

- o chamado nasce em `aberta`
- o chamado avanca de forma sequencial
- ao sair de `em_andamento`, deve existir descricao do servico executado
- chamado encerrado nao deve seguir fluxo operacional normal

### 11.3 Eventos de negocio associados

- abertura do chamado
- atribuicao de tecnico
- mudanca de status
- registro de iteracao
- envio de anexo
- encerramento

---

## 12. Casos de Uso

Esta secao serve como base textual para o diagrama de casos de uso.

### UC01 - Autenticar usuario

Atores:

- Administrador
- Tecnico
- Cliente

Objetivo:

- permitir acesso ao sistema conforme perfil

### UC02 - Cadastrar cliente com acesso

Atores:

- Administrador

Objetivo:

- criar o registro do cliente juntamente com seu usuario de acesso

### UC03 - Manter cliente

Atores:

- Administrador

Objetivo:

- editar dados de cliente e seu acesso vinculado

### UC04 - Cadastrar usuario interno

Atores:

- Administrador

Objetivo:

- criar usuario interno admin ou tecnico

### UC05 - Manter cadastros auxiliares

Atores:

- Administrador

Objetivo:

- manter departamentos, tipos, categorias, prioridades e urgencias

### UC06 - Abrir chamado como cliente

Atores:

- Cliente

Objetivo:

- abrir chamado para o proprio cadastro informando setor de destino e dados da solicitacao

Pre-condicoes:

- cliente autenticado
- cliente vinculado ao usuario

Pos-condicoes:

- chamado criado com status `aberta`
- historico inicial registrado

### UC07 - Abrir chamado como usuario interno

Atores:

- Administrador
- Tecnico

Objetivo:

- registrar um chamado operacional conforme regras do perfil

### UC08 - Consultar chamados

Atores:

- Administrador
- Tecnico
- Cliente

Objetivo:

- visualizar chamados permitidos pelo perfil

### UC09 - Visualizar detalhes do chamado

Atores:

- Administrador
- Tecnico
- Cliente

Objetivo:

- consultar dados completos de um chamado permitido

### UC10 - Atribuir tecnico

Atores:

- Administrador

Objetivo:

- definir o tecnico responsavel pelo chamado

### UC11 - Avancar status do chamado

Atores:

- Administrador
- Tecnico

Objetivo:

- mover chamado para o proximo status valido

Regra especial:

- se status atual for `em_andamento`, deve ser registrada a descricao do servico executado

### UC12 - Registrar iteracao

Atores:

- Administrador
- Tecnico

Objetivo:

- complementar o contexto do chamado com informacoes adicionais

### UC13 - Enviar anexo

Atores:

- Administrador
- Tecnico
- Cliente

Objetivo:

- anexar arquivo ao chamado no contexto permitido

### UC14 - Acompanhar meus chamados

Atores:

- Tecnico
- Cliente
- Administrador

Objetivo:

- acompanhar rapidamente chamados do escopo do usuario

---

## 13. Fluxos de Atividade

Esta secao nao substitui o diagrama, mas fornece os roteiros que devem ser convertidos em diagramas de atividade.

### 13.1 Fluxo de abertura de chamado pelo cliente

1. Cliente autentica no sistema.
2. Cliente acessa `Abrir Chamado`.
3. Sistema identifica automaticamente o cliente vinculado.
4. Sistema apresenta formulario reduzido.
5. Cliente escolhe o departamento de destino.
6. Cliente informa tipo.
7. Cliente informa categoria.
8. Cliente informa titulo.
9. Cliente informa descricao detalhada.
10. Cliente anexa arquivos, se desejar.
11. Sistema valida dados obrigatorios.
12. Sistema cria a ordem de servico com status `aberta`.
13. Sistema registra historico inicial.
14. Sistema confirma abertura e disponibiliza acompanhamento.

### 13.2 Fluxo de atribuicao de tecnico pelo administrador

1. Administrador acessa um chamado.
2. Sistema apresenta dados atuais do chamado.
3. Administrador escolhe um tecnico.
4. Sistema valida o usuario selecionado.
5. Sistema grava a atribuicao.
6. Sistema atualiza a visualizacao.

### 13.3 Fluxo de tratamento do chamado pelo tecnico

1. Tecnico acessa os chamados do seu departamento.
2. Tecnico identifica o chamado.
3. Tecnico inicia atendimento.
4. Tecnico move o chamado pelo fluxo operacional.
5. Ao sair de `em_andamento`, tecnico informa o servico executado.
6. Sistema registra a mudanca de status e observacao.
7. Chamado segue para avaliacao e encerramento.

### 13.4 Fluxo de acompanhamento pelo cliente

1. Cliente autentica no sistema.
2. Cliente acessa `Dashboard` ou `Meus Chamados`.
3. Sistema lista apenas chamados do proprio cliente.
4. Cliente consulta status, historico, iteracoes e anexos disponiveis.
5. Cliente acompanha o encerramento do atendimento.

### 13.5 Fluxo de manutencao de cadastros auxiliares

1. Administrador acessa `Cadastros`.
2. Sistema exibe categorias de cadastros.
3. Administrador cria, edita, ativa ou inativa registros.
4. Sistema aplica os dados nos formularios operacionais.

---

## 14. Regras de Desenho dos Diagramas

### 14.1 Diagrama de Classes

O diagrama de classes deve obrigatoriamente representar:

- `Usuario`
- `PerfilUsuario`
- `Cliente`
- `OrdemServico`
- `HistoricoStatus`
- `HistoricoEtapa`
- `Iteracao`
- `Anexo`
- `OpcaoDepartamento`
- `OpcaoTipo`
- `OpcaoCategoria`
- `OpcaoPrioridade`
- `OpcaoUrgencia`

Tambem deve deixar visivel:

- cardinalidades
- especializacao de perfis por atributo `tipo`
- dupla relacao de `Usuario` com `OrdemServico` como `criado_por` e `atribuido_para`

### 14.2 Diagrama de Casos de Uso

Deve conter no minimo os atores:

- Administrador
- Tecnico
- Cliente

E os casos:

- autenticar
- manter clientes
- manter usuarios internos
- manter cadastros auxiliares
- abrir chamado
- consultar chamado
- acompanhar meus chamados
- atribuir tecnico
- avancar status
- registrar iteracao
- anexar arquivo

### 14.3 Diagrama de Atividades

Deve existir pelo menos para:

- abertura de chamado pelo cliente
- atribuicao de tecnico
- tratamento do chamado pelo tecnico
- encerramento do chamado

---

## 15. Regras Especificas Para a Documentacao Formal

Ao transformar este conteudo em documentacao oficial, o programador deve:

- manter a numeracao das regras de negocio
- manter a separacao entre ator, acao e restricao
- distinguir claramente o fluxo do cliente do fluxo interno
- deixar explicito que cliente nao define prioridade nem urgencia
- deixar explicito que o cliente escolhe o departamento de destino
- deixar explicito que cliente e acesso fazem parte do mesmo fluxo de negocio
- deixar explicito que usuarios internos sao mantidos separadamente

---

## 16. Estrutura Sugerida dos Documentos Finais

Sugestao de entrega documental:

1. `01-visao-geral.md`
2. `02-regras-de-negocio.md`
3. `03-requisitos-funcionais.md`
4. `04-requisitos-nao-funcionais.md`
5. `05-casos-de-uso.md`
6. `06-diagrama-de-classes.md`
7. `07-diagramas-de-atividade.md`
8. `08-diagrama-do-banco.md`

---

## 17. Observacoes Finais

Este projeto ja possui implementacao funcional em frontend e backend, mas a documentacao formal deve ser produzida como artefato de analise, organizando o conhecimento do dominio de forma clara.

A documentacao final deve refletir principalmente:

- o modelo de perfis
- o comportamento diferenciado entre cliente, tecnico e administrador
- o fluxo de abertura e tratamento dos chamados
- a centralidade da ordem de servico como entidade principal
- a administracao das tabelas auxiliares
- o controle por departamento
