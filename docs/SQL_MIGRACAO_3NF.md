# 🗄️ IMPLEMENTAÇÃO PRÁTICA — MIGRAÇÃO PARA 3NF
## Scripts SQL e Exemplos Django

---

## 📊 DIAGRAMA COMPARATIVO

### ❌ ESTADO ATUAL (Desnormalizado)

```
┌──────────────────────────────────────────────────────────────────────┐
│                       ordens_servico (REDUNDANTE)                    │
├──────────────────────────────────────────────────────────────────────┤
│ id (PK)                                                              │
│ numero, titulo, descricao                                            │
│ status VARCHAR          ← Sem FK (valores string repetidos)          │
│ prioridade VARCHAR      ← Sem FK (valores string repetidos)          │
│ tipo VARCHAR            ← Sem FK (valores string repetidos)          │
│ categoria VARCHAR       ← Sem FK (valores string repetidos)          │
│ urgencia VARCHAR        ← Sem FK (valores string repetidos)          │
│ departamento VARCHAR    ← Sem FK (valores string repetidos)          │
│ ──────────────────────────────────────────────────────────────────── │
│ aberta_em TIMESTAMP     ← Redundante (Dep. de status='aberta')      │
│ aguardando_em TIMESTAMP ← Redundante (Dep. de status='aguardando')  │
│ em_andamento_em TIMESTAMP ← Redundante (Dep. status='em_andamento') │
│ avaliacao_em TIMESTAMP  ← Redundante (Dep. de status='avaliacao')  │
│ encerrada_em TIMESTAMP  ← Redundante (Dep. de status='encerrada')  │
│ fechada_em TIMESTAMP    ← Redundante (Dep. de status='fechada')    │
│ ──────────────────────────────────────────────────────────────────── │
│ cliente_id FK                                                        │
│ criado_por_id FK                                                     │
│ atribuido_para_id FK                                                 │
└──────────────────────────────────────────────────────────────────────┘

Problemas: 6 violações de 3NF, sem integridade referencial
```

### ✅ ESTADO NOVO (3NF Completo)

```
┌────────────────────────────────────────────┐
│       ordens_servico (NORMALIZADO)         │
├────────────────────────────────────────────┤
│ id (PK)                                    │
│ numero, titulo, descricao                  │
│ prioridade_id FK → os_opcoes_prioridade    │
│ tipo_id FK → os_opcoes_tipo                │
│ categoria_id FK → os_opcoes_categoria      │
│ urgencia_id FK → os_opcoes_urgencia        │
│ departamento_id FK → os_opcoes_departamento│
│ status VARCHAR (apenas estado atual)       │
│ etapa VARCHAR                              │
│ valor_total NUMERIC                        │
│ cliente_id FK → clientes                   │
│ criado_por_id FK → usuarios                │
│ atribuido_para_id FK → usuarios            │
│ criado_em TIMESTAMP                        │
│ status_alterado_em TIMESTAMP (atualizado)  │
└────────────────────────────────────────────┘
         │      │      │      │      │
         └──┬───┴──┬───┴──┬───┴──┬───┘
         ┌──────────────┐
         │ os_status_timeline (NOVO) │
         ├──────────────┤
         │ id (PK)      │
         │ os_id FK     │
         │ status_novo  │
         │ timestamp    │
         │ alterado_por │
         │ observacao   │
         └──────────────┘

Benefício: Histórico automático, sem redundância, 3NF garantida
```

---

## 🔧 SCRIPTS DE MIGRAÇÃO

### PASSO 1: Criar Tabelas de Lookup Melhoradas

```sql
-- ✅ Melhorar tabelas de lookup com IDs numéricos
ALTER TABLE os_opcoes_prioridade ADD COLUMN id SERIAL UNIQUE;
ALTER TABLE os_opcoes_prioridade ADD COLUMN nome VARCHAR(50) UNIQUE NOT NULL;
UPDATE os_opcoes_prioridade SET nome = descricao WHERE nome IS NULL;

ALTER TABLE os_opcoes_urgencia ADD COLUMN id SERIAL UNIQUE;
ALTER TABLE os_opcoes_urgencia ADD COLUMN nome VARCHAR(50) UNIQUE NOT NULL;

ALTER TABLE os_opcoes_tipo ADD COLUMN id SERIAL UNIQUE;
ALTER TABLE os_opcoes_tipo ADD COLUMN nome VARCHAR(50) UNIQUE NOT NULL;

ALTER TABLE os_opcoes_categoria ADD COLUMN id SERIAL UNIQUE;
ALTER TABLE os_opcoes_categoria ADD COLUMN nome VARCHAR(50) UNIQUE NOT NULL;

ALTER TABLE os_opcoes_departamento ADD COLUMN id SERIAL UNIQUE;
ALTER TABLE os_opcoes_departamento ADD COLUMN nome VARCHAR(50) UNIQUE NOT NULL;
```

