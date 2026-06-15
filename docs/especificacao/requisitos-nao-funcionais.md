# Requisitos Nao Funcionais - SGOS

## Objetivo
Este documento descreve os requisitos nao funcionais que orientam arquitetura, seguranca, usabilidade e qualidade do SGOS.

## RNF01 - Arquitetura
O sistema deve operar com frontend web e backend baseado em API REST.

## RNF02 - Seguranca
O sistema deve utilizar autenticacao segura baseada em token JWT ou mecanismo equivalente.

## RNF03 - Autorizacao
As regras de permissao devem ser aplicadas no backend, nao apenas na interface.

## RNF04 - Rastreabilidade
O sistema deve manter trilha minima de auditoria das alteracoes relevantes do chamado.

## RNF05 - Usabilidade
As telas devem possuir padrao visual consistente, boa legibilidade e navegacao adequada ao perfil do usuario.

## RNF06 - Responsividade
As interfaces devem funcionar adequadamente em diferentes tamanhos de tela utilizados no ambiente web.

## RNF07 - Manutenibilidade
Cadastros auxiliares nao devem ser fixos no codigo da interface; devem ser mantidos por configuracao administrativa.

## RNF08 - Integridade dos dados
Relacionamentos entre cliente, usuario, chamado e departamento devem ser protegidos por validacoes de dominio.

## RNF09 - Consistencia documental
Os nomes das entidades, atores, regras e fluxos devem ser mantidos de forma uniforme entre codigo e documentacao.

## RNF10 - Escalabilidade funcional
O sistema deve permitir evolucao de novos cadastros, relatorios e regras sem quebra estrutural do dominio principal.

## RNF11 - Performance percebida
As consultas principais devem suportar paginacao, filtros e respostas adequadas para o uso cotidiano.

## RNF12 - Portabilidade
O sistema deve ser executavel em ambiente local e em ambiente de nuvem.

## RNF13 - Compatibilidade web
O frontend deve funcionar em navegadores modernos suportados pelo ambiente institucional.

## RNF14 - Auditabilidade
Mudancas de status e interacoes devem permanecer disponiveis para consulta historica.

## RNF15 - Segregacao por perfil
A experiencia da aplicacao deve ser diferente para administrador, tecnico e cliente, respeitando as restricoes de acesso e operacao.
