# Casos de Uso - SGOS

## Atores
- Administrador
- Tecnico
- Cliente

## UC01 - Autenticar usuario
### Atores
- Administrador
- Tecnico
- Cliente

### Objetivo
Permitir acesso ao sistema conforme o perfil do usuario.

### Pre-condicoes
- usuario previamente cadastrado

### Pos-condicoes
- sessao autenticada iniciada
- perfil identificado

## UC02 - Cadastrar cliente com acesso
### Ator
- Administrador

### Objetivo
Criar o cliente juntamente com seu usuario de acesso.

## UC03 - Manter cliente
### Ator
- Administrador

### Objetivo
Editar dados do cliente e de seu acesso vinculado.

## UC04 - Cadastrar usuario interno
### Ator
- Administrador

### Objetivo
Criar usuario interno do tipo administrador ou tecnico.

## UC05 - Manter cadastros auxiliares
### Ator
- Administrador

### Objetivo
Manter departamentos, tipos, categorias, prioridades e urgencias.

## UC06 - Abrir chamado como cliente
### Ator
- Cliente

### Objetivo
Abrir chamado para o proprio cadastro.

### Pre-condicoes
- cliente autenticado
- cliente vinculado ao usuario logado

### Fluxo principal
1. Cliente acessa a tela de abertura.
2. Sistema identifica automaticamente o cliente vinculado.
3. Cliente escolhe o departamento de destino.
4. Cliente informa tipo, categoria, titulo e descricao.
5. Cliente anexa arquivos, se desejar.
6. Sistema valida os dados.
7. Sistema cria o chamado com status `aberta`.

### Pos-condicoes
- chamado criado
- historico inicial registrado

## UC07 - Abrir chamado como usuario interno
### Atores
- Administrador
- Tecnico

### Objetivo
Registrar um chamado operacional conforme as regras do perfil interno.

## UC08 - Consultar chamados
### Atores
- Administrador
- Tecnico
- Cliente

### Objetivo
Visualizar chamados dentro do escopo permitido pelo perfil.

## UC09 - Visualizar detalhes do chamado
### Atores
- Administrador
- Tecnico
- Cliente

### Objetivo
Consultar dados completos, historico, iteracoes e anexos de um chamado permitido.

## UC10 - Atribuir tecnico
### Ator
- Administrador

### Objetivo
Definir ou alterar o tecnico responsavel pelo chamado.

## UC11 - Avancar status do chamado
### Atores
- Administrador
- Tecnico

### Objetivo
Mover o chamado para o proximo status do fluxo.

### Regra especial
Ao sair de `em_andamento`, deve ser informada a descricao do servico executado.

## UC12 - Registrar iteracao
### Atores
- Administrador
- Tecnico

### Objetivo
Registrar informacoes complementares sobre o atendimento.

## UC13 - Enviar anexo
### Atores
- Administrador
- Tecnico
- Cliente

### Objetivo
Anexar arquivos ao chamado no contexto permitido.

## UC14 - Acompanhar meus chamados
### Atores
- Administrador
- Tecnico
- Cliente

### Objetivo
Permitir acompanhamento rapido dos chamados do escopo do usuario.

## Relacoes sugeridas para o diagrama
- Administrador inclui: manter clientes, manter usuarios internos, manter cadastros auxiliares, atribuir tecnico, avancar status
- Tecnico inclui: consultar chamados, visualizar detalhes, avancar status, registrar iteracao, enviar anexo
- Cliente inclui: abrir chamado, consultar chamados, visualizar detalhes, acompanhar meus chamados, enviar anexo