### PASSO 2: Criar Tabela de Timeline de Status (NOVO)

```sql
-- ✅ Criar tabela para rastrear histórico de status
CREATE TABLE os_status_timeline (
    id SERIAL PRIMARY KEY,
    os_id INT NOT NULL REFERENCES ordens_servico(id) ON DELETE CASCADE,
    
    status_anterior VARCHAR(50) NOT NULL,
    status_novo VARCHAR(50) NOT NULL,
    
    timestamp_transicao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    alterado_por_id INT REFERENCES usuarios(id) ON DELETE SET NULL,
    observacao TEXT,
    
    -- Garantir que cada OS + timestamp seja único
    UNIQUE(os_id, timestamp_transicao),
    
    -- Índices para performance
    INDEX idx_os_id (os_id),
    INDEX idx_timestamp (timestamp_transicao)
);

-- Índices adicionais para performance
CREATE INDEX idx_os_status_novo ON os_status_timeline(status_novo);
CREATE INDEX idx_os_alterado_por ON os_status_timeline(alterado_por_id);
```

### PASSO 3: Migrar Dados Históricos

```sql
-- ✅ Preencher timeline com dados do histórico existente
INSERT INTO os_status_timeline 
(os_id, status_anterior, status_novo, timestamp_transicao, alterado_por_id, observacao)
SELECT 
    os_id,
    status_anterior,
    status_novo,
    alterado_em,
    alterado_por_id,
    observacao
FROM os_historico_status
ORDER BY os_id, alterado_em;
```

### PASSO 4: Adicionar Colunas de ID nas Lookup Tables

```sql
-- ✅ Adicionar as novas colunas de FK à tabela ordens_servico
ALTER TABLE ordens_servico 
ADD COLUMN prioridade_id INT DEFAULT NULL,
ADD COLUMN tipo_id INT DEFAULT NULL,
ADD COLUMN categoria_id INT DEFAULT NULL,
ADD COLUMN urgencia_id INT DEFAULT NULL,
ADD COLUMN departamento_id INT DEFAULT NULL;

-- ✅ Preencher com IDs baseado nos valores atuais (string)
UPDATE ordens_servico os
SET prioridade_id = (SELECT id FROM os_opcoes_prioridade WHERE nome = os.prioridade LIMIT 1)
WHERE prioridade IS NOT NULL AND prioridade_id IS NULL;

UPDATE ordens_servico os
SET tipo_id = (SELECT id FROM os_opcoes_tipo WHERE nome = os.tipo LIMIT 1)
WHERE tipo IS NOT NULL AND tipo_id IS NULL;

UPDATE ordens_servico os
SET categoria_id = (SELECT id FROM os_opcoes_categoria WHERE nome = os.categoria LIMIT 1)
WHERE categoria IS NOT NULL AND categoria_id IS NULL;

UPDATE ordens_servico os
SET urgencia_id = (SELECT id FROM os_opcoes_urgencia WHERE nome = os.urgencia LIMIT 1)
WHERE urgencia IS NOT NULL AND urgencia_id IS NULL;

UPDATE ordens_servico os
SET departamento_id = (SELECT id FROM os_opcoes_departamento WHERE nome = os.departamento LIMIT 1)
WHERE departamento IS NOT NULL AND departamento_id IS NULL;
```

### PASSO 5: Adicionar Foreign Keys

```sql
-- ✅ Adicionar constraints de FK
ALTER TABLE ordens_servico
ADD CONSTRAINT fk_os_prioridade_id 
FOREIGN KEY (prioridade_id) REFERENCES os_opcoes_prioridade(id);

ALTER TABLE ordens_servico
ADD CONSTRAINT fk_os_tipo_id 
FOREIGN KEY (tipo_id) REFERENCES os_opcoes_tipo(id);

ALTER TABLE ordens_servico
ADD CONSTRAINT fk_os_categoria_id 
FOREIGN KEY (categoria_id) REFERENCES os_opcoes_categoria(id);

ALTER TABLE ordens_servico
ADD CONSTRAINT fk_os_urgencia_id 
FOREIGN KEY (urgencia_id) REFERENCES os_opcoes_urgencia(id);

ALTER TABLE ordens_servico
ADD CONSTRAINT fk_os_departamento_id 
FOREIGN KEY (departamento_id) REFERENCES os_opcoes_departamento(id);
```

