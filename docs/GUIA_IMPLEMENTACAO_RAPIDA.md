# ⚡ GUIA RÁPIDO DE IMPLEMENTAÇÃO 3NF
## SGOS — Pronto para Copy-Paste

---

## 🚀 5 PASSOS PARA IMPLEMENTAR

### PASSO 1: Backup do Banco

```bash
# 1. Backup completo
pg_dump -U <SEU_USUARIO> sgos > backup_sgos_$(date +%Y%m%d_%H%M%S).sql

# 2. Verificar backup
ls -lh backup_sgos_*.sql

# 3. Guardar em lugar seguro
cp backup_sgos_*.sql ~/backups/
```

---

### PASSO 2: Criar Migration Django

**Arquivo:** `core/migrations/0002_add_fk_opcoes.py`

```python
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        # 1. Adicionar novos campos FK (nullable)
        migrations.AddField(
            model_name='ordemservico',
            name='prioridade_fk',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='ordens_prioridade',
                to='core.opcaoprioridade'
            ),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='tipo_fk',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='ordens_tipo',
                to='core.opcaotipo'
            ),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='categoria_fk',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='ordens_categoria',
                to='core.opcaocategoria'
            ),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='urgencia_fk',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='ordens_urgencia',
                to='core.opcaourgencia'
            ),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='departamento_fk',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='ordens_departamento',
                to='core.opcaodepartamento'
            ),
        ),
        
        # 2. Migrar dados dos campos string para FK
        migrations.RunPython(migrar_dados_para_fk),
        
        # 3. Renomear campos (trocar _fk por string old)
        migrations.RenameField('ordemservico', 'prioridade', 'prioridade_old'),
        migrations.RenameField('ordemservico', 'prioridade_fk', 'prioridade'),
        
        migrations.RenameField('ordemservico', 'tipo', 'tipo_old'),
        migrations.RenameField('ordemservico', 'tipo_fk', 'tipo'),
        
        migrations.RenameField('ordemservico', 'categoria', 'categoria_old'),
        migrations.RenameField('ordemservico', 'categoria_fk', 'categoria'),
        
        migrations.RenameField('ordemservico', 'urgencia', 'urgencia_old'),
        migrations.RenameField('ordemservico', 'urgencia_fk', 'urgencia'),
        
        migrations.RenameField('ordemservico', 'departamento', 'departamento_old'),
        migrations.RenameField('ordemservico', 'departamento_fk', 'departamento'),
    ]

def migrar_dados_para_fk(apps, schema_editor):
    """Popula as FKs baseado nos valores string existentes"""
    OrdemServico = apps.get_model('core', 'OrdemServico')
    OpcaoPrioridade = apps.get_model('core', 'OpcaoPrioridade')
    OpcaoTipo = apps.get_model('core', 'OpcaoTipo')
    OpcaoCategoria = apps.get_model('core', 'OpcaoCategoria')
    OpcaoUrgencia = apps.get_model('core', 'OpcaoUrgencia')
    OpcaoDepartamento = apps.get_model('core', 'OpcaoDepartamento')
    
    count_updated = 0
    count_failed = 0
    
    for os in OrdemServico.objects.all():
        try:
            if os.prioridade and not os.prioridade_fk:
                os.prioridade_fk = OpcaoPrioridade.objects.get(nome=os.prioridade)
            if os.tipo and not os.tipo_fk:
                os.tipo_fk = OpcaoTipo.objects.get(nome=os.tipo)
            if os.categoria and not os.categoria_fk:
                os.categoria_fk = OpcaoCategoria.objects.get(nome=os.categoria)
            if os.urgencia and not os.urgencia_fk:
                os.urgencia_fk = OpcaoUrgencia.objects.get(nome=os.urgencia)
            if os.departamento and not os.departamento_fk:
                os.departamento_fk = OpcaoDepartamento.objects.get(nome=os.departamento)
            
            os.save()
            count_updated += 1
        except Exception as e:
            count_failed += 1
            print(f"[ERRO] OS {os.numero}: {str(e)}")
    
    print(f"✅ {count_updated} OSs atualizadas")
    if count_failed > 0:
        print(f"❌ {count_failed} OSs com erro — revisar manualmente")

def reverter(apps, schema_editor):
    """Reverter para os campos string"""
    pass  # Você pode implementar se necessário
```

---

### PASSO 3: Executar Migration

