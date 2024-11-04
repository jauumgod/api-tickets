from django.urls import path, include
from .views import (
    GroupCreateView, NotaFiscalViewSet, TicketsStatsView, UserListCreateView, UserRetrieveUpdateDestroyView,
    TicketsListCreateView, TicketsRetrieveUpdateDestroyView,
    EmpresasListCreateView, EmpresasRetrieveUpdateDestroyView,
    ImagensViewSet, TicketsCountView, GroupCreateView,GroupRetrieveUpdateDestroyView
)
from .views import CustomTokenObtainPairView, homepage

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r'imagens', ImagensViewSet, basename='imagens')
router.register(r'notas-fiscais', NotaFiscalViewSet, basename='notafiscal')

urlpatterns = [
    
    path('users/', UserListCreateView.as_view(), name='users-list'),
    path('users/<int:pk>', UserRetrieveUpdateDestroyView.as_view(), name='users-detail'),
    path('tickets/', TicketsListCreateView.as_view(), name='tickets-list'),
    path('tickets/<int:pk>', TicketsRetrieveUpdateDestroyView.as_view(), name='tickets-detail'),
    path('tickets/count/', TicketsCountView.as_view(), name='ticket-count'),
    path('tickets/stats/', TicketsStatsView.as_view(), name='tickets-stats'),
    path('empresas/', EmpresasListCreateView.as_view(), name='operacao-list'),
    path('empresas/<int:pk>', EmpresasRetrieveUpdateDestroyView.as_view(), name='tickets-detail'),
    path('grupos/', GroupCreateView.as_view(), name='tickets-detail'),
    path('grupos/<int:pk>', GroupRetrieveUpdateDestroyView.as_view(), name='tickets-detail'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('imagens/ticket/<int:ticket_id>/', ImagensViewSet.as_view({'get': 'list_by_ticket'}), name='imagens-by-ticket'),


    
    path('', include(router.urls)),
    
]