### PASSO 6: Criar VIEW para Compatibilidade com Código Existente

```sql
-- ✅ VIEW para recuperar timestamps por status (sem redundância física)
CREATE VIEW vw_os_timestamps AS
SELECT 
    os.id,
    os.numero,
    os.criado_em,
    
    -- Timestamps de cada status (extraído do timeline)
    MAX(CASE WHEN ost.status_novo = 'aberta' 
        THEN ost.timestamp_transicao END) as aberta_em,
        
    MAX(CASE WHEN ost.status_novo = 'aguardando' 
        THEN ost.timestamp_transicao END) as aguardando_em,
        
    MAX(CASE WHEN ost.status_novo = 'em_andamento' 
        THEN ost.timestamp_transicao END) as em_andamento_em,
        
    MAX(CASE WHEN ost.status_novo = 'avaliacao' 
        THEN ost.timestamp_transicao END) as avaliacao_em,
        
    MAX(CASE WHEN ost.status_novo = 'encerrada' 
        THEN ost.timestamp_transicao END) as encerrada_em,
        
    MAX(CASE WHEN ost.status_novo = 'fechada' 
        THEN ost.timestamp_transicao END) as fechada_em
        
FROM ordens_servico os
LEFT JOIN os_status_timeline ost ON os.id = ost.os_id
GROUP BY os.id, os.numero, os.criado_em;

-- ✅ VIEW para listar OS com todas as informações normalizadas
CREATE VIEW vw_ordens_servico_completas AS
SELECT 
    os.id,
    os.numero,
    os.titulo,
    os.descricao,
    os.status,
    os.valor_total,
    os.criado_em,
    os.status_alterado_em,
    
    -- Nomes das opcoes (JOIN automático)
    p.nome as prioridade,
    t.nome as tipo,
    c.nome as categoria,
    u.nome as urgencia,
    d.nome as departamento,
    
    -- Dados de cliente
    cli.nome as cliente_nome,
    cli.email as cliente_email,
    cli.telefone as cliente_telefone,
    
    -- Dados de usuarios
    usu_criador.username as criado_por,
    usu_atribuido.username as atribuido_para
    
FROM ordens_servico os
LEFT JOIN os_opcoes_prioridade p ON os.prioridade_id = p.id
LEFT JOIN os_opcoes_tipo t ON os.tipo_id = t.id
LEFT JOIN os_opcoes_categoria c ON os.categoria_id = c.id
LEFT JOIN os_opcoes_urgencia u ON os.urgencia_id = u.id
LEFT JOIN os_opcoes_departamento d ON os.departamento_id = d.id
LEFT JOIN clientes cli ON os.cliente_id = cli.id
LEFT JOIN usuarios usu_criador ON os.criado_por_id = usu_criador.id
LEFT JOIN usuarios usu_atribuido ON os.atribuido_para_id = usu_atribuido.id;
```

### PASSO 7: Atualizar Triggers

```sql
-- ✅ Trigger melhorado para registrar mudanças de status
CREATE OR REPLACE FUNCTION registrar_mudanca_status()
RETURNS TRIGGER AS $$
BEGIN
    -- Registrar mudança no timeline
    INSERT INTO os_status_timeline 
    (os_id, status_anterior, status_novo, timestamp_transicao, alterado_por_id)
    VALUES 
    (NEW.id, OLD.status, NEW.status, NOW(), NULL);
    
    -- Atualizar timestamp de alteracao
    NEW.status_alterado_em = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER trg_os_status_alterado
BEFORE UPDATE ON ordens_servico
FOR EACH ROW
WHEN (OLD.status IS DISTINCT FROM NEW.status)
EXECUTE FUNCTION registrar_mudanca_status();
```

### PASSO 8: Deprecar Colunas Antigas (Não Deletar Imediatamente)

