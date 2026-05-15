"""
SGOS – Models
Espelha fielmente o schema PostgreSQL do diagrama (postgres_-_public.png).
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# ══════════════════════════════════════════════════════════════════════════════
#  TABELAS DE OPÇÕES (lookup tables – os_opcoes_*)
# ══════════════════════════════════════════════════════════════════════════════

class OpcaoBase(models.Model):
    """Classe abstrata comum a todas as tabelas de opções."""
    nome        = models.CharField(max_length=100, unique=True)
    ativo       = models.BooleanField(default=True)
    criado_em   = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['nome']

    def __str__(self):
        return self.nome


class OpcaoUrgencia(OpcaoBase):
    """os_opcoes_urgencia — nível define a ordem (1=baixa … 4=imediata)."""
    nivel = models.PositiveSmallIntegerField(default=1)

    class Meta(OpcaoBase.Meta):
        db_table = 'os_opcoes_urgencia'
        verbose_name = 'Urgência'
        verbose_name_plural = 'Urgências'
        ordering = ['nivel']


class OpcaoPrioridade(OpcaoBase):
    """os_opcoes_prioridade — nível define a ordem (1=baixa … 4=crítica)."""
    nivel = models.PositiveSmallIntegerField(default=1)

    class Meta(OpcaoBase.Meta):
        db_table = 'os_opcoes_prioridade'
        verbose_name = 'Prioridade'
        verbose_name_plural = 'Prioridades'
        ordering = ['nivel']


class OpcaoDepartamento(OpcaoBase):
    """os_opcoes_departamento."""
    class Meta(OpcaoBase.Meta):
        db_table = 'os_opcoes_departamento'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'


class OpcaoTipo(OpcaoBase):
    """os_opcoes_tipo."""
    class Meta(OpcaoBase.Meta):
        db_table = 'os_opcoes_tipo'
        verbose_name = 'Tipo de OS'
        verbose_name_plural = 'Tipos de OS'


class OpcaoCategoria(OpcaoBase):
    """os_opcoes_categoria."""
    class Meta(OpcaoBase.Meta):
        db_table = 'os_opcoes_categoria'
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'


# ══════════════════════════════════════════════════════════════════════════════
#  CLIENTES
# ══════════════════════════════════════════════════════════════════════════════

class Cliente(models.Model):
    """Tabela clientes."""
    nome          = models.CharField(max_length=200)
    email         = models.EmailField()
    telefone      = models.CharField(max_length=20)
    endereco      = models.CharField(max_length=300, blank=True)
    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'clientes'
        ordering = ['nome']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nome

    @property
    def tem_os_ativa(self):
        """RN001: possui OS com status diferente de 'encerrada'."""
        return self.ordens.exclude(status='encerrada').exists()


# ══════════════════════════════════════════════════════════════════════════════
#  ORDENS DE SERVIÇO
# ══════════════════════════════════════════════════════════════════════════════

class OrdemServico(models.Model):
    """
    Tabela ordens_servico.
    Inclui todos os campos do diagrama:
      - status (workflow principal)
      - etapa  (etapa atual dentro do workflow, ex: 'triagem', 'execucao')
      - timestamps individuais por status
      - valor_total
      - atribuido_para_id
    """

    STATUS_CHOICES = [
        ('aberta',       'Aberta'),
        ('aguardando',   'Aguardando'),
        ('em_andamento', 'Em Andamento'),
        ('em_avaliacao', 'Em Avaliação'),
        ('encerrada',    'Encerrada'),
    ]

    # Sequência obrigatória – RN004
    STATUS_ORDER = ['aberta', 'aguardando', 'em_andamento', 'em_avaliacao', 'encerrada']

    # ── Identificação ──────────────────────────────────────
    numero  = models.CharField(max_length=20, unique=True, editable=False)
    titulo  = models.CharField(max_length=200)
    descricao = models.TextField()

    # ── Classificação (FK para tabelas de opções) ──────────
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    prioridade  = models.CharField(max_length=100, blank=True)   # nome da OpcaoPrioridade
    tipo        = models.CharField(max_length=100, blank=True)   # nome do OpcaoTipo
    categoria   = models.CharField(max_length=100, blank=True)   # nome da OpcaoCategoria
    urgencia    = models.CharField(max_length=100, blank=True)   # nome da OpcaoUrgencia
    departamento = models.CharField(max_length=100, blank=True)  # nome do OpcaoDepartamento

    # ── Etapa interna (sub-estágio dentro do status) ───────
    etapa           = models.CharField(max_length=100, blank=True)
    etapa_alterada_em = models.DateTimeField(null=True, blank=True)

    # ── Relacionamentos ────────────────────────────────────
    cliente        = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ordens')
    criado_por     = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='os_criadas')
    atribuido_para = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='os_atribuidas')

    # ── Financeiro ─────────────────────────────────────────
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # ── Timestamps por status (diagrama) ───────────────────
    aberta_em         = models.DateTimeField(auto_now_add=True)          # RN003
    status_alterado_em = models.DateTimeField(auto_now=True)
    aguardando_em     = models.DateTimeField(null=True, blank=True)
    em_andamento_em   = models.DateTimeField(null=True, blank=True)
    avaliacao_em      = models.DateTimeField(null=True, blank=True)
    encerrada_em      = models.DateTimeField(null=True, blank=True)
    fechada_em        = models.DateTimeField(null=True, blank=True)       # alias de encerrada_em

    class Meta:
        db_table = 'ordens_servico'
        ordering = ['-aberta_em']
        verbose_name = 'Ordem de Serviço'
        verbose_name_plural = 'Ordens de Serviço'

    def __str__(self):
        return f'{self.numero} – {self.titulo}'

    def save(self, *args, **kwargs):
        # Gera número sequencial (OS-0001, OS-0002 …)
        if not self.numero:
            ultimo = OrdemServico.objects.order_by('-id').first()
            seq = (ultimo.id + 1) if ultimo else 1
            self.numero = f'OS-{seq:04d}'
        super().save(*args, **kwargs)

    # ── Helpers de workflow ────────────────────────────────
    def pode_avancar(self):
        """RN004: há próximo status disponível."""
        return self.STATUS_ORDER.index(self.status) < len(self.STATUS_ORDER) - 1

    def proximo_status(self):
        idx = self.STATUS_ORDER.index(self.status)
        return self.STATUS_ORDER[idx + 1] if self.pode_avancar() else None

    def registrar_timestamp_status(self):
        """Registra o timestamp do status recém-atribuído."""
        now = timezone.now()
        mapa = {
            'aguardando':   'aguardando_em',
            'em_andamento': 'em_andamento_em',
            'em_avaliacao': 'avaliacao_em',
            'encerrada':    'encerrada_em',
        }
        campo = mapa.get(self.status)
        if campo and not getattr(self, campo):
            setattr(self, campo, now)
        if self.status == 'encerrada':
            self.fechada_em = now
            self.encerrada_em = now


# ══════════════════════════════════════════════════════════════════════════════
#  HISTÓRICO DE STATUS  (os_historico_status)
# ══════════════════════════════════════════════════════════════════════════════

class HistoricoStatus(models.Model):
    os              = models.ForeignKey(OrdemServico, on_delete=models.CASCADE,
                                        related_name='historico_status', db_column='os_id')
    status_anterior = models.CharField(max_length=20, blank=True)
    status_novo     = models.CharField(max_length=20)
    alterado_por    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                        db_column='alterado_por_id')
    alterado_em     = models.DateTimeField(auto_now_add=True)
    observacao      = models.TextField(blank=True)

    class Meta:
        db_table = 'os_historico_status'
        ordering = ['alterado_em']

    def __str__(self):
        return f'{self.os.numero}: {self.status_anterior} → {self.status_novo}'


# ══════════════════════════════════════════════════════════════════════════════
#  HISTÓRICO DE ETAPAS  (os_historico_etapas)
# ══════════════════════════════════════════════════════════════════════════════

class HistoricoEtapa(models.Model):
    os             = models.ForeignKey(OrdemServico, on_delete=models.CASCADE,
                                       related_name='historico_etapas', db_column='os_id')
    etapa_anterior = models.CharField(max_length=100, blank=True)
    etapa_nova     = models.CharField(max_length=100)
    alterado_por   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                       db_column='alterado_por_id')
    alterado_em    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'os_historico_etapas'
        ordering = ['alterado_em']

    def __str__(self):
        return f'{self.os.numero}: etapa {self.etapa_anterior} → {self.etapa_nova}'


# ══════════════════════════════════════════════════════════════════════════════
#  ITERAÇÕES / COMENTÁRIOS  (os_iteracoes)
# ══════════════════════════════════════════════════════════════════════════════

class Iteracao(models.Model):
    os         = models.ForeignKey(OrdemServico, on_delete=models.CASCADE,
                                   related_name='iteracoes', db_column='os_id')
    texto      = models.TextField()
    criado_em  = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   db_column='criado_por_id')

    class Meta:
        db_table = 'os_iteracoes'
        ordering = ['criado_em']

    def __str__(self):
        return f'Iteração #{self.pk} em {self.os.numero}'


# ══════════════════════════════════════════════════════════════════════════════
#  ANEXOS  (os_anexos)
# ══════════════════════════════════════════════════════════════════════════════

class Anexo(models.Model):
    os            = models.ForeignKey(OrdemServico, on_delete=models.CASCADE,
                                      related_name='anexos', db_column='os_id')
    arquivo       = models.FileField(upload_to='anexos/%Y/%m/')
    nome_arquivo  = models.CharField(max_length=255)
    tipo_conteudo = models.CharField(max_length=100)
    tamanho_bytes = models.PositiveIntegerField()
    enviado_por   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                      db_column='enviado_por_id')
    enviado_em    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'os_anexos'

    def __str__(self):
        return self.nome_arquivo


# ══════════════════════════════════════════════════════════════════════════════
#  ANOTAÇÕES ERP  (os_anotacoes_erp)
# ══════════════════════════════════════════════════════════════════════════════

class AnotacaoERP(models.Model):
    """Anotações vindas de integração com sistema ERP."""
    cod_os        = models.CharField(max_length=30)
    anotacao      = models.TextField()
    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    criado_por    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                      db_column='criado_por_id')

    class Meta:
        db_table = 'os_anotacoes_erp'
        verbose_name = 'Anotação ERP'
        verbose_name_plural = 'Anotações ERP'

    def __str__(self):
        return f'ERP {self.cod_os}'


# ══════════════════════════════════════════════════════════════════════════════
#  PERFIL DE USUÁRIO  (usuarios_perfis)
# ══════════════════════════════════════════════════════════════════════════════

class PerfilUsuario(models.Model):
    usuario       = models.OneToOneField(User, on_delete=models.CASCADE,
                                         related_name='perfil', db_column='usuario_id')
    departamento  = models.CharField(max_length=100, blank=True)
    criado_em     = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuarios_perfis'
        verbose_name = 'Perfil de Usuário'
        verbose_name_plural = 'Perfis de Usuários'

    def __str__(self):
        return f'Perfil de {self.usuario.username}'
