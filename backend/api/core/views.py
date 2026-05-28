from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from datetime import timedelta
from rest_framework import generics, status, filters, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Cliente, OrdemServico, HistoricoStatus, Iteracao, Anexo
from .serializers import (
    RegisterSerializer, UserSerializer,
    ClienteSerializer,
    OrdemServicoListSerializer, OrdemServicoDetailSerializer,
    OrdemServicoCreateSerializer, AvancarStatusSerializer,
    IteracaoCreateSerializer, AnexoSerializer,
    TecnicoSerializer, TecnicoCreateSerializer, TecnicoUpdateSerializer,
)


# ── AUTH ──────────────────────────────────────────────────────────────────────
class RegisterView(generics.CreateAPIView):
    """RF001: Cadastrar novo usuário."""
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Usuário cadastrado com sucesso.',
            'user': UserSerializer(user).data,
            'tokens': {
                'access':  str(refresh.access_token),
                'refresh': str(refresh),
            }
        }, status=status.HTTP_201_CREATED)


class LogoutView(APIView):
    """Invalida o refresh token."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
            return Response({'message': 'Logout realizado com sucesso.'})
        except Exception:
            return Response({'error': 'Token inválido.'}, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """Retorna dados do usuário autenticado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class MeOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            departamento = user.perfil.departamento.nome if user.perfil.departamento_id else ''
        except Exception:
            departamento = ''

        is_admin = bool(user.is_superuser)

        qs = OrdemServico.objects.select_related(
            'cliente',
            'criado_por',
            'atribuido_para',
            'prioridade',
            'urgencia',
            'departamento',
            'tipo',
            'categoria',
        )

        my_all = qs.filter(atribuido_para=user)
        my_open = my_all.exclude(status='encerrada')

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = (today_start - timedelta(days=today_start.weekday()))

        closed_today = HistoricoStatus.objects.filter(
            os__atribuido_para=user,
            status_novo='encerrada',
            alterado_em__gte=today_start,
        ).values('os_id').distinct().count()

        closed_week = HistoricoStatus.objects.filter(
            os__atribuido_para=user,
            status_novo='encerrada',
            alterado_em__gte=week_start,
        ).values('os_id').distinct().count()

        kpis = {
            'aberta': my_open.filter(status='aberta').count(),
            'aguardando': my_open.filter(status='aguardando').count(),
            'em_andamento': my_open.filter(status='em_andamento').count(),
            'em_avaliacao': my_open.filter(status='em_avaliacao').count(),
            'encerradas_hoje': closed_today,
            'encerradas_semana': closed_week,
        }

        high = my_open.filter(prioridade__nivel__gte=3).order_by('status_alterado_em')[:20]
        queue = my_open.order_by('-prioridade__nivel', '-urgencia__nivel', 'status_alterado_em')[:10]

        stale_hours = request.query_params.get('stale_hours') or '48'
        try:
            stale_hours = int(stale_hours)
        except Exception:
            stale_hours = 48
        stale_before = now - timedelta(hours=stale_hours)
        stale_ids = list(my_open.filter(status='aguardando', status_alterado_em__lte=stale_before).values_list('id', flat=True))

        badge_aguardando = my_open.filter(status='aguardando').count()
        badge_high = my_open.filter(prioridade__nivel__gte=3).count()

        hs = HistoricoStatus.objects.filter(alterado_por=user).select_related('os').order_by('-alterado_em')[:20]
        it = Iteracao.objects.filter(criado_por=user).select_related('os').order_by('-criado_em')[:20]
        recent = []

        for r in hs:
            recent.append({
                'kind': 'status',
                'at': r.alterado_em,
                'os_id': r.os_id,
                'os_numero': r.os.numero,
                'os_titulo': r.os.titulo,
                'from': r.status_anterior,
                'to': r.status_novo,
            })
        for r in it:
            recent.append({
                'kind': 'iteracao',
                'at': r.criado_em,
                'os_id': r.os_id,
                'os_numero': r.os.numero,
                'os_titulo': r.os.titulo,
                'texto': r.texto[:140],
            })
        recent.sort(key=lambda x: x['at'], reverse=True)
        recent = recent[:10]

        os_fields = (
            'id', 'numero', 'titulo', 'status',
            'aberta_em', 'status_alterado_em',
            'cliente__nome',
            'prioridade__nome', 'prioridade__nivel',
            'urgencia__nome', 'urgencia__nivel',
            'departamento__nome',
            'tipo__nome',
            'categoria__nome',
        )

        def dump_os(rows):
            out = []
            for row in rows.values(*os_fields):
                out.append({
                    'id': row['id'],
                    'numero': row['numero'],
                    'titulo': row['titulo'],
                    'status': row['status'],
                    'aberta_em': row['aberta_em'],
                    'status_alterado_em': row['status_alterado_em'],
                    'cliente_nome': row['cliente__nome'] or '',
                    'prioridade': row['prioridade__nome'] or '',
                    'prioridade_nivel': row['prioridade__nivel'] or 0,
                    'urgencia': row['urgencia__nome'] or '',
                    'urgencia_nivel': row['urgencia__nivel'] or 0,
                    'departamento': row['departamento__nome'] or '',
                    'tipo': row['tipo__nome'] or '',
                    'categoria': row['categoria__nome'] or '',
                })
            return out

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'departamento': departamento,
                'is_admin': is_admin,
            },
            'kpis': kpis,
            'badges': {
                'aguardando': badge_aguardando,
                'alta_critica': badge_high,
            },
            'stale_ids': stale_ids,
            'prioridade_do_dia': dump_os(high),
            'fila': dump_os(queue),
            'recentes': recent,
            'saved_filters': [
                {'key': 'my_high', 'label': 'Minhas críticas', 'params': {'assigned_to': 'me', 'prioridade': 'Crítica'}},
                {'key': 'my_wait', 'label': 'Minhas aguardando', 'params': {'assigned_to': 'me', 'status': 'aguardando'}},
                {'key': 'stale_48', 'label': 'Sem atualização 48h', 'params': {'assigned_to': 'me', 'stale_hours': 48}},
                {'key': 'dept_ti', 'label': 'Departamento TI', 'params': {'departamento': 'TI'}},
            ],
        })


class IsSuperUserOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class TecnicoListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsSuperUserOnly]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TecnicoCreateSerializer
        return TecnicoSerializer

    def get_queryset(self):
        return User.objects.filter(groups__name='Tecnicos').select_related('perfil__departamento').order_by('first_name', 'username')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(TecnicoSerializer(user).data, status=status.HTTP_201_CREATED)


class TecnicoDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsSuperUserOnly]
    queryset = User.objects.filter(groups__name='Tecnicos').select_related('perfil__departamento')
    serializer_class = TecnicoUpdateSerializer

    def update(self, request, *args, **kwargs):
        user_obj = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=True, context={'user_obj': user_obj})
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.update(user_obj, serializer.validated_data)
        return Response(TecnicoSerializer(user_obj).data)

    def destroy(self, request, *args, **kwargs):
        user_obj = self.get_object()
        user_obj.is_active = False
        user_obj.save(update_fields=['is_active'])
        return Response(TecnicoSerializer(user_obj).data)


# ── CLIENTES ─────────────────────────────────────────────────────────────────
class ClienteListCreateView(generics.ListCreateAPIView):
    """RF004/RF010: Listar e cadastrar clientes; pesquisa por nome."""
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'email', 'telefone']
    ordering_fields = ['nome', 'criado_em']
    ordering = ['nome']

    def get_queryset(self):
        return Cliente.objects.annotate(
            total_os=Count('ordens'),
            os_abertas=Count('ordens', filter=~Q(ordens__status='encerrada'))
        )


class ClienteDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF005/RF006: Editar e excluir cliente. RN001 aplicado no delete."""
    serializer_class = ClienteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cliente.objects.all()

    def destroy(self, request, *args, **kwargs):
        cliente = self.get_object()
        # RN001: só pode excluir se não tiver OS ativa
        if cliente.tem_os_ativa:
            return Response(
                {'error': 'Cliente possui ordens de serviço em aberto e não pode ser excluído. (RN001)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


# ── ORDENS DE SERVIÇO ─────────────────────────────────────────────────────────
class OrdemServicoListCreateView(generics.ListCreateAPIView):
    """RF007/RF009/RF011: Listar, criar e pesquisar OS."""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['numero', 'titulo', 'cliente__nome', 'departamento__nome']
    ordering_fields = ['aberta_em', 'status', 'prioridade__nivel']
    ordering = ['-aberta_em']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrdemServicoCreateSerializer
        return OrdemServicoListSerializer

    def get_queryset(self):
        qs = OrdemServico.objects.select_related(
            'cliente',
            'criado_por',
            'atribuido_para',
            'prioridade',
            'tipo',
            'categoria',
            'urgencia',
            'departamento',
        )

        if not self.request.user.is_superuser:
            try:
                dept_id = self.request.user.perfil.departamento_id
            except Exception:
                dept_id = None
            if dept_id:
                qs = qs.filter(departamento_id=dept_id)
            else:
                qs = qs.none()
        # Filtros opcionais
        status_param = self.request.query_params.get('status')
        prioridade   = self.request.query_params.get('prioridade')
        tipo         = self.request.query_params.get('tipo')
        cliente_id   = self.request.query_params.get('cliente')
        departamento = self.request.query_params.get('departamento')
        assigned_to  = self.request.query_params.get('assigned_to')
        created_by   = self.request.query_params.get('created_by')

        if status_param:
            qs = qs.filter(status=status_param)
        if prioridade:
            if prioridade.isdigit():
                qs = qs.filter(prioridade_id=int(prioridade))
            else:
                qs = qs.filter(prioridade__nome=prioridade)
        if tipo:
            if tipo.isdigit():
                qs = qs.filter(tipo_id=int(tipo))
            else:
                qs = qs.filter(tipo__nome=tipo)
        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)
        if departamento:
            if departamento.isdigit():
                qs = qs.filter(departamento_id=int(departamento))
            else:
                qs = qs.filter(departamento__nome=departamento)
        if assigned_to:
            if assigned_to == 'me':
                qs = qs.filter(atribuido_para=self.request.user)
            elif assigned_to.isdigit():
                qs = qs.filter(atribuido_para_id=int(assigned_to))
            elif assigned_to == 'none':
                qs = qs.filter(atribuido_para__isnull=True)
        if created_by:
            if created_by == 'me':
                qs = qs.filter(criado_por=self.request.user)
            elif created_by.isdigit():
                qs = qs.filter(criado_por_id=int(created_by))
        return qs

    def perform_create(self, serializer):
        """RN003: status inicial = aberta, data registrada pelo sistema."""
        if not self.request.user.is_superuser:
            try:
                dept_name = self.request.user.perfil.departamento.nome if self.request.user.perfil.departamento_id else ''
            except Exception:
                dept_name = ''
            req_dep = (serializer.validated_data.get('departamento') or '').strip()
            if not dept_name:
                raise serializers.ValidationError({'departamento': 'Usuário sem departamento. Solicite a um admin.'})
            if req_dep != dept_name:
                raise serializers.ValidationError({'departamento': 'Departamento do chamado deve ser o seu departamento.'})
        os_obj = serializer.save(criado_por=self.request.user, status='aberta')
        # Registra histórico inicial
        HistoricoStatus.objects.create(
            os=os_obj,
            status_anterior='',
            status_novo='aberta',
            alterado_por=self.request.user,
            observacao='OS criada.'
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        os_obj = OrdemServico.objects.get(pk=serializer.instance.pk)
        return Response(
            OrdemServicoDetailSerializer(os_obj).data,
            status=status.HTTP_201_CREATED
        )


class OrdemServicoDetailView(generics.RetrieveUpdateDestroyAPIView):
    """RF009/RF012: Visualizar, editar e excluir OS. RN006 no delete."""
    permission_classes = [IsAuthenticated]
    queryset = OrdemServico.objects.prefetch_related(
        'historico_status', 'iteracoes', 'anexos', 'historico_status__alterado_por'
    ).select_related('cliente', 'criado_por')

    def get_queryset(self):
        qs = super().get_queryset().select_related('departamento', 'atribuido_para', 'prioridade', 'urgencia', 'tipo', 'categoria')
        if self.request.user.is_superuser:
            return qs
        try:
            dept_id = self.request.user.perfil.departamento_id
        except Exception:
            dept_id = None
        if dept_id:
            return qs.filter(departamento_id=dept_id)
        return qs.none()

    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return OrdemServicoCreateSerializer
        return OrdemServicoDetailSerializer

    def destroy(self, request, *args, **kwargs):
        """RF012: Só exclui OS encerrada (RN006 inverso — só encerrada pode ser excluída)."""
        os_obj = self.get_object()
        if os_obj.status != 'encerrada':
            return Response(
                {'error': 'Apenas ordens de serviço encerradas podem ser excluídas. (RF012)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """RN006: OS encerrada não pode ser editada."""
        os_obj = self.get_object()
        if os_obj.status == 'encerrada':
            return Response(
                {'error': 'OS encerrada não pode ser editada. (RN006)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)


# ── AVANÇAR STATUS ────────────────────────────────────────────────────────────
class AvancarStatusView(APIView):
    """RF008/RN004: Avançar status sequencial, sem retroceder."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            os_obj = OrdemServico.objects.get(pk=pk)
        except OrdemServico.DoesNotExist:
            return Response({'error': 'OS não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        if not request.user.is_superuser:
            try:
                user_dept_id = request.user.perfil.departamento_id
            except Exception:
                user_dept_id = None
            if not user_dept_id or os_obj.departamento_id != user_dept_id:
                return Response({'error': 'Sem permissão para alterar chamados de outro departamento.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AvancarStatusSerializer(data=request.data, context={'os_obj': os_obj})
        serializer.is_valid(raise_exception=True)

        status_anterior = os_obj.status
        novo_status = os_obj.proximo_status()

        os_obj.status = novo_status
        if novo_status == 'em_andamento' and not os_obj.atribuido_para_id and not request.user.is_superuser:
            os_obj.atribuido_para = request.user
        os_obj.save()

        HistoricoStatus.objects.create(
            os=os_obj,
            status_anterior=status_anterior,
            status_novo=novo_status,
            alterado_por=request.user,
            observacao=serializer.validated_data.get('observacao', '')
        )

        return Response(OrdemServicoDetailSerializer(os_obj).data)


class AtribuirTecnicoView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            os_obj = OrdemServico.objects.select_related('departamento', 'atribuido_para').get(pk=pk)
        except OrdemServico.DoesNotExist:
            return Response({'error': 'OS não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        if not os_obj.departamento_id:
            return Response({'error': 'OS sem departamento.'}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_superuser:
            user_id = request.data.get('user_id')
            if not user_id or not str(user_id).isdigit():
                return Response({'error': 'user_id é obrigatório.'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                target = User.objects.select_related('perfil__departamento').get(pk=int(user_id))
            except User.DoesNotExist:
                return Response({'error': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        else:
            target = request.user
            if os_obj.atribuido_para_id:
                return Response({'error': 'Chamado já possui técnico atribuído.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            target_dept_id = target.perfil.departamento_id
        except Exception:
            target_dept_id = None
        if not target_dept_id or target_dept_id != os_obj.departamento_id:
            return Response({'error': 'Técnico deve ser do mesmo departamento do chamado.'}, status=status.HTTP_400_BAD_REQUEST)

        grp, _ = Group.objects.get_or_create(name='Tecnicos')
        if not target.groups.filter(pk=grp.pk).exists() and not target.is_superuser:
            return Response({'error': 'Usuário não é técnico.'}, status=status.HTTP_400_BAD_REQUEST)

        os_obj.atribuido_para = target
        os_obj.save(update_fields=['atribuido_para'])
        return Response(OrdemServicoDetailSerializer(os_obj).data)


# ── ITERAÇÕES ─────────────────────────────────────────────────────────────────
class IteracaoListCreateView(generics.ListCreateAPIView):
    """Listar e adicionar iterações/comentários a uma OS."""
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return IteracaoCreateSerializer
        from .serializers import IteracaoSerializer
        return IteracaoSerializer

    def get_queryset(self):
        return Iteracao.objects.filter(os_id=self.kwargs['pk']).select_related('criado_por')

    def perform_create(self, serializer):
        os_obj = generics.get_object_or_404(OrdemServico, pk=self.kwargs['pk'])
        if os_obj.status == 'encerrada':
            raise serializers.ValidationError('Não é possível adicionar iterações a uma OS encerrada.')
        serializer.save(os=os_obj, criado_por=self.request.user)


# ── ANEXOS ────────────────────────────────────────────────────────────────────
class AnexoUploadView(APIView):
    """Upload de anexos para uma OS."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        os_obj = generics.get_object_or_404(OrdemServico, pk=pk)
        if os_obj.status == 'encerrada':
            return Response({'error': 'OS encerrada não aceita anexos.'}, status=400)

        arquivo = request.FILES.get('arquivo')
        if not arquivo:
            return Response({'error': 'Nenhum arquivo enviado.'}, status=400)

        # Limite de 10MB
        if arquivo.size > 10 * 1024 * 1024:
            return Response({'error': 'Arquivo excede o limite de 10MB.'}, status=400)

        anexo = Anexo.objects.create(
            os=os_obj,
            arquivo=arquivo,
            nome_arquivo=arquivo.name,
            tipo_conteudo=arquivo.content_type,
            tamanho_bytes=arquivo.size,
            enviado_por=request.user,
        )
        return Response(AnexoSerializer(anexo).data, status=201)


# ── DASHBOARD / MÉTRICAS ──────────────────────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
    """Agrega KPIs para o Dashboard."""
    qs = OrdemServico.objects.all()

    kpis = {
        'total':        qs.count(),
        'aberta':       qs.filter(status='aberta').count(),
        'aguardando':   qs.filter(status='aguardando').count(),
        'em_andamento': qs.filter(status='em_andamento').count(),
        'em_avaliacao': qs.filter(status='em_avaliacao').count(),
        'encerrada':    qs.filter(status='encerrada').count(),
        'total_clientes': Cliente.objects.count(),
    }

    por_tipo_raw = qs.values('tipo__nome').annotate(total=Count('id')).order_by('-total')
    por_tipo = [{'tipo': r['tipo__nome'] or '', 'total': r['total']} for r in por_tipo_raw]

    por_prioridade_raw = qs.values('prioridade__nome').annotate(total=Count('id')).order_by('-total')
    por_prioridade = [{'prioridade': r['prioridade__nome'] or '', 'total': r['total']} for r in por_prioridade_raw]

    # Últimas 5 OS para tabela recente
    recentes = OrdemServicoListSerializer(
        qs.order_by('-aberta_em')[:5], many=True
    ).data

    return Response({
        'kpis': kpis,
        'por_tipo': por_tipo,
        'por_prioridade': por_prioridade,
        'recentes': recentes,
    })


# ── METADADOS (dropdowns do formulário) ───────────────────────────────────────
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def meta_view(request):
    """
    Retorna opções das tabelas de lookup para popular selects no frontend.
    Espelha GET /api/workorders/meta/ do diagrama de sequência (passo 3).
    """
    from .models import OpcaoTipo, OpcaoPrioridade, OpcaoUrgencia, OpcaoDepartamento, OpcaoCategoria

    def to_list(qs):
        return [{'value': o.nome, 'label': o.nome} for o in qs]

    return Response({
        'tipo':          to_list(OpcaoTipo.objects.filter(ativo=True)),
        'prioridade':    to_list(OpcaoPrioridade.objects.filter(ativo=True).order_by('nivel')),
        'urgencia':      to_list(OpcaoUrgencia.objects.filter(ativo=True).order_by('nivel')),
        'categoria':     to_list(OpcaoCategoria.objects.filter(ativo=True)),
        'departamentos': list(OpcaoDepartamento.objects.filter(ativo=True).values_list('nome', flat=True)),
        'status':        [{'value': k, 'label': v} for k, v in OrdemServico.STATUS_CHOICES],
    })