```sql
-- ✅ Manter colunas antigas por 1 ciclo de release, depois deletar
-- Adicionar comentário para alertar
COMMENT ON COLUMN ordens_servico.prioridade IS 'DEPRECADO: Usar prioridade_id ao invés';
COMMENT ON COLUMN ordens_servico.tipo IS 'DEPRECADO: Usar tipo_id ao invés';
COMMENT ON COLUMN ordens_servico.categoria IS 'DEPRECADO: Usar categoria_id ao invés';
COMMENT ON COLUMN ordens_servico.urgencia IS 'DEPRECADO: Usar urgencia_id ao invés';
COMMENT ON COLUMN ordens_servico.departamento IS 'DEPRECADO: Usar departamento_id ao invés';
COMMENT ON COLUMN ordens_servico.aberta_em IS 'DEPRECADO: Usar vw_os_timestamps ao invés';
COMMENT ON COLUMN ordens_servico.aguardando_em IS 'DEPRECADO: Usar vw_os_timestamps ao invés';
COMMENT ON COLUMN ordens_servico.em_andamento_em IS 'DEPRECADO: Usar vw_os_timestamps ao invés';
COMMENT ON COLUMN ordens_servico.avaliacao_em IS 'DEPRECADO: Usar vw_os_timestamps ao invés';
COMMENT ON COLUMN ordens_servico.encerrada_em IS 'DEPRECADO: Usar vw_os_timestamps ao invés';
COMMENT ON COLUMN ordens_servico.fechada_em IS 'DEPRECADO: Usar vw_os_timestamps ao invés';
```

---

## 🐍 ATUALIZAÇÃO DOS MODELS DJANGO

### Antes (Desnormalizado)

```python
# models.py
class OrdemServico(models.Model):
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('aguardando', 'Aguardando'),
        ('em_andamento', 'Em Andamento'),
        ('avaliacao', 'Em Avaliação'),
        ('encerrada', 'Encerrada'),
        ('fechada', 'Fechada'),
    ]
    
    numero = models.CharField(max_length=20, unique=True)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    
    # ❌ Sem FK (strings diretas)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    prioridade = models.CharField(max_length=50)  # "Alta", "Média"...
    tipo = models.CharField(max_length=50)        # "Incidente", "Solicitação"...
    categoria = models.CharField(max_length=50)   # "Hardware", "Software"...
    urgencia = models.CharField(max_length=50)    # "Imediata", "Alta"...
    departamento = models.CharField(max_length=50) # "TI", "Suporte"...
    
    # ❌ Timestamps redundantes
    aberta_em = models.DateTimeField(null=True, blank=True)
    aguardando_em = models.DateTimeField(null=True, blank=True)
    em_andamento_em = models.DateTimeField(null=True, blank=True)
    avaliacao_em = models.DateTimeField(null=True, blank=True)
    encerrada_em = models.DateTimeField(null=True, blank=True)
    fechada_em = models.DateTimeField(null=True, blank=True)
    
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    criado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT)
    atribuido_para = models.ForeignKey(Usuario, null=True, on_delete=models.SET_NULL)
    
    criado_em = models.DateTimeField(auto_now_add=True)
    status_alterado_em = models.DateTimeField(auto_now=True)
```

### Depois (Normalizado em 3NF)

