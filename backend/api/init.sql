-- ============================================================
--  SGOS – Schema PostgreSQL
--  Espelha fielmente o diagrama postgres_-_public.png
--  Execute: psql -U sgos_user -d sgos -f init.sql
-- ============================================================

-- Extensão para UUIDs (opcional, mantemos bigserial padrão)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Tabelas de Opções (lookup tables) ─────────────────────────────────────────

CREATE TABLE IF NOT EXISTS os_opcoes_urgencia (
    id            BIGSERIAL PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL UNIQUE,
    ativo         BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    nivel         SMALLINT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS os_opcoes_prioridade (
    id            BIGSERIAL PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL UNIQUE,
    ativo         BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    nivel         SMALLINT NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS os_opcoes_departamento (
    id            BIGSERIAL PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL UNIQUE,
    ativo         BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS os_opcoes_tipo (
    id            BIGSERIAL PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL UNIQUE,
    ativo         BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS os_opcoes_categoria (
    id            BIGSERIAL PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL UNIQUE,
    ativo         BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Clientes ──────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS clientes (
    id            BIGSERIAL PRIMARY KEY,
    nome          VARCHAR(200) NOT NULL,
    email         VARCHAR(254) NOT NULL,
    telefone      VARCHAR(20)  NOT NULL,
    endereco      VARCHAR(300) NOT NULL DEFAULT '',
    criado_em     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    atualizado_em TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clientes_nome ON clientes (nome);

-- ── Ordens de Serviço ─────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS ordens_servico (
    id                 BIGSERIAL PRIMARY KEY,
    numero             VARCHAR(20)     NOT NULL UNIQUE,
    titulo             VARCHAR(200)    NOT NULL,
    descricao          TEXT            NOT NULL,

    -- Workflow principal (RN003: default 'aberta')
    status             VARCHAR(20)     NOT NULL DEFAULT 'aberta'
                           CHECK (status IN ('aberta','aguardando','em_andamento','em_avaliacao','encerrada')),

    -- Classificação (nomes livres alinhados com tabelas de opções)
    prioridade         VARCHAR(100)    NOT NULL DEFAULT '',
    tipo               VARCHAR(100)    NOT NULL DEFAULT '',
    categoria          VARCHAR(100)    NOT NULL DEFAULT '',
    urgencia           VARCHAR(100)    NOT NULL DEFAULT '',
    departamento       VARCHAR(100)    NOT NULL DEFAULT '',

    -- Etapa interna (sub-estágio)
    etapa              VARCHAR(100)    NOT NULL DEFAULT '',
    etapa_alterada_em  TIMESTAMPTZ,

    -- Relacionamentos
    cliente_id         BIGINT          NOT NULL REFERENCES clientes(id) ON DELETE RESTRICT,
    criado_por_id      INTEGER         REFERENCES auth_user(id) ON DELETE SET NULL,
    atribuido_para_id  INTEGER         REFERENCES auth_user(id) ON DELETE SET NULL,

    -- Financeiro
    valor_total        NUMERIC(10, 2),

    -- Timestamps por status (diagrama)
    aberta_em          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    status_alterado_em TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    aguardando_em      TIMESTAMPTZ,
    em_andamento_em    TIMESTAMPTZ,
    avaliacao_em       TIMESTAMPTZ,
    encerrada_em       TIMESTAMPTZ,
    fechada_em         TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_os_status      ON ordens_servico (status);
CREATE INDEX IF NOT EXISTS idx_os_cliente     ON ordens_servico (cliente_id);
CREATE INDEX IF NOT EXISTS idx_os_criado_por  ON ordens_servico (criado_por_id);
CREATE INDEX IF NOT EXISTS idx_os_aberta_em   ON ordens_servico (aberta_em DESC);

-- ── Histórico de Status ───────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS os_historico_status (
    id              BIGSERIAL PRIMARY KEY,
    status_anterior VARCHAR(20)  NOT NULL DEFAULT '',
    status_novo     VARCHAR(20)  NOT NULL,
    alterado_em     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    alterado_por_id INTEGER      REFERENCES auth_user(id) ON DELETE SET NULL,
    os_id           BIGINT       NOT NULL REFERENCES ordens_servico(id) ON DELETE CASCADE,
    observacao      TEXT         NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_hist_status_os ON os_historico_status (os_id);

-- ── Histórico de Etapas ───────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS os_historico_etapas (
    id              BIGSERIAL PRIMARY KEY,
    etapa_anterior  VARCHAR(100) NOT NULL DEFAULT '',
    etapa_nova      VARCHAR(100) NOT NULL,
    alterado_em     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    alterado_por_id INTEGER      REFERENCES auth_user(id) ON DELETE SET NULL,
    os_id           BIGINT       NOT NULL REFERENCES ordens_servico(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_hist_etapas_os ON os_historico_etapas (os_id);

-- ── Iterações / Comentários ───────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS os_iteracoes (
    id           BIGSERIAL PRIMARY KEY,
    texto        TEXT        NOT NULL,
    criado_em    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    criado_por_id INTEGER    REFERENCES auth_user(id) ON DELETE SET NULL,
    os_id        BIGINT      NOT NULL REFERENCES ordens_servico(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_iteracoes_os ON os_iteracoes (os_id);

-- ── Anexos ────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS os_anexos (
    id             BIGSERIAL PRIMARY KEY,
    arquivo        VARCHAR(255) NOT NULL,
    nome_arquivo   VARCHAR(255) NOT NULL,
    tipo_conteudo  VARCHAR(100) NOT NULL,
    tamanho_bytes  INTEGER      NOT NULL,
    enviado_em     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    enviado_por_id INTEGER      REFERENCES auth_user(id) ON DELETE SET NULL,
    os_id          BIGINT       NOT NULL REFERENCES ordens_servico(id) ON DELETE CASCADE
);

-- ── Anotações ERP ─────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS os_anotacoes_erp (
    id             BIGSERIAL PRIMARY KEY,
    cod_os         VARCHAR(30)  NOT NULL,
    anotacao       TEXT         NOT NULL,
    criado_em      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    atualizado_em  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    criado_por_id  INTEGER      REFERENCES auth_user(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_anotacoes_erp_cod ON os_anotacoes_erp (cod_os);

-- ── Perfis de Usuário ─────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS usuarios_perfis (
    id             BIGSERIAL PRIMARY KEY,
    departamento   VARCHAR(100) NOT NULL DEFAULT '',
    criado_em      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    atualizado_em  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    usuario_id     INTEGER      NOT NULL UNIQUE REFERENCES auth_user(id) ON DELETE CASCADE
);

-- ── Dados iniciais (opções) ────────────────────────────────────────────────────

INSERT INTO os_opcoes_urgencia (nome, nivel) VALUES
  ('Baixa',    1),
  ('Média',    2),
  ('Alta',     3),
  ('Imediata', 4)
ON CONFLICT (nome) DO NOTHING;

INSERT INTO os_opcoes_prioridade (nome, nivel) VALUES
  ('Baixa',   1),
  ('Média',   2),
  ('Alta',    3),
  ('Crítica', 4)
ON CONFLICT (nome) DO NOTHING;

INSERT INTO os_opcoes_departamento (nome) VALUES
  ('TI'), ('Suporte'), ('Financeiro'), ('RH'), ('Comercial'), ('Operações')
ON CONFLICT (nome) DO NOTHING;

INSERT INTO os_opcoes_tipo (nome) VALUES
  ('Incidente'), ('Solicitação de Serviço'), ('Problema'), ('Manutenção')
ON CONFLICT (nome) DO NOTHING;

INSERT INTO os_opcoes_categoria (nome) VALUES
  ('Hardware'), ('Software'), ('Rede'), ('Acesso'), ('Banco de Dados'), ('Outros')
ON CONFLICT (nome) DO NOTHING;

-- ── Função: atualizar atualizado_em automaticamente ─────────────────────────

CREATE OR REPLACE FUNCTION set_atualizado_em()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
  NEW.atualizado_em = NOW();
  RETURN NEW;
END;
$$;

-- Triggers
DO $$ BEGIN
  CREATE TRIGGER trg_clientes_atualizado
    BEFORE UPDATE ON clientes
    FOR EACH ROW EXECUTE FUNCTION set_atualizado_em();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE TRIGGER trg_os_status_alterado
    BEFORE UPDATE ON ordens_servico
    FOR EACH ROW EXECUTE FUNCTION set_atualizado_em();
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ── View: resumo Kanban ────────────────────────────────────────────────────────

CREATE OR REPLACE VIEW vw_kanban AS
SELECT
    os.id,
    os.numero,
    os.titulo,
    os.status,
    os.prioridade,
    os.tipo,
    os.categoria,
    os.urgencia,
    os.departamento,
    os.etapa,
    os.valor_total,
    os.aberta_em,
    os.encerrada_em,
    c.nome  AS cliente_nome,
    c.email AS cliente_email,
    u.username AS criado_por,
    a.username AS atribuido_para
FROM ordens_servico os
JOIN clientes c      ON c.id = os.cliente_id
LEFT JOIN auth_user u ON u.id = os.criado_por_id
LEFT JOIN auth_user a ON a.id = os.atribuido_para_id;

-- ── View: dashboard KPIs ──────────────────────────────────────────────────────

CREATE OR REPLACE VIEW vw_dashboard_kpis AS
SELECT
    COUNT(*)                                        AS total,
    COUNT(*) FILTER (WHERE status = 'aberta')       AS aberta,
    COUNT(*) FILTER (WHERE status = 'aguardando')   AS aguardando,
    COUNT(*) FILTER (WHERE status = 'em_andamento') AS em_andamento,
    COUNT(*) FILTER (WHERE status = 'em_avaliacao') AS em_avaliacao,
    COUNT(*) FILTER (WHERE status = 'encerrada')    AS encerrada,
    AVG(EXTRACT(EPOCH FROM (encerrada_em - aberta_em))/3600)
                                                    AS media_horas_resolucao
FROM ordens_servico;

