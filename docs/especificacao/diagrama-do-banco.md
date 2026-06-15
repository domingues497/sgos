# Diagrama do Banco - Base de Modelagem

## Objetivo
Este documento serve como referencia textual para o desenho do diagrama do banco de dados do SGOS.

## Tabelas principais
- auth_user
- usuarios_perfis
- clientes
- ordens_servico
- os_historico_status
- os_historico_etapas
- os_iteracoes
- os_anexos
- os_anotacoes_erp
- os_opcoes_departamento
- os_opcoes_tipo
- os_opcoes_categoria
- os_opcoes_prioridade
- os_opcoes_urgencia

## 1. auth_user
### Finalidade
Armazenar a identidade autenticavel do sistema.

### Campos relevantes
- id
- username
- first_name
- last_name
- email
- is_active
- is_superuser

## 2. usuarios_perfis
### Finalidade
Classificar o tipo do usuario e associar departamento interno quando aplicavel.

### Campos relevantes
- id
- usuario_id
- tipo
- departamento_id
- criado_em
- atualizado_em

### Relacoes
- usuario_id -> auth_user.id
- departamento_id -> os_opcoes_departamento.id

## 3. clientes
### Finalidade
Armazenar os dados de negocio do cliente.

### Campos relevantes
- id
- nome
- email
- telefone
- endereco
- usuario_id
- departamento_id
- criado_em
- atualizado_em

### Relacoes
- usuario_id -> auth_user.id
- departamento_id -> os_opcoes_departamento.id

## 4. ordens_servico
### Finalidade
Armazenar o chamado principal.

### Campos relevantes
- id
- numero
- titulo
- descricao
- status
- prioridade_id
- tipo_id
- categoria_id
- urgencia_id
- departamento_id
- etapa
- etapa_alterada_em
- cliente_id
- criado_por_id
- atribuido_para_id
- valor_total
- aberta_em
- status_alterado_em

### Relacoes
- cliente_id -> clientes.id
- criado_por_id -> auth_user.id
- atribuido_para_id -> auth_user.id
- departamento_id -> os_opcoes_departamento.id
- tipo_id -> os_opcoes_tipo.id
- categoria_id -> os_opcoes_categoria.id
- prioridade_id -> os_opcoes_prioridade.id
- urgencia_id -> os_opcoes_urgencia.id

## 5. os_historico_status
### Finalidade
Registrar mudancas de status dos chamados.

### Campos relevantes
- id
- os_id
- status_anterior
- status_novo
- alterado_por_id
- alterado_em
- observacao

### Relacoes
- os_id -> ordens_servico.id
- alterado_por_id -> auth_user.id

## 6. os_historico_etapas
### Finalidade
Registrar mudancas de etapa interna do chamado.

### Campos relevantes
- id
- os_id
- etapa_anterior
- etapa_nova
- alterado_por_id
- alterado_em

### Relacoes
- os_id -> ordens_servico.id
- alterado_por_id -> auth_user.id

## 7. os_iteracoes
### Finalidade
Registrar comentarios e comunicacoes dentro do chamado.

### Campos relevantes
- id
- os_id
- texto
- criado_em
- criado_por_id

### Relacoes
- os_id -> ordens_servico.id
- criado_por_id -> auth_user.id

## 8. os_anexos
### Finalidade
Registrar arquivos enviados no contexto do chamado.

### Campos relevantes
- id
- os_id
- arquivo
- nome_arquivo
- tipo_conteudo
- tamanho_bytes
- enviado_por_id
- enviado_em

### Relacoes
- os_id -> ordens_servico.id
- enviado_por_id -> auth_user.id

## 9. os_anotacoes_erp
### Finalidade
Registrar anotacoes oriundas de integracao externa.

### Campos relevantes
- id
- cod_os
- anotacao
- criado_em
- atualizado_em
- criado_por_id

## 10. Tabelas de apoio

### os_opcoes_departamento
- id
- nome
- ativo
- criado_em
- atualizado_em

### os_opcoes_tipo
- id
- nome
- ativo
- criado_em
- atualizado_em

### os_opcoes_categoria
- id
- nome
- ativo
- criado_em
- atualizado_em

### os_opcoes_prioridade
- id
- nome
- nivel
- ativo
- criado_em
- atualizado_em

### os_opcoes_urgencia
- id
- nome
- nivel
- ativo
- criado_em
- atualizado_em

## Cardinalidades para o desenho
- auth_user 1:1 usuarios_perfis
- auth_user 1:1 clientes
- clientes 1:N ordens_servico
- auth_user 1:N ordens_servico como criado_por
- auth_user 1:N ordens_servico como atribuido_para
- ordens_servico 1:N os_historico_status
- ordens_servico 1:N os_historico_etapas
- ordens_servico 1:N os_iteracoes
- ordens_servico 1:N os_anexos
- os_opcoes_departamento 1:N clientes
- os_opcoes_departamento 1:N usuarios_perfis
- os_opcoes_departamento 1:N ordens_servico
- os_opcoes_tipo 1:N ordens_servico
- os_opcoes_categoria 1:N ordens_servico
- os_opcoes_prioridade 1:N ordens_servico
- os_opcoes_urgencia 1:N ordens_servico

## Observacoes para o diagrama
- `ordens_servico` e a tabela central.
- `clientes` e `auth_user` possuem vinculo 1:1 no processo de negocio do cliente.
- `usuarios_perfis` especializa o usuario por atributo `tipo`.
- As tabelas `os_opcoes_*` devem ser representadas como tabelas de dominio parametrizavel.
