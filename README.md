# SGOS – Sistema de Gestão de Chamados (OS)

Projeto com **frontend estático (HTML/JS)** e **backend Django REST (JWT)**.

- Frontend: `http://localhost:5010/` (principal: `login.html`)
- Backend API: `http://127.0.0.1:8010/api/`

---

## Credenciais (seed)

- Admin (superuser): `admin` / `admin123`
- Funcionário: `rafael` / `rafael123`
- Outros usuários seed (técnicos/exemplos): `gustavo` / `gustavo123`, `ana` / `ana123`, `juliana` / `juliana123`, `bruno` / `bruno123`

---

## Como rodar (Windows)

### Backend (Django)

```powershell
cd .\backend\api
py -m pip install -r requirements.txt
py manage.py migrate
py manage.py seed
py manage.py runserver 0.0.0.0:8010
```

### Frontend (estático)

```powershell
cd .\frontend
py -m http.server 5010
```

Acesse: `http://localhost:5010/login.html`

---

## Script de atalho

Existe o script [start-dev.ps1](file:///c:/Users/Rafael/Desktop/Unicesumar/imers%C3%A3o/sgos/start-dev.ps1) para ajudar a iniciar front/back (padrão: **front 5010** / **back 8010**).

---

## Regras de fluxo (Departamento / Técnico)

- **Toda OS precisa ter um departamento** (obrigatório na criação).
- A OS pertence a **um único departamento**.
- **Usuário não-admin**:
  - Enxerga apenas OS do seu departamento.
  - Só pode criar OS no seu próprio departamento.
- **Atribuição de técnico**:
  - Ao entrar em `em_andamento`, se a OS não tiver `atribuido_para`, o sistema atribui automaticamente para o técnico que avançou (não-admin).
  - Também existe endpoint para atribuir.
- **Descrição do serviço**:
  - Para sair de `em_andamento`, é obrigatório informar uma **descrição do serviço executado** (validação no backend e UI no Kanban).

---

## Frontend (telas principais)

- `login.html` – autenticação
- `dashboard.html` – KPIs e (admin) gestão de técnicos
- `abrir-chamado.html` – abertura de OS (com departamento obrigatório)
- `kanban.html` – Kanban geral
- `kanban.html?view=mine` – “Meus Chamados” (fila, prioridade do dia, KPIs pessoais, histórico recente)

---

## API (principais endpoints)

### Auth (JWT)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/register/` | Cadastrar usuário |
| POST | `/api/auth/login/` | Login (JWT) |
| POST | `/api/auth/refresh/` | Renovar token |
| POST | `/api/auth/logout/` | Logout |
| GET  | `/api/auth/me/` | Usuário logado |
| GET  | `/api/me/overview/` | KPIs/badges e dados do “Meus Chamados” |

### Clientes

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET    | `/api/clientes/` | Listar clientes |
| GET    | `/api/clientes/?search=nome` | Pesquisar |
| POST   | `/api/clientes/` | Cadastrar cliente |
| GET    | `/api/clientes/{id}/` | Detalhar |
| PUT    | `/api/clientes/{id}/` | Editar |
| DELETE | `/api/clientes/{id}/` | Excluir (bloqueia se tiver OS ativa) |

### Ordens de Serviço (OS)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET    | `/api/workorders/` | Listar OS (paginado) |
| GET    | `/api/workorders/?status=aberta` | Filtrar por status |
| GET    | `/api/workorders/?departamento=TI` | Filtrar por departamento (admin) |
| GET    | `/api/workorders/?assigned_to=me` | Minhas OS atribuídas |
| GET    | `/api/workorders/?created_by=me` | OS criadas por mim |
| POST   | `/api/workorders/` | Criar OS (departamento obrigatório) |
| GET    | `/api/workorders/{id}/` | Detalhar OS |
| PATCH  | `/api/workorders/{id}/etapa/` | Avançar status (exige descrição ao sair de `em_andamento`) |
| PATCH  | `/api/workorders/{id}/assign/` | Atribuir técnico (admin escolhe, técnico atribui para si) |
| GET    | `/api/workorders/{id}/iteracoes/` | Listar iterações |
| POST   | `/api/workorders/{id}/iteracoes/` | Adicionar iteração |
| POST   | `/api/workorders/{id}/anexos/` | Upload de anexo |
| DELETE | `/api/workorders/{id}/` | Excluir (apenas encerrada) |

### Utilitários

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/workorders/meta/` | Choices/lookup para formulários |
| GET | `/api/dashboard/` | KPIs e métricas do dashboard |

### Admin (Técnicos)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET/POST | `/api/tecnicos/` | Listar/criar técnicos (somente admin) |
| PATCH/DELETE | `/api/tecnicos/{id}/` | Atualizar/ativar/desativar técnico (somente admin) |

---

## Reset de OS (zerar chamados)

Para apagar todas as OS e dados relacionados (histórico/iterações/anexos):

```powershell
cd .\backend\api
py manage.py shell -c "from core.models import OrdemServico, HistoricoStatus, HistoricoEtapa, Iteracao, Anexo; Anexo.objects.all().delete(); Iteracao.objects.all().delete(); HistoricoEtapa.objects.all().delete(); HistoricoStatus.objects.all().delete(); OrdemServico.objects.all().delete(); print('OK')"
```

---

## Estrutura do projeto

```
frontend/            ← HTML/JS/CSS (servido via http.server)
backend/api/         ← Django (DRF + JWT)
  core/              ← models/serializers/views/urls
  sgos/              ← settings/urls
start-dev.ps1        ← atalho para dev
```