```python
# models.py
from django.db import models

class OpcaoPrioridade(models.Model):
    """Tabela lookup para prioridades"""
    nome = models.CharField(max_length=50, unique=True)
    nivel = models.IntegerField()  # 1-4
    descricao = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Opção de Prioridade"
        verbose_name_plural = "Opções de Prioridade"
    
    def __str__(self):
        return self.nome

class OpcaoTipo(models.Model):
    """Tabela lookup para tipos"""
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

class OpcaoCategoria(models.Model):
    """Tabela lookup para categorias"""
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

class OpcaoUrgencia(models.Model):
    """Tabela lookup para urgências"""
    nome = models.CharField(max_length=50, unique=True)
    nivel = models.IntegerField()  # 1-4
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

class OpcaoDepartamento(models.Model):
    """Tabela lookup para departamentos"""
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.TextField(blank=True)
    
    def __str__(self):
        return self.nome

# ✅ NOVO: Timeline de Status
class OSStatusTimeline(models.Model):
    """Histórico de mudanças de status"""
    os = models.ForeignKey('OrdemServico', on_delete=models.CASCADE, related_name='status_timeline')
    
    status_anterior = models.CharField(max_length=50)
    status_novo = models.CharField(max_length=50)
    
    timestamp_transicao = models.DateTimeField(auto_now_add=True, db_index=True)
    alterado_por = models.ForeignKey(Usuario, null=True, on_delete=models.SET_NULL)
    observacao = models.TextField(blank=True)
    
    class Meta:
        verbose_name = "Timeline de Status da OS"
        verbose_name_plural = "Timelines de Status da OS"
        ordering = ['-timestamp_transicao']
        unique_together = ['os', 'timestamp_transicao']
    
    def __str__(self):
        return f"{self.os.numero}: {self.status_anterior} → {self.status_novo}"

# ✅ REFATORADO: OrdemServico
class OrdemServico(models.Model):
    STATUS_CHOICES = [
        ('aberta', 'Aberta'),
        ('aguardando', 'Aguardando'),
        ('em_andamento', 'Em Andamento'),
        ('avaliacao', 'Em Avaliação'),
        ('encerrada', 'Encerrada'),
        ('fechada', 'Fechada'),
    ]
    
    numero = models.CharField(max_length=20, unique=True, db_index=True)
    titulo = models.CharField(max_length=255)
    descricao = models.TextField()
    
    # ✅ ForeignKeys para lookup tables (3NF)
    prioridade = models.ForeignKey(OpcaoPrioridade, on_delete=models.PROTECT)
    tipo = models.ForeignKey(OpcaoTipo, on_delete=models.PROTECT)
    categoria = models.ForeignKey(OpcaoCategoria, on_delete=models.PROTECT)
    urgencia = models.ForeignKey(OpcaoUrgencia, on_delete=models.PROTECT)
    departamento = models.ForeignKey(OpcaoDepartamento, on_delete=models.PROTECT)
    
    # ✅ Status apenas como campo de estado (não redundante)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='aberta', db_index=True)
    etapa = models.CharField(max_length=50, default='aberta')
    valor_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # ForeignKeys para Usuario e Cliente
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ordens_servico')
    criado_por = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='ordens_criadas')
    atribuido_para = models.ForeignKey(
        Usuario, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='ordens_atribuidas'
    )
    
    criado_em = models.DateTimeField(auto_now_add=True, db_index=True)
    status_alterado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Ordem de Serviço"
        verbose_name_plural = "Ordens de Serviço"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['cliente', '-criado_em']),
            models.Index(fields=['status', '-status_alterado_em']),
        ]
    
    def __str__(self):
        return f"{self.numero} - {self.titulo}"
    
    # ✅ Propriedade para obter timestamps via timeline
    @property
    def timestamps(self):
        """Retorna dicionário com timestamps de cada status"""
        timeline = self.status_timeline.all().order_by('timestamp_transicao')
        timestamps = {}
        
        for entry in timeline:
            if entry.status_novo not in timestamps:
                timestamps[entry.status_novo] = entry.timestamp_transicao
        
        return timestamps
    
    @property
    def aberta_em(self):
        return self.timestamps.get('aberta')
    
    @property
    def aguardando_em(self):
        return self.timestamps.get('aguardando')
    
    @property
    def em_andamento_em(self):
        return self.timestamps.get('em_andamento')
    
    @property
    def avaliacao_em(self):
        return self.timestamps.get('avaliacao')
    
    @property
    def encerrada_em(self):
        return self.timestamps.get('encerrada')
    
    @property
    def fechada_em(self):
        return self.timestamps.get('fechada')
```

### Serializers Atualizados

```python
# serializers.py
from rest_framework import serializers
from .models import *

class OpcaoPrioridadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcaoPrioridade
        fields = ['id', 'nome', 'nivel', 'descricao']

class OpcaoTipoSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpcaoTipo
        fields = ['id', 'nome', 'descricao']

class OrdemServicoSerializer(serializers.ModelSerializer):
    # ✅ Nested serializers para exibir dados completos
    prioridade = OpcaoPrioridadeSerializer(read_only=True)
    prioridade_id = serializers.PrimaryKeyRelatedField(
        queryset=OpcaoPrioridade.objects.all(),
        write_only=True,
        source='prioridade'
    )
    
    tipo = OpcaoTipoSerializer(read_only=True)
    tipo_id = serializers.PrimaryKeyRelatedField(
        queryset=OpcaoTipo.objects.all(),
        write_only=True,
        source='tipo'
    )
    
    cliente_nome = serializers.CharField(source='cliente.nome', read_only=True)
    criado_por_username = serializers.CharField(source='criado_por.username', read_only=True)
    
    # ✅ Propriedades calculadas
    aberta_em = serializers.SerializerMethodField()
    aguardando_em = serializers.SerializerMethodField()
    
    class Meta:
        model = OrdemServico
        fields = [
            'id', 'numero', 'titulo', 'descricao',
            'prioridade', 'prioridade_id',
            'tipo', 'tipo_id',
            'categoria', 'urgencia', 'departamento',
            'status', 'valor_total',
            'cliente_nome', 'criado_por_username',
            'criado_em', 'status_alterado_em',
            'aberta_em', 'aguardando_em'
        ]
    
    def get_aberta_em(self, obj):
        return obj.aberta_em
    
    def get_aguardando_em(self, obj):
        return obj.aguardando_em
```

