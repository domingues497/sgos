# SGOS – Sistema de Gestão de Ordens de Serviço
## Backend Django REST API

### Instalação

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed          # popula dados de exemplo
python manage.py runserver
```

Credenciais de acesso:
- Admin: `admin` / `admin123`
- Funcionário: `gustavo` / `gustavo123`

---

### Endpoints da API

#### Auth
| Método | Endpoint | Descrição | RF |
|--------|----------|-----------|-----|
| POST | `/api/auth/register/` | Cadastrar usuário | RF001 |
| POST | `/api/auth/login/` | Login (retorna JWT) | RF002 |
| POST | `/api/auth/refresh/` | Renovar token | — |
| POST | `/api/auth/logout/` | Logout (blacklist) | — |
| GET  | `/api/auth/me/` | Dados do usuário logado | — |

#### Clientes
| Método | Endpoint | Descrição | RF |
|--------|----------|-----------|-----|
| GET    | `/api/clientes/` | Listar clientes | RF010 |
| GET    | `/api/clientes/?search=nome` | Pesquisar por nome | RF010 |
| POST   | `/api/clientes/` | Cadastrar cliente | RF004 |
| GET    | `/api/clientes/{id}/` | Detalhar cliente | RF009 |
| PUT    | `/api/clientes/{id}/` | Editar cliente | RF005 |
| DELETE | `/api/clientes/{id}/` | Excluir cliente (RN001) | RF006 |

#### Ordens de Serviço
| Método | Endpoint | Descrição | RF |
|--------|----------|-----------|-----|
| GET    | `/api/workorders/` | Listar OS | RF011 |
| GET    | `/api/workorders/?search=termo` | Pesquisar OS | RF011 |
| GET    | `/api/workorders/?status=aberta` | Filtrar por status | — |
| POST   | `/api/workorders/` | Criar OS (RN002/RN003) | RF007 |
| GET    | `/api/workorders/{id}/` | Detalhar OS | RF009 |
| DELETE | `/api/workorders/{id}/` | Excluir OS encerrada | RF012 |
| PATCH  | `/api/workorders/{id}/etapa/` | Avançar status (RN004) | RF008 |
| GET    | `/api/workorders/{id}/iteracoes/` | Listar iterações | — |
| POST   | `/api/workorders/{id}/iteracoes/` | Adicionar iteração | — |
| POST   | `/api/workorders/{id}/anexos/` | Upload de anexo | — |

#### Utilitários
| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/workorders/meta/` | Choices para formulários |
| GET | `/api/dashboard/` | KPIs e métricas |

---

### Regras de Negócio implementadas

| RN | Implementação |
|----|---------------|
| RN001 | `DELETE /clientes/{id}/` retorna 400 se o cliente tem OS ativa |
| RN002 | Serializer valida que o cliente existe antes de criar OS |
| RN003 | Status inicial sempre `aberta`; data registrada via `auto_now_add` |
| RN004 | `AvancarStatusView` só permite avançar, nunca retroceder |
| RN005 | Todos os endpoints exigem JWT (`IsAuthenticated`) |
| RN006 | OS encerrada não aceita edição, iterações ou anexos |
| RN007 | `UniqueValidator` no campo `username` do `RegisterSerializer` |

---

### Autenticação JWT

Todas as rotas (exceto `/api/auth/register/` e `/api/auth/login/`) exigem:

```
Authorization: Bearer <access_token>
```

O token de acesso expira em **8 horas**. Use `/api/auth/refresh/` com o `refresh` token para renovar.

---

### Estrutura do Projeto

```
sgos/               ← configurações Django
core/
  models.py         ← Cliente, OrdemServico, HistoricoStatus, Iteracao, Anexo
  serializers.py    ← serializers DRF
  views.py          ← endpoints
  urls.py           ← rotas da API
  admin.py          ← painel administrativo
  management/
    commands/
      seed.py       ← dados de exemplo
```

---

## Banco de Dados PostgreSQL

```bash
# 1. Instale o PostgreSQL e crie o banco
createdb sgos
# 2. Configure variáveis de ambiente
cp .env.example .env
# edite .env com suas credenciais

# 3. Execute o schema SQL (cria tabelas, índices, triggers e views)
psql -U <SEU_USUARIO> -d sgos -f init.sql

# 4. Execute as migrations Django (tabelas do admin/auth)
python manage.py migrate

# 5. Popula dados iniciais
python manage.py seed

# 6. Sobe o servidor
python manage.py runserver
```

---

### Schema do Banco — Tabelas

| Tabela | Descrição |
|--------|-----------|
| `clientes` | Clientes cadastrados |
| `ordens_servico` | OS com timestamps por status, etapa, valor_total |
| `os_historico_status` | Cada mudança de status registrada |
| `os_historico_etapas` | Cada mudança de etapa interna |
| `os_iteracoes` | Comentários/iterações da OS |
| `os_anexos` | Arquivos anexados |
| `os_anotacoes_erp` | Anotações de integração ERP |
| `os_opcoes_urgencia` | Lookup: níveis de urgência |
| `os_opcoes_prioridade` | Lookup: níveis de prioridade |
| `os_opcoes_departamento` | Lookup: departamentos |
| `os_opcoes_tipo` | Lookup: tipos de OS |
| `os_opcoes_categoria` | Lookup: categorias |
| `usuarios_perfis` | Perfil estendido do usuário (departamento) |

### Views SQL criadas

| View | Descrição |
|------|-----------|
| `vw_kanban` | OS com dados de cliente e usuários para o painel Kanban |
| `vw_dashboard_kpis` | Contadores por status + média de horas de resolução |

### Triggers

- `trg_clientes_atualizado` — atualiza `atualizado_em` em clientes
- `trg_os_status_alterado` — atualiza `status_alterado_em` em OS