```bash
# 1. Testar migration localmente
python manage.py migrate core 0002_add_fk_opcoes

# 2. Verificar banco (deve ter novos campos)
python manage.py dbshell
# No psql:
# \d ordens_servico
# Deve ver: prioridade_fk, tipo_fk, categoria_fk, urgencia_fk, departamento_fk

# 3. Verificar dados migrados
# SELECT COUNT(*) FROM ordens_servico WHERE prioridade_fk IS NOT NULL;
# SELECT COUNT(*) FROM ordens_servico WHERE prioridade_old IS NOT NULL;
```

---

### PASSO 4: Atualizar Models e Serializers

**Arquivo:** `core/models.py` — Substituir linhas 136-140

```python
class OrdemServico(models.Model):
    # ... campos existentes ...
    
    # Classificação (NOVO: ForeignKeys)
    prioridade = models.ForeignKey(
        OpcaoPrioridade,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='ordens_prioridade'
    )
    tipo = models.ForeignKey(
        OpcaoTipo,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='ordens_tipo'
    )
    categoria = models.ForeignKey(
        OpcaoCategoria,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='ordens_categoria'
    )
    urgencia = models.ForeignKey(
        OpcaoUrgencia,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='ordens_urgencia'
    )
    departamento = models.ForeignKey(
        OpcaoDepartamento,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='ordens_departamento'
    )
    
    # ... resto do modelo ...
```

**Arquivo:** `core/serializers.py` — Adicionar após imports

```python
class OrdemServicoSerializer(serializers.ModelSerializer):
    # Nested serializers (para ler dados completos)
    prioridade_detalhes = OpcaoPrioridadeSerializer(
        source='prioridade', read_only=True
    )
    tipo_detalhes = OpcaoTipoSerializer(
        source='tipo', read_only=True
    )
    categoria_detalhes = OpcaoCategoriaSerializer(
        source='categoria', read_only=True
    )
    
    # IDs para escrita (criar/atualizar)
    prioridade_id = serializers.PrimaryKeyRelatedField(
        queryset=OpcaoPrioridade.objects.all(),
        source='prioridade',
        write_only=True,
        required=False,
        allow_null=True
    )
    tipo_id = serializers.PrimaryKeyRelatedField(
        queryset=OpcaoTipo.objects.all(),
        source='tipo',
        write_only=True,
        required=False,
        allow_null=True
    )
    categoria_id = serializers.PrimaryKeyRelatedField(
        queryset=OpcaoCategoria.objects.all(),
        source='categoria',
        write_only=True,
        required=False,
        allow_null=True
    )
    urgencia_id = serializers.PrimaryKeyRelatedField(
        queryset=OpcaoUrgencia.objects.all(),
        source='urgencia',
        write_only=True,
        required=False,
        allow_null=True
    )
    departamento_id = serializers.PrimaryKeyRelatedField(
        queryset=OpcaoDepartamento.objects.all(),
        source='departamento',
        write_only=True,
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = OrdemServico
        fields = [
            'id', 'numero', 'titulo', 'descricao',
            'status', 'etapa',
            # Prioridade (ler com objeto, escrever com ID)
            'prioridade', 'prioridade_id', 'prioridade_detalhes',
            # Tipo (ler com objeto, escrever com ID)
            'tipo', 'tipo_id', 'tipo_detalhes',
            # Categoria
            'categoria', 'categoria_id', 'categoria_detalhes',
            # Urgência
            'urgencia', 'urgencia_id',
            # Departamento
            'departamento', 'departamento_id',
            # Relacionamentos
            'cliente', 'criado_por', 'atribuido_para',
            'valor_total',
            'aberta_em', 'status_alterado_em', 'aguardando_em',
            'em_andamento_em', 'avaliacao_em', 'encerrada_em', 'fechada_em'
        ]
```

**Arquivo:** `core/views.py` — Atualizar ViewSet

```python
class OrdemServicoViewSet(viewsets.ModelViewSet):
    queryset = OrdemServico.objects.all()
    serializer_class = OrdemServicoSerializer
    
    def get_queryset(self):
        """✅ Usar select_related para evitar N+1 queries"""
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'cliente',
            'criado_por',
            'atribuido_para',
            'prioridade',
            'tipo',
            'categoria',
            'urgencia',
            'departamento'
        )
        return queryset
```

---

### PASSO 5: Testar e Deploy

```bash
# 1. Rodar testes
python manage.py test core --verbosity=2

# 2. Testar API com curl
TOKEN="seu_token_aqui"

# ✅ GET funcionando
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8010/api/workorders/

# ✅ POST com novo formato (IDs)
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "numero": "OS-TEST-001",
    "titulo": "Teste com FK",
    "descricao": "Testando nova estrutura",
    "cliente": 1,
    "prioridade_id": 1,
    "tipo_id": 1,
    "categoria_id": 1,
    "urgencia_id": 1,
    "departamento_id": 1
  }' \
  http://localhost:8010/api/workorders/

# 3. Verificar resposta (deve incluir prioridade_detalhes, etc)
# {
#   "id": 999,
#   "numero": "OS-TEST-001",
#   "prioridade": 1,
#   "prioridade_detalhes": {
#     "id": 1,
#     "nome": "Alta",
#     "nivel": 3
#   },
#   ...
# }
```

