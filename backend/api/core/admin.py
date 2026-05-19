from django.contrib import admin
from .models import (Cliente, OrdemServico, HistoricoStatus, HistoricoEtapa,
                     Iteracao, Anexo, AnotacaoERP, PerfilUsuario,
                     OpcaoUrgencia, OpcaoPrioridade, OpcaoDepartamento,
                     OpcaoTipo, OpcaoCategoria)


# ── Lookup tables ──────────────────────────────────────────────────────────────
@admin.register(OpcaoUrgencia)
class OpcaoUrgenciaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nivel', 'ativo')

@admin.register(OpcaoPrioridade)
class OpcaoPrioridadeAdmin(admin.ModelAdmin):
    list_display = ('nome', 'nivel', 'ativo')

@admin.register(OpcaoDepartamento)
class OpcaoDepartamentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')

@admin.register(OpcaoTipo)
class OpcaoTipoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')

@admin.register(OpcaoCategoria)
class OpcaoCategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')


# ── Cliente ────────────────────────────────────────────────────────────────────
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ('nome', 'telefone', 'email', 'criado_em')
    search_fields = ('nome', 'email', 'telefone')
    ordering      = ('nome',)


# ── OS Inlines ─────────────────────────────────────────────────────────────────
class HistoricoStatusInline(admin.TabularInline):
    model = HistoricoStatus
    extra = 0
    readonly_fields = ('status_anterior', 'status_novo', 'alterado_por', 'alterado_em', 'observacao')

class HistoricoEtapaInline(admin.TabularInline):
    model = HistoricoEtapa
    extra = 0
    readonly_fields = ('etapa_anterior', 'etapa_nova', 'alterado_por', 'alterado_em')

class IteracaoInline(admin.TabularInline):
    model = Iteracao
    extra = 0
    readonly_fields = ('criado_por', 'texto', 'criado_em')

class AnexoInline(admin.TabularInline):
    model = Anexo
    extra = 0
    readonly_fields = ('nome_arquivo', 'tipo_conteudo', 'tamanho_bytes', 'enviado_por', 'enviado_em')


# ── Ordem de Serviço ──────────────────────────────────────────────────────────
@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    list_display    = ('numero', 'titulo', 'cliente', 'status', 'prioridade', 'criado_por', 'aberta_em')
    list_filter     = ('status', 'prioridade', 'tipo', 'departamento')
    search_fields   = ('numero', 'titulo', 'cliente__nome')
    readonly_fields = ('numero', 'aberta_em', 'status_alterado_em')
    inlines         = [HistoricoStatusInline, HistoricoEtapaInline, IteracaoInline, AnexoInline]
    ordering        = ('-aberta_em',)
    fieldsets = (
        ('Identificação',  {'fields': ('numero', 'titulo', 'descricao')}),
        ('Classificação',  {'fields': ('status', 'prioridade', 'tipo', 'categoria', 'urgencia', 'departamento')}),
        ('Etapa',          {'fields': ('etapa', 'etapa_alterada_em')}),
        ('Relacionamentos',{'fields': ('cliente', 'criado_por', 'atribuido_para')}),
        ('Financeiro',     {'fields': ('valor_total',)}),
        ('Timestamps',     {'fields': ('aberta_em', 'status_alterado_em')}),
    )


@admin.register(AnotacaoERP)
class AnotacaoERPAdmin(admin.ModelAdmin):
    list_display = ('cod_os', 'criado_por', 'criado_em')
    search_fields = ('cod_os',)


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'departamento', 'criado_em')
