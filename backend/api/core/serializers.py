from django.contrib.auth.models import User, Group
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import (
    Cliente,
    OrdemServico,
    HistoricoStatus,
    Iteracao,
    Anexo,
    PerfilUsuario,
    OpcaoDepartamento,
    OpcaoPrioridade,
    OpcaoTipo,
    OpcaoCategoria,
    OpcaoUrgencia,
)


# ── AUTH ──────────────────────────────────────────────────────────────────────
class RegisterSerializer(serializers.ModelSerializer):
    """RF001: Cadastro de usuário (login único – RN007)."""
    email = serializers.EmailField(required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(required=True,
        validators=[UniqueValidator(queryset=User.objects.all())])
    password  = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Confirmar senha')
    telefone = serializers.CharField(required=True, allow_blank=False)
    departamento = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'telefone', 'password', 'password2', 'departamento')
        extra_kwargs = {'first_name': {'required': True}, 'last_name': {'required': False}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'As senhas não conferem.'})
        return attrs

    def create(self, validated_data):
        departamento = validated_data.pop('departamento', '')
        telefone = validated_data.pop('telefone')
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        dep_fk = None
        if departamento:
            dep_fk, _ = OpcaoDepartamento.objects.get_or_create(nome=departamento)
        PerfilUsuario.objects.create(
            usuario=user,
            departamento=dep_fk,
            tipo=PerfilUsuario.TIPO_CLIENTE,
        )
        Cliente.objects.create(
            nome=f"{user.first_name} {user.last_name}".strip() or user.username,
            email=user.email,
            telefone=telefone,
            departamento=dep_fk,
            usuario=user,
        )
        return user


class PasswordResetSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, label='Confirmar senha')

    def validate_username(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Informe o usuário.')
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({'password': 'As senhas não conferem.'})

        username = attrs['username'].strip()
        email = attrs['email'].strip().lower()
        try:
            user = User.objects.get(username=username, email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': 'Usuário e e-mail não conferem.'})

        attrs['user_obj'] = user
        return attrs

    def save(self, **kwargs):
        user = self.validated_data['user_obj']
        user.set_password(self.validated_data['password'])
        user.save(update_fields=['password'])
        return user


class UserSerializer(serializers.ModelSerializer):
    tipo = serializers.SerializerMethodField()
    cliente_id = serializers.SerializerMethodField()
    departamento = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'departamento', 'tipo', 'cliente_id')

    def get_departamento(self, obj):
        try:
            perfil = obj.perfil
            if getattr(perfil, 'departamento_id', None):
                return perfil.departamento.nome
            return ''
        except PerfilUsuario.DoesNotExist:
            return ''

    def get_tipo(self, obj):
        if obj.is_superuser:
            return PerfilUsuario.TIPO_ADMIN
        try:
            return obj.perfil.tipo or PerfilUsuario.TIPO_CLIENTE
        except PerfilUsuario.DoesNotExist:
            return PerfilUsuario.TIPO_CLIENTE

    def get_cliente_id(self, obj):
        cliente = getattr(obj, 'cliente_vinculado', None)
        return getattr(cliente, 'id', None)


def sync_user_role(user, tipo, departamento_obj=None):
    perfil, _ = PerfilUsuario.objects.get_or_create(usuario=user)
    perfil.tipo = tipo or PerfilUsuario.TIPO_CLIENTE
    perfil.departamento = departamento_obj
    perfil.save()

    grp, _ = Group.objects.get_or_create(name='Tecnicos')
    user.groups.remove(grp)
    user.is_superuser = tipo == PerfilUsuario.TIPO_ADMIN
    user.is_staff = user.is_superuser
    if tipo == PerfilUsuario.TIPO_TECNICO:
        user.groups.add(grp)
    user.save(update_fields=['is_superuser', 'is_staff'])
    return perfil


ADMIN_USER_TYPE_CHOICES = [
    (PerfilUsuario.TIPO_ADMIN, 'Administrador'),
    (PerfilUsuario.TIPO_TECNICO, 'Técnico'),
]


class AdminUserSerializer(serializers.ModelSerializer):
    departamento = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email', 'is_active',
            'departamento', 'tipo',
        )

    def get_departamento(self, obj):
        try:
            perfil = obj.perfil
            if getattr(perfil, 'departamento_id', None):
                return perfil.departamento.nome
            return ''
        except Exception:
            return ''

    def get_tipo(self, obj):
        if obj.is_superuser:
            return PerfilUsuario.TIPO_ADMIN
        try:
            return obj.perfil.tipo or PerfilUsuario.TIPO_CLIENTE
        except Exception:
            return PerfilUsuario.TIPO_CLIENTE

class AdminUserCreateSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    departamento = serializers.CharField(required=False, allow_blank=True, default='')
    tipo = serializers.ChoiceField(choices=ADMIN_USER_TYPE_CHOICES)

    def validate_username(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError('Usuário não pode ser vazio.')
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Usuário já existe.')
        return value

    def validate_email(self, value):
        value = value.strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email já está em uso.')
        return value

    def validate_departamento(self, value):
        value = (value or '').strip()
        if value and not OpcaoDepartamento.objects.filter(nome=value, ativo=True).exists():
            raise serializers.ValidationError('Departamento inválido.')
        return value

    def validate(self, attrs):
        tipo = attrs.get('tipo')
        departamento = (attrs.get('departamento') or '').strip()

        if tipo == PerfilUsuario.TIPO_TECNICO and not departamento:
            raise serializers.ValidationError({'departamento': 'Departamento é obrigatório para técnico.'})
        return attrs

    def create(self, validated_data):
        departamento = validated_data.pop('departamento', '') or ''
        password = validated_data.pop('password')
        tipo = validated_data.pop('tipo')

        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        user.save()

        dep_fk = None
        if departamento:
            dep_fk = OpcaoDepartamento.objects.get(nome=departamento)
        sync_user_role(user, tipo, dep_fk)
        return user


class AdminUserUpdateSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=False)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    departamento = serializers.CharField(required=False, allow_blank=True)
    is_active = serializers.BooleanField(required=False)
    tipo = serializers.ChoiceField(choices=ADMIN_USER_TYPE_CHOICES, required=False)
    password = serializers.CharField(required=False, allow_blank=True, min_length=6, write_only=True)

    def validate_username(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Usuário não pode ser vazio.')
        user = self.context.get('user_obj')
        qs = User.objects.filter(username=value)
        if user:
            qs = qs.exclude(pk=user.pk)
        if qs.exists():
            raise serializers.ValidationError('Usuário já existe.')
        return value

    def validate_email(self, value):
        value = (value or '').strip()
        if not value:
            return value
        user = self.context.get('user_obj')
        qs = User.objects.filter(email=value)
        if user:
            qs = qs.exclude(pk=user.pk)
        if qs.exists():
            raise serializers.ValidationError('Email já está em uso.')
        return value

    def validate_departamento(self, value):
        value = (value or '').strip()
        if value and not OpcaoDepartamento.objects.filter(nome=value, ativo=True).exists():
            raise serializers.ValidationError('Departamento inválido.')
        return value

    def validate(self, attrs):
        user = self.context.get('user_obj')
        current_tipo = PerfilUsuario.TIPO_ADMIN if getattr(user, 'is_superuser', False) else getattr(getattr(user, 'perfil', None), 'tipo', PerfilUsuario.TIPO_TECNICO)
        tipo = attrs.get('tipo', current_tipo)
        departamento = attrs.get('departamento', None)

        dept_value = (departamento or '').strip() if departamento is not None else None
        current_dept = ''
        try:
            current_dept = user.perfil.departamento.nome if user.perfil.departamento_id else ''
        except Exception:
            current_dept = ''
        effective_dept = dept_value if dept_value is not None else current_dept

        if tipo == PerfilUsuario.TIPO_TECNICO and not effective_dept:
            raise serializers.ValidationError({'departamento': 'Departamento é obrigatório para técnico.'})
        return attrs

    def update(self, instance, validated_data):
        if 'username' in validated_data:
            instance.username = validated_data['username']
        if 'first_name' in validated_data:
            instance.first_name = validated_data['first_name']
        if 'last_name' in validated_data:
            instance.last_name = validated_data['last_name']
        if 'email' in validated_data:
            instance.email = validated_data['email']
        if 'is_active' in validated_data:
            instance.is_active = validated_data['is_active']
        if 'password' in validated_data and validated_data['password']:
            instance.set_password(validated_data['password'])
        instance.save()

        try:
            perfil = instance.perfil
        except Exception:
            perfil = PerfilUsuario(usuario=instance)

        dep_name = validated_data.get('departamento', None)
        if dep_name is None:
            departamento_obj = perfil.departamento if getattr(perfil, 'departamento_id', None) else None
        else:
            departamento_obj = OpcaoDepartamento.objects.get(nome=dep_name) if dep_name else None
        tipo = validated_data.get('tipo', PerfilUsuario.TIPO_ADMIN if instance.is_superuser else (perfil.tipo or PerfilUsuario.TIPO_TECNICO))
        sync_user_role(instance, tipo, departamento_obj)
        return instance


class OpcaoLookupSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'nome', 'ativo')

    def validate_nome(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Nome não pode ser vazio.')
        model = self.Meta.model
        qs = model.objects.filter(nome__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Já existe um cadastro com este nome.')
        return value


class OpcaoLookupNivelSerializer(OpcaoLookupSerializer):
    nivel = serializers.IntegerField(min_value=1, max_value=99)

    class Meta(OpcaoLookupSerializer.Meta):
        fields = ('id', 'nome', 'nivel', 'ativo')


class DepartamentoSerializer(OpcaoLookupSerializer):
    class Meta(OpcaoLookupSerializer.Meta):
        model = OpcaoDepartamento


class TipoSerializer(OpcaoLookupSerializer):
    class Meta(OpcaoLookupSerializer.Meta):
        model = OpcaoTipo


class CategoriaSerializer(OpcaoLookupSerializer):
    class Meta(OpcaoLookupSerializer.Meta):
        model = OpcaoCategoria


class PrioridadeSerializer(OpcaoLookupNivelSerializer):
    class Meta(OpcaoLookupNivelSerializer.Meta):
        model = OpcaoPrioridade


class UrgenciaSerializer(OpcaoLookupNivelSerializer):
    class Meta(OpcaoLookupNivelSerializer.Meta):
        model = OpcaoUrgencia


# ── CLIENTE ───────────────────────────────────────────────────────────────────
class ClienteSerializer(serializers.ModelSerializer):
    total_os      = serializers.SerializerMethodField()
    os_abertas    = serializers.SerializerMethodField()
    tem_os_ativa  = serializers.BooleanField(read_only=True)
    departamento = serializers.CharField(required=True, allow_blank=False, write_only=True)
    usuario_id = serializers.IntegerField(read_only=True)
    usuario_username = serializers.CharField(required=False, allow_blank=False, write_only=True)
    usuario_password = serializers.CharField(required=False, allow_blank=True, write_only=True, min_length=6)

    class Meta:
        model  = Cliente
        fields = ('id', 'nome', 'telefone', 'email', 'endereco',
                  'departamento', 'usuario_id', 'usuario_username', 'usuario_password',
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

    def validate_departamento(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Departamento é obrigatório.')
        if not OpcaoDepartamento.objects.filter(nome=value, ativo=True).exists():
            raise serializers.ValidationError('Departamento inválido.')
        return value

    def validate_usuario_username(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('Usuário de acesso é obrigatório.')
        qs = User.objects.filter(username=value)
        if self.instance and getattr(self.instance, 'usuario_id', None):
            qs = qs.exclude(pk=self.instance.usuario_id)
        if qs.exists():
            raise serializers.ValidationError('Usuário de acesso já existe.')
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if not self.instance:
            if not attrs.get('usuario_username'):
                raise serializers.ValidationError({'usuario_username': 'Usuário de acesso é obrigatório.'})
            if not attrs.get('usuario_password'):
                raise serializers.ValidationError({'usuario_password': 'Senha de acesso é obrigatória.'})
        return attrs

    def create(self, validated_data):
        departamento = validated_data.pop('departamento')
        username = validated_data.pop('usuario_username')
        password = validated_data.pop('usuario_password')
        dept_obj = OpcaoDepartamento.objects.get(nome=departamento)

        nome = validated_data.get('nome', '').strip()
        partes_nome = nome.split()
        first_name = partes_nome[0] if partes_nome else ''
        last_name = ' '.join(partes_nome[1:]) if len(partes_nome) > 1 else ''

        user = User.objects.create_user(
            username=username,
            email=validated_data.get('email', ''),
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        user.save()
        sync_user_role(user, PerfilUsuario.TIPO_CLIENTE, dept_obj)

        validated_data['departamento'] = dept_obj
        validated_data['usuario'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        departamento = validated_data.pop('departamento', None)
        username = validated_data.pop('usuario_username', None)
        password = validated_data.pop('usuario_password', None)
        if departamento is not None:
            instance.departamento = OpcaoDepartamento.objects.get(nome=departamento)

        user = getattr(instance, 'usuario', None)
        if not user:
            if not username:
                raise serializers.ValidationError({'usuario_username': 'Cliente sem usuário vinculado. Informe um usuário.'})
            if not password:
                raise serializers.ValidationError({'usuario_password': 'Cliente sem usuário vinculado. Informe uma senha.'})
            user = User.objects.create_user(
                username=username,
                email=validated_data.get('email', instance.email),
                password=password,
            )
            instance.usuario = user

        if username is not None:
            user.username = username
        user.email = validated_data.get('email', instance.email)
        partes_nome = (validated_data.get('nome', instance.nome) or '').strip().split()
        user.first_name = partes_nome[0] if partes_nome else ''
        user.last_name = ' '.join(partes_nome[1:]) if len(partes_nome) > 1 else ''
        if password:
            user.set_password(password)
        user.is_active = True
        user.save()
        sync_user_role(user, PerfilUsuario.TIPO_CLIENTE, instance.departamento)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['departamento'] = instance.departamento.nome if getattr(instance, 'departamento_id', None) else ''
        data['usuario_id'] = instance.usuario_id or None
        data['usuario_username'] = instance.usuario.username if getattr(instance, 'usuario_id', None) else ''
        return data


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
    criado_por_id = serializers.IntegerField(source='criado_por.id', read_only=True)
    atribuido_para_nome = serializers.SerializerMethodField()
    atribuido_para_id = serializers.SerializerMethodField()
    status_display    = serializers.CharField(source='get_status_display',    read_only=True)
    prioridade = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()
    categoria = serializers.SerializerMethodField()
    urgencia = serializers.SerializerMethodField()
    departamento = serializers.SerializerMethodField()
    prioridade_display = serializers.SerializerMethodField()
    tipo_display = serializers.SerializerMethodField()
    encerrada_em = serializers.DateTimeField(read_only=True)
    status_alterado_em = serializers.DateTimeField(read_only=True)

    class Meta:
        model  = OrdemServico
        fields = (
            'id', 'numero', 'titulo', 'status', 'status_display',
            'prioridade', 'prioridade_display', 'tipo', 'tipo_display',
            'categoria', 'urgencia', 'departamento',
            'cliente_nome', 'criado_por_nome', 'criado_por_id',
            'atribuido_para_nome', 'atribuido_para_id',
            'aberta_em', 'status_alterado_em', 'encerrada_em',
        )

    def get_criado_por_nome(self, obj):
        if obj.criado_por:
            return obj.criado_por.get_full_name() or obj.criado_por.username
        return ''

    def get_atribuido_para_nome(self, obj):
        if getattr(obj, 'atribuido_para_id', None):
            return obj.atribuido_para.get_full_name() or obj.atribuido_para.username
        return ''

    def get_atribuido_para_id(self, obj):
        return getattr(obj, 'atribuido_para_id', None) or None

    def get_prioridade(self, obj):
        if getattr(obj, 'prioridade_id', None):
            return obj.prioridade.nome
        return ''

    def get_tipo(self, obj):
        if getattr(obj, 'tipo_id', None):
            return obj.tipo.nome
        return ''

    def get_categoria(self, obj):
        if getattr(obj, 'categoria_id', None):
            return obj.categoria.nome
        return ''

    def get_urgencia(self, obj):
        if getattr(obj, 'urgencia_id', None):
            return obj.urgencia.nome
        return ''

    def get_departamento(self, obj):
        if getattr(obj, 'departamento_id', None):
            return obj.departamento.nome
        return ''

    def get_prioridade_display(self, obj):
        return self.get_prioridade(obj)

    def get_tipo_display(self, obj):
        return self.get_tipo(obj)


class OrdemServicoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo com histórico, iterações e anexos."""
    cliente_nome    = serializers.CharField(source='cliente.nome', read_only=True)
    cliente_telefone = serializers.CharField(source='cliente.telefone', read_only=True)
    criado_por_nome = serializers.CharField(source='criado_por.username', default='', read_only=True)
    atribuido_para_nome = serializers.SerializerMethodField()
    atribuido_para_id = serializers.SerializerMethodField()
    status_display  = serializers.CharField(source='get_status_display', read_only=True)
    prioridade = serializers.SerializerMethodField()
    tipo = serializers.SerializerMethodField()
    categoria = serializers.SerializerMethodField()
    urgencia = serializers.SerializerMethodField()
    departamento = serializers.SerializerMethodField()
    prioridade_display = serializers.SerializerMethodField()
    tipo_display = serializers.SerializerMethodField()
    encerrada_em = serializers.DateTimeField(read_only=True)
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
            'criado_por_nome', 'atribuido_para_nome', 'atribuido_para_id',
            'aberta_em', 'encerrada_em', 'status_alterado_em',
            'historico_status', 'iteracoes', 'anexos',
            'pode_avancar', 'proximo_status',
        )
        read_only_fields = ('numero', 'aberta_em', 'status_alterado_em')

    def get_atribuido_para_nome(self, obj):
        if getattr(obj, 'atribuido_para_id', None):
            return obj.atribuido_para.get_full_name() or obj.atribuido_para.username
        return ''

    def get_atribuido_para_id(self, obj):
        return getattr(obj, 'atribuido_para_id', None) or None

    def get_prioridade(self, obj):
        if getattr(obj, 'prioridade_id', None):
            return obj.prioridade.nome
        return ''

    def get_tipo(self, obj):
        if getattr(obj, 'tipo_id', None):
            return obj.tipo.nome
        return ''

    def get_categoria(self, obj):
        if getattr(obj, 'categoria_id', None):
            return obj.categoria.nome
        return ''

    def get_urgencia(self, obj):
        if getattr(obj, 'urgencia_id', None):
            return obj.urgencia.nome
        return ''

    def get_departamento(self, obj):
        if getattr(obj, 'departamento_id', None):
            return obj.departamento.nome
        return ''

    def get_prioridade_display(self, obj):
        return self.get_prioridade(obj)

    def get_tipo_display(self, obj):
        return self.get_tipo(obj)


class OrdemServicoCreateSerializer(serializers.ModelSerializer):
    """RF007: Criação de OS – RN002: cliente deve existir."""
    tipo = serializers.CharField(required=False, allow_blank=True, default='')
    categoria = serializers.CharField(required=False, allow_blank=True, default='')
    prioridade = serializers.CharField(required=False, allow_blank=True, default='')
    urgencia = serializers.CharField(required=False, allow_blank=True, default='')
    departamento = serializers.CharField(required=True, allow_blank=False)

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

    def validate_prioridade(self, value):
        if value and not OpcaoPrioridade.objects.filter(nome=value).exists():
            raise serializers.ValidationError('Prioridade inválida.')
        return value

    def validate_tipo(self, value):
        if value and not OpcaoTipo.objects.filter(nome=value).exists():
            raise serializers.ValidationError('Tipo inválido.')
        return value

    def validate_categoria(self, value):
        if value and not OpcaoCategoria.objects.filter(nome=value).exists():
            raise serializers.ValidationError('Categoria inválida.')
        return value

    def validate_urgencia(self, value):
        if value and not OpcaoUrgencia.objects.filter(nome=value).exists():
            raise serializers.ValidationError('Urgência inválida.')
        return value

    def validate_departamento(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError('Departamento é obrigatório.')
        if value and not OpcaoDepartamento.objects.filter(nome=value).exists():
            raise serializers.ValidationError('Departamento inválido.')
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        cliente = attrs.get('cliente') or getattr(self.instance, 'cliente', None)
        departamento = attrs.get('departamento')

        if cliente and not getattr(cliente, 'departamento_id', None):
            raise serializers.ValidationError({'cliente': 'Cliente sem departamento cadastrado. Atualize o cadastro do cliente.'})

        if cliente and departamento and (
            not user or getattr(getattr(user, 'perfil', None), 'tipo', '') != PerfilUsuario.TIPO_CLIENTE
        ) and cliente.departamento.nome != departamento:
            raise serializers.ValidationError({'departamento': 'Departamento do chamado deve ser o mesmo departamento do cliente.'})

        if user and getattr(getattr(user, 'perfil', None), 'tipo', '') == PerfilUsuario.TIPO_CLIENTE:
            if (attrs.get('prioridade') or '').strip():
                raise serializers.ValidationError({'prioridade': 'Cliente não pode definir prioridade do chamado.'})
            if (attrs.get('urgencia') or '').strip():
                raise serializers.ValidationError({'urgencia': 'Cliente não pode definir urgência do chamado.'})

        return attrs

    def create(self, validated_data):
        prioridade = validated_data.pop('prioridade', '') or ''
        tipo = validated_data.pop('tipo', '') or ''
        categoria = validated_data.pop('categoria', '') or ''
        urgencia = validated_data.pop('urgencia', '') or ''
        departamento = validated_data.pop('departamento', '') or ''

        if prioridade:
            validated_data['prioridade'] = OpcaoPrioridade.objects.get(nome=prioridade)
        if tipo:
            validated_data['tipo'] = OpcaoTipo.objects.get(nome=tipo)
        if categoria:
            validated_data['categoria'] = OpcaoCategoria.objects.get(nome=categoria)
        if urgencia:
            validated_data['urgencia'] = OpcaoUrgencia.objects.get(nome=urgencia)
        if departamento:
            validated_data['departamento'] = OpcaoDepartamento.objects.get(nome=departamento)

        return OrdemServico.objects.create(**validated_data)

    def update(self, instance, validated_data):
        prioridade = validated_data.pop('prioridade', None)
        tipo = validated_data.pop('tipo', None)
        categoria = validated_data.pop('categoria', None)
        urgencia = validated_data.pop('urgencia', None)
        departamento = validated_data.pop('departamento', None)

        for k, v in validated_data.items():
            setattr(instance, k, v)

        if prioridade is not None:
            instance.prioridade = OpcaoPrioridade.objects.get(nome=prioridade) if prioridade else None
        if tipo is not None:
            instance.tipo = OpcaoTipo.objects.get(nome=tipo) if tipo else None
        if categoria is not None:
            instance.categoria = OpcaoCategoria.objects.get(nome=categoria) if categoria else None
        if urgencia is not None:
            instance.urgencia = OpcaoUrgencia.objects.get(nome=urgencia) if urgencia else None
        if departamento is not None:
            instance.departamento = OpcaoDepartamento.objects.get(nome=departamento) if departamento else None

        instance.save()
        return instance


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
        if os_obj.status == 'em_andamento':
            obs = (attrs.get('observacao') or '').strip()
            if not obs:
                raise serializers.ValidationError({'observacao': 'Descreva o serviço executado para avançar.'})
        return attrs


class IteracaoCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Iteracao
        fields = ('texto',)

    def validate_texto(self, value):
        if not value.strip():
            raise serializers.ValidationError('Texto não pode ser vazio.')
        return value.strip()
