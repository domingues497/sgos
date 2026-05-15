from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import Cliente, OrdemServico, HistoricoStatus, Iteracao, Anexo, PerfilUsuario


# ── AUTH ──────────────────────────────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    """RF001: Cadastro de usuário (login único – RN007)."""
    email = serializers.EmailField(required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])
    password  = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Confirmar senha')
    departamento = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password', 'password2', 'departamento')
        extra_kwargs = {'first_name': {'required': True}, 'last_name': {'required': False}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'As senhas não conferem.'})
        return attrs

    def create(self, validated_data):
        departamento = validated_data.pop('departamento', '')
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        PerfilUsuario.objects.create(usuario=user, departamento=departamento)
        return user


class UserSerializer(serializers.ModelSerializer):
    departamento = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'departamento')

    def get_departamento(self, obj):
        try:
            return obj.perfil.departamento
        except PerfilUsuario.DoesNotExist:
            return ''


# ── CLIENTE ───────────────────────────────────────────────────────────────────
class ClienteSerializer(serializers.ModelSerializer):
    total_os      = serializers.SerializerMethodField()
    os_abertas    = serializers.SerializerMethodField()
    tem_os_ativa  = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Cliente
        fields = ('id', 'nome', 'telefone', 'email', 'endereco',
                  'criado_em', 'total_os', 'os_abertas', 'tem_os_ativa')
        read_only_fields = ('criado_em',)

    def get_total_os(self, obj):
        return obj.ordens.count()

    def get_os_abertas(self, obj):
        return obj.ordens.exclude(status='encerrada').count()

    def validate_nome(self, value):
        if not value.strip():
            raise serializers.ValidationError('Nome não pode ser vazio.')
        return value.strip()


# ── HISTÓRICO ─────────────────────────────────────────────────────────────────
class HistoricoStatusSerializer(serializers.ModelSerializer):
    alterado_por_nome = serializers.SerializerMethodField()

    class Meta:
        model  = HistoricoStatus
        fields = ('id', 'status_anterior', 'status_novo', 'alterado_por_nome', 'alterado_em', 'observacao')

    def get_alterado_por_nome(self, obj):
        if obj.alterado_por:
            return obj.alterado_por.get_full_name() or obj.alterado_por.username
        return 'Sistema'


# ── ITERAÇÃO ──────────────────────────────────────────────────────────────────
class IteracaoSerializer(serializers.ModelSerializer):
    autor_nome = serializers.SerializerMethodField()

    class Meta:
        model  = Iteracao
        fields = ('id', 'texto', 'autor_nome', 'criado_por', 'criado_em')
        read_only_fields = ('criado_em', 'criado_por')
        read_only_fields = ('criado_em',)

    def get_autor_nome(self, obj):
        if obj.criado_por:
            return obj.criado_por.get_full_name() or obj.criado_por.username
        return 'Desconhecido'


# ── ANEXO ─────────────────────────────────────────────────────────────────────
class AnexoSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Anexo
        fields = ('id', 'nome_arquivo', 'tipo_conteudo', 'tamanho_bytes', 'enviado_em', 'arquivo')
        read_only_fields = ('enviado_em',)


# ── ORDEM DE SERVIÇO ──────────────────────────────────────────────────────────
class OrdemServicoListSerializer(serializers.ModelSerializer):
    """Serializer leve para listagens (Kanban / Dashboard)."""
    cliente_nome  = serializers.CharField(source='cliente.nome', read_only=True)
    criado_por_nome = serializers.SerializerMethodField()
    status_display    = serializers.CharField(source='get_status_display',    read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)
    tipo_display      = serializers.CharField(source='get_tipo_display',      read_only=True)

    class Meta:
        model  = OrdemServico
        fields = (
            'id', 'numero', 'titulo', 'status', 'status_display',
            'prioridade', 'prioridade_display', 'tipo', 'tipo_display',
            'categoria', 'urgencia', 'departamento',
            'cliente_nome', 'criado_por_nome', 'aberta_em', 'encerrada_em',
        )

    def get_criado_por_nome(self, obj):
        if obj.criado_por:
            return obj.criado_por.get_full_name() or obj.criado_por.username
        return ''


class OrdemServicoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo com histórico, iterações e anexos."""
    cliente_nome    = serializers.CharField(source='cliente.nome', read_only=True)
    cliente_telefone = serializers.CharField(source='cliente.telefone', read_only=True)
    criado_por_nome = serializers.CharField(source='criado_por.username', default='', read_only=True)
    status_display  = serializers.CharField(source='get_status_display', read_only=True)
    prioridade_display = serializers.CharField(source='get_prioridade_display', read_only=True)
    tipo_display    = serializers.CharField(source='get_tipo_display', read_only=True)
    historico_status = HistoricoStatusSerializer(many=True, read_only=True)
    iteracoes        = IteracaoSerializer(many=True, read_only=True)
    anexos           = AnexoSerializer(many=True, read_only=True)
    pode_avancar     = serializers.BooleanField(read_only=True)
    proximo_status   = serializers.CharField(read_only=True)

    class Meta:
        model  = OrdemServico
        fields = (
            'id', 'numero', 'titulo', 'descricao',
            'status', 'status_display', 'prioridade', 'prioridade_display',
            'tipo', 'tipo_display', 'categoria', 'urgencia', 'departamento',
            'cliente', 'cliente_nome', 'cliente_telefone',
            'criado_por_nome', 'aberta_em', 'encerrada_em', 'status_alterado_em',
            'historico_status', 'iteracoes', 'anexos',
            'pode_avancar', 'proximo_status',
        )
        read_only_fields = ('numero', 'aberta_em', 'status_alterado_em')


class OrdemServicoCreateSerializer(serializers.ModelSerializer):
    """RF007: Criação de OS – RN002: cliente deve existir."""
    class Meta:
        model  = OrdemServico
        fields = (
            'cliente', 'titulo', 'descricao', 'tipo',
            'categoria', 'prioridade', 'urgencia', 'departamento',
        )

    def validate_cliente(self, value):
        if not Cliente.objects.filter(pk=value.pk).exists():
            raise serializers.ValidationError('Cliente não encontrado.')
        return value


class AvancarStatusSerializer(serializers.Serializer):
    """RF008: Avançar status – RN004."""
    observacao = serializers.CharField(required=False, allow_blank=True, default='')

    def validate(self, attrs):
        os_obj = self.context.get('os_obj')
        if not os_obj:
            raise serializers.ValidationError('OS não encontrada.')
        if not os_obj.pode_avancar():
            raise serializers.ValidationError('Esta OS já está encerrada e não pode avançar.')
        # RN006: OS encerrada não pode ser editada
        if os_obj.status == 'encerrada':
            raise serializers.ValidationError('OS encerrada não pode ser alterada.')
        return attrs


class IteracaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Iteracao
        fields = ('texto',)

    def validate_texto(self, value):
        if not value.strip():
            raise serializers.ValidationError('Texto não pode ser vazio.')
        return value.strip()