---

## 🧪 TESTES RÁPIDOS

### Query para validar integridade

```sql
-- ✅ Verificar que todos têm FK (não deixar NULL)
SELECT COUNT(*) FROM ordens_servico WHERE prioridade_id IS NULL;
-- Deve retornar: 0

-- ✅ Verificar que não há valores órfãos
SELECT COUNT(*) FROM ordens_servico os
WHERE os.prioridade_id NOT IN (SELECT id FROM os_opcoes_prioridade);
-- Deve retornar: 0

-- ✅ Verificar performance
EXPLAIN ANALYZE
SELECT os.numero, p.nome, t.nome
FROM ordens_servico os
LEFT JOIN os_opcoes_prioridade p ON os.prioridade_id = p.id
LEFT JOIN os_opcoes_tipo t ON os.tipo_id = t.id
WHERE os.status = 'aberta';
-- Deve ser rápido com índices
```

---

## 📋 CHECKLIST FINAL

```
ANTES DE FAZER MIGRATION:
  [ ] Backup do banco feito
  [ ] Branch Git criado
  [ ] Migration testada localmente
  [ ] Serializers atualizados
  [ ] Models prontos

APÓS MIGRATION:
  [ ] Todos os dados migrados (COUNT validado)
  [ ] Testes passando
  [ ] API retornando dados corretos
  [ ] Dropdowns funcionando no frontend

ANTES DE DEPLOY:
  [ ] Testar em staging
  [ ] Verificar performance
  [ ] Validar integridade referencial
  [ ] Plano de rollback pronto

APÓS DEPLOY:
  [ ] Monitorar erros por 24h
  [ ] Validar relatórios/KPIs
  [ ] Feedback do time
  [ ] Celebrar! 🎉
```

---

## 🚨 SE DER ERRO

### Erro: `IntegrityError` ao rodar migration

```python
# Problema: Alguns campos prioridade_old não tem match em os_opcoes_prioridade
# Solução: Verificar quais são

python manage.py dbshell
# SELECT DISTINCT prioridade FROM ordens_servico;
# Ver quais não existem em os_opcoes_prioridade

# Depois adicionar manualmente ou ignorar na migration
```

### Erro: `Foreign key constraint violation`

```python
# Problema: Tentou deletar um departamento que tem OS
# Solução: Usar on_delete=models.PROTECT (que já está configurado)
# Isso vai impedir deletar departamentos com OS — seguro!
```

### Frontend quebrou após update

```python
# Problema: API está retornando prioridade como objeto, não string
# Solução: Frontend JS precisa acessar prioridade.nome ao invés de prioridade

# Antes:
console.log(os.prioridade)  // "Alta"

# Depois:
console.log(os.prioridade.nome)  // "Alta" (do objeto)
console.log(os.prioridade_id)    // 1 (o ID)
```

---

## ⏱️ TEMPO ESTIMADO

| Tarefa | Tempo | Responsável |
|--------|-------|------------|
| Backup + Preparação | 30 min | DevOps |
| Criar Migration | 20 min | Backend |
| Executar Migration | 10 min | Backend |
| Atualizar Models/Serializers | 30 min | Backend |
| Testes | 30 min | QA |
| Deploy Staging | 20 min | DevOps |
| Testes em Staging | 30 min | QA |
| Deploy Produção | 15 min | DevOps |
| **TOTAL** | **~3h 5min** | - |

---

## 💬 COMUNICADO PARA O CLIENTE

```
Prezado Cliente,

Estamos implementando melhorias de qualidade no banco de dados 
do SGOS para aumentar a integridade e confiabilidade dos dados.

⏰ Quando: [Data]
⏱️  Duração: ~30 minutos
🔧 Impacto: Sem impacto no uso — sistema continuará funcionando

O que muda:
✅ Dados mais seguros e confiáveis
✅ Relatórios mais precisos
✅ Melhor performance
✅ Sem perda de dados

Agradecemos a compreensão!
```

---

**Pronto para implementar!** 🚀

Para dúvidas, ver documentos completos em:
- `ANALISE_3NF_CODIGO_REAL.md` (Análise técnica)
- `SQL_MIGRACAO_3NF.md` (Scripts detalhados)
