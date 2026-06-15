# Diagrama de Classes - Base de Modelagem

## Objetivo
Este documento fornece os insumos necessarios para desenhar o diagrama de classes do SGOS.

## Entidades obrigatorias
- Usuario
- PerfilUsuario
- Cliente
- OrdemServico
- HistoricoStatus
- HistoricoEtapa
- Iteracao
- Anexo
- OpcaoDepartamento
- OpcaoTipo
- OpcaoCategoria
- OpcaoPrioridade
- OpcaoUrgencia

## Classe Usuario
### Responsabilidade
Representar a conta autenticavel do sistema.

### Atributos principais
- id
- username
- first_name
- last_name
- email
- is_active
- is_superuser

### Relacionamentos
- 1:1 com PerfilUsuario
- 1:1 opcional com Cliente
- 1:N com OrdemServico como criado_por
- 1:N com OrdemServico como atribuido_para
- 1:N com HistoricoStatus como alterado_por
- 1:N com Iteracao como criado_por
- 1:N com Anexo como enviado_por

## Classe PerfilUsuario
### Responsabilidade
Classificar o usuario e vincular departamento interno quando aplicavel.

### Atributos principais
- tipo
- departamento
- criado_em
- atualizado_em

### Tipos
- admin
- tecnico
- somente_cliente

### Relacionamentos
- 1:1 com Usuario
- N:1 com OpcaoDepartamento

## Classe Cliente
### Responsabilidade
Representar o solicitante de negocio.

### Atributos principais
- nome
- email
- telefone
- endereco
- criado_em
- atualizado_em

### Relacionamentos
- 1:1 com Usuario
- N:1 com OpcaoDepartamento
- 1:N com OrdemServico

## Classe OrdemServico
### Responsabilidade
Representar o registro principal do atendimento.

### Atributos principais
- numero
- titulo
- descricao
- status
- etapa
- aberta_em
- status_alterado_em
- valor_total

### Status
- aberta
- aguardando
- em_andamento
- em_avaliacao
- encerrada

### Relacionamentos
- N:1 com Cliente
- N:1 com Usuario como criado_por
- N:1 com Usuario como atribuido_para
- N:1 com OpcaoDepartamento
- N:1 com OpcaoTipo
- N:1 com OpcaoCategoria
- N:1 com OpcaoPrioridade
- N:1 com OpcaoUrgencia
- 1:N com HistoricoStatus
- 1:N com HistoricoEtapa
- 1:N com Iteracao
- 1:N com Anexo

## Classe HistoricoStatus
### Responsabilidade
Registrar mudancas de status do chamado.

### Atributos principais
- status_anterior
- status_novo
- alterado_em
- observacao

### Relacionamentos
- N:1 com OrdemServico
- N:1 com Usuario

## Classe HistoricoEtapa
### Responsabilidade
Registrar mudancas de etapa interna do chamado.

### Atributos principais
- etapa_anterior
- etapa_nova
- alterado_em

### Relacionamentos
- N:1 com OrdemServico
- N:1 com Usuario

## Classe Iteracao
### Responsabilidade
Registrar comentarios e complementos de informacao sobre o chamado.

### Atributos principais
- texto
- criado_em

### Relacionamentos
- N:1 com OrdemServico
- N:1 com Usuario

## Classe Anexo
### Responsabilidade
Registrar arquivos anexados ao chamado.

### Atributos principais
- nome_arquivo
- tipo_conteudo
- tamanho_bytes
- enviado_em

### Relacionamentos
- N:1 com OrdemServico
- N:1 com Usuario

## Classes de apoio

### OpcaoDepartamento
Campos principais:
- nome
- ativo
- criado_em
- atualizado_em

### OpcaoTipo
Campos principais:
- nome
- ativo
- criado_em
- atualizado_em

### OpcaoCategoria
Campos principais:
- nome
- ativo
- criado_em
- atualizado_em

### OpcaoPrioridade
Campos principais:
- nome
- nivel
- ativo
- criado_em
- atualizado_em

### OpcaoUrgencia
Campos principais:
- nome
- nivel
- ativo
- criado_em
- atualizado_em

## Relacionamentos principais para o desenho
- Usuario 1:1 PerfilUsuario
- Usuario 1:1 Cliente
- Cliente 1:N OrdemServico
- OrdemServico N:1 Usuario como criador
- OrdemServico N:1 Usuario como tecnico atribuido
- OrdemServico N:1 OpcaoDepartamento
- OrdemServico N:1 OpcaoTipo
- OrdemServico N:1 OpcaoCategoria
- OrdemServico N:1 OpcaoPrioridade
- OrdemServico N:1 OpcaoUrgencia
- OrdemServico 1:N HistoricoStatus
- OrdemServico 1:N HistoricoEtapa
- OrdemServico 1:N Iteracao
- OrdemServico 1:N Anexo

## Observacoes para o programador
- Cliente e Usuario nao sao a mesma tabela, mas fazem parte do mesmo fluxo de negocio do ator cliente.
- O atributo `tipo` em PerfilUsuario substitui uma heranca classica entre perfis.
- A classe OrdemServico e a entidade central do dominio e deve ficar no centro do diagrama.
