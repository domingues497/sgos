# SGOS - Backend Django REST API

Backend do SGOS com Django, Django REST Framework e autenticacao JWT.

## Instalacao

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed
python manage.py runserver 0.0.0.0:8010
```

Se preferir, copie `.env.example` para `.env` e configure `DATABASE_URL` ou as variaveis `POSTGRES_*` antes de rodar as migrations.

## Credenciais seed

- Admin: `admin` / `admin123`
- Usuario padrao: `rafael` / `rafael123`
- Tecnicos de exemplo: `gustavo` / `gustavo123`, `ana` / `ana123`, `juliana` / `juliana123`, `bruno` / `bruno123`

## Endpoints principais

### Auth

| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| POST | `/api/auth/register/` | Cadastrar usuario |
| POST | `/api/auth/login/` | Login JWT |
| POST | `/api/auth/refresh/` | Renovar token |
| POST | `/api/auth/logout/` | Logout |
| GET  | `/api/auth/me/` | Dados do usuario logado |
| POST | `/api/auth/reset-password/` | Redefinir senha |
| GET  | `/api/me/overview/` | Visao pessoal e badges de chamados |

### Clientes

| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| GET | `/api/clientes/` | Listar clientes |
| POST | `/api/clientes/` | Cadastrar cliente |
| GET | `/api/clientes/{id}/` | Detalhar cliente |
| PUT | `/api/clientes/{id}/` | Editar cliente |
| DELETE | `/api/clientes/{id}/` | Excluir cliente se nao houver OS ativa |

### Ordens de servico

| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| GET | `/api/workorders/` | Listar OS |
| POST | `/api/workorders/` | Criar OS |
| GET | `/api/workorders/{id}/` | Detalhar OS |
| PATCH | `/api/workorders/{id}/etapa/` | Avancar status |
| PATCH | `/api/workorders/{id}/assign/` | Atribuir tecnico |
| GET | `/api/workorders/{id}/iteracoes/` | Listar iteracoes |
| POST | `/api/workorders/{id}/iteracoes/` | Adicionar iteracao |
| POST | `/api/workorders/{id}/anexos/` | Enviar anexo |
| DELETE | `/api/workorders/{id}/` | Excluir OS encerrada |

### Admin

| Metodo | Endpoint | Descricao |
|--------|----------|-----------|
| GET/POST | `/api/tecnicos/` | Listar ou criar tecnicos |
| PATCH/DELETE | `/api/tecnicos/{id}/` | Atualizar ou desativar tecnico |

## Regras implementadas

- Toda OS exige departamento na abertura.
- Usuario nao admin enxerga apenas chamados do proprio departamento.
- Tecnico pertence a um departamento e so atua nos chamados desse departamento.
- Ao sair de `em_andamento`, a descricao do servico executado e obrigatoria.
- Todos os endpoints privados exigem `Authorization: Bearer <access_token>`.

## Estrutura

```text
backend/api/
  core/
    management/commands/seed.py
    migrations/
    models.py
    serializers.py
    urls.py
    views.py
  sgos/
    settings.py
    urls.py
    wsgi.py
  manage.py
  requirements.txt
```
