from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────
    path('auth/register/',        views.RegisterView.as_view(),         name='register'),
    path('auth/login/',           TokenObtainPairView.as_view(),        name='login'),       # RF002
    path('auth/refresh/',         TokenRefreshView.as_view(),           name='token-refresh'),
    path('auth/logout/',          views.LogoutView.as_view(),           name='logout'),
    path('auth/me/',              views.MeView.as_view(),               name='me'),

    # ── Clientes ──────────────────────────────────────────
    path('clientes/',             views.ClienteListCreateView.as_view(),  name='clientes'),   # RF004/RF010
    path('clientes/<int:pk>/',    views.ClienteDetailView.as_view(),      name='cliente'),    # RF005/RF006

    # ── Ordens de Serviço ─────────────────────────────────
    path('workorders/',           views.OrdemServicoListCreateView.as_view(), name='workorders'), # RF007/RF011
    path('workorders/<int:pk>/',  views.OrdemServicoDetailView.as_view(),     name='workorder'),  # RF009/RF012
    path('workorders/<int:pk>/etapa/',   views.AvancarStatusView.as_view(),   name='avançar'),    # RF008/RN004
    path('workorders/<int:pk>/iteracoes/', views.IteracaoListCreateView.as_view(), name='iteracoes'),
    path('workorders/<int:pk>/anexos/',   views.AnexoUploadView.as_view(),    name='anexos'),

    # ── Utilitários ───────────────────────────────────────
    path('workorders/meta/',      views.meta_view,                      name='meta'),        # diagrama seq.
    path('dashboard/',            views.dashboard_view,                 name='dashboard'),
]
