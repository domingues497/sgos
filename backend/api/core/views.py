from django.utils import timezone
from django.db.models import Q, Count
from django.contrib.auth.models import User

from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
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
    search_fields = ['numero', 'titulo', 'cliente__nome', 'departamento']
    ordering_fields = ['aberta_em', 'status', 'prioridade']
    ordering = ['-aberta_em']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrdemServicoCreateSerializer
        return OrdemServicoListSerializer

    def get_queryset(self):
        qs = OrdemServico.objects.select_related('cliente', 'criado_por')
        # Filtros opcionais
        status_param = self.request.query_params.get('status')
        prioridade   = self.request.query_params.get('prioridade')
        tipo         = self.request.query_params.get('tipo')
        cliente_id   = self.request.query_params.get('cliente')

        if status_param:
            qs = qs.filter(status=status_param)
        if prioridade:
            qs = qs.filter(prioridade=prioridade)
        if tipo:
            qs = qs.filter(tipo=tipo)
        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)
        return qs

    def perform_create(self, serializer):
        """RN003: status inicial = aberta, data registrada pelo sistema."""
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

        serializer = AvancarStatusSerializer(data=request.data, context={'os_obj': os_obj})
        serializer.is_valid(raise_exception=True)

        status_anterior = os_obj.status
        novo_status = os_obj.proximo_status()

        os_obj.status = novo_status
        if novo_status == 'encerrada':
            os_obj.encerrada_em = timezone.now()
        os_obj.save()

        HistoricoStatus.objects.create(
            os=os_obj,
            status_anterior=status_anterior,
            status_novo=novo_status,
            alterado_por=request.user,
            observacao=serializer.validated_data.get('observacao', '')
        )

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
        return Iteracao.objects.filter(os_id=self.kwargs['pk']).select_related('autor')

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

    por_tipo = list(
        qs.values('tipo').annotate(total=Count('id')).order_by('-total')
    )

    por_prioridade = list(
        qs.values('prioridade').annotate(total=Count('id')).order_by('-total')
    )

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