---

## 📊 TESTES DE VALIDAÇÃO

```python
# tests.py
from django.test import TestCase
from .models import *

class OrdemServicoNormalizacaoTest(TestCase):
    """Testes para validar conformidade com 3NF"""
    
    def setUp(self):
        self.prioridade = OpcaoPrioridade.objects.create(
            nome='Alta', nivel=3
        )
        self.tipo = OpcaoTipo.objects.create(nome='Incidente')
        self.cliente = Cliente.objects.create(nome='Cliente Teste')
        self.usuario = Usuario.objects.create_user(username='teste')
    
    def test_orderm_servico_com_fk_prioridade(self):
        """Verificar que prioridade é FK, não string"""
        os = OrdemServico.objects.create(
            numero='OS-0001',
            titulo='Teste',
            prioridade=self.prioridade,
            tipo=self.tipo,
            cliente=self.cliente,
            criado_por=self.usuario
        )
        
        # ✅ Prioridade deve ser instância de OpcaoPrioridade
        self.assertIsInstance(os.prioridade, OpcaoPrioridade)
        self.assertEqual(os.prioridade.nome, 'Alta')
    
    def test_timeline_status_automatica(self):
        """Verificar que timeline é criada automaticamente"""
        os = OrdemServico.objects.create(
            numero='OS-0002',
            titulo='Teste Timeline',
            prioridade=self.prioridade,
            tipo=self.tipo,
            cliente=self.cliente,
            criado_por=self.usuario,
            status='aberta'
        )
        
        # ✅ Timeline deve ter entrada
        self.assertEqual(os.status_timeline.count(), 1)
        timeline_entry = os.status_timeline.first()
        self.assertEqual(timeline_entry.status_novo, 'aberta')
    
    def test_integridade_referencial(self):
        """Verificar que não é possível inserir valor inválido"""
        from django.db import IntegrityError
        
        with self.assertRaises(IntegrityError):
            os = OrdemServico.objects.create(
                numero='OS-0003',
                titulo='Teste Integridade',
                prioridade_id=9999,  # ID inexistente
                tipo=self.tipo,
                cliente=self.cliente,
                criado_por=self.usuario
            )
    
    def test_propriedades_timestamps(self):
        """Verificar que propriedades de timestamp funcionam"""
        os = OrdemServico.objects.create(
            numero='OS-0004',
            titulo='Teste Timestamps',
            prioridade=self.prioridade,
            tipo=self.tipo,
            cliente=self.cliente,
            criado_por=self.usuario,
            status='aberta'
        )
        
        # ✅ Propriedade deve retornar timestamp
        self.assertIsNotNone(os.aberta_em)
        self.assertIsNone(os.aguardando_em)  # Ainda não mudou
        
        # ✅ Atualizar status
        os.status = 'aguardando'
        os.save()
        
        # Recarregar e verificar
        os.refresh_from_db()
        self.assertIsNotNone(os.aguardando_em)
```

---

## 📝 CHECKLIST DE IMPLEMENTAÇÃO

```
Fase 1: Preparação
  [ ] Backup completo do BD de produção
  [ ] Criar BD de teste com dados reais
  [ ] Executar scripts de migração em teste
  [ ] Validar integridade dos dados
  
Fase 2: Backend (Django)
  [ ] Criar novos models normalizados
  [ ] Criar migrations com `makemigrations`
  [ ] Atualizar serializers
  [ ] Atualizar views/endpoints
  [ ] Atualizar testes
  
Fase 3: Frontend
  [ ] Atualizar API.js para usar novos endpoints
  [ ] Atualizar forms para receber IDs ao invés de strings
  [ ] Testar todos os formulários
  [ ] Verificar dropdowns com novos dados
  
Fase 4: Produção
  [ ] Deploy em staging
  [ ] Testar com dados reais
  [ ] Manutenção de rollback
  [ ] Deploy em produção
  [ ] Monitoramento por 48 horas
```

---

**Scripts preparados para:** PostgreSQL 16 + Django 4.2
**Compatibilidade:** Python 3.12+
**Data:** 13/05/2026
