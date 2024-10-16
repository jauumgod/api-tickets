from rest_framework import generics
from rest_framework.response import Response
from .models import Empresas, Usuarios, Tickets, Imagens
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncDay
from rest_framework.views import APIView
from .serializers import (
    EmpresaSerializers, UsuarioSerializer,
    TicketSerializers, ImagensSerializer, CustomTokenObtainPairSerializer
)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, status, viewsets
from rest_framework.permissions import IsAuthenticated


#============OPERACAO===========
class EmpresasListCreateView(generics.ListCreateAPIView):
    queryset = Empresas.objects.all()
    serializer_class = EmpresaSerializers


class EmpresasRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Empresas.objects.all()
    serializer_class = EmpresaSerializers


#=============USER==============
class UserListCreateView(generics.ListCreateAPIView):
    queryset = Usuarios.objects.all()
    serializer_class = UsuarioSerializer


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Usuarios.objects.all()
    serializer_class = UsuarioSerializer


#===========================TICKETS V2 - CREATE TICKET BASED ON TOKEN =========================

class TicketsListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSerializers
    permission_classes = [IsAuthenticated]  # Garante que o usuário esteja autenticado

    def get_queryset(self):
        queryset = Tickets.objects.all()

        # Obtendo os parâmetros da query
        empresa = self.request.query_params.get('empresa')
        sequencia = self.request.query_params.get('sequencia')
        criacao = self.request.query_params.get('criacao')

        # Filtrando com base nos parâmetros, se estiverem presentes
        if empresa:
            queryset = queryset.filter(empresa__nome__icontains=empresa)

        if sequencia:
            queryset = queryset.filter(sequencia=sequencia)

        if criacao:
            queryset = queryset.filter(criacao=criacao)

        return queryset

    def perform_create(self, serializer):
        user = self.request.user

        try:
            # Obtem todas as empresas associadas ao usuário
            user_empresas = Usuarios.objects.get(id=user.id).empresa.all()  
        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        if not user_empresas.exists():  # Verifica se o usuário tem empresas associadas
            return Response(
                {'error': 'Usuário não está associado a nenhuma empresa.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Pega a primeira empresa associada (você pode mudar isso conforme necessário)
        empresa = user_empresas.first()

        # Salva o ticket com a empresa e o usuário
        serializer.save(usuario=user, empresa=empresa)




class TicketsRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tickets.objects.all()
    serializer_class = TicketSerializers
    permission_classes = [IsAuthenticated]

    def partial_update(self, request, *args, **kwargs):
        # Pegando o ticket a ser atualizado
        ticket = self.get_object()
        
        # Atualizando parcialmente o ticket com os dados fornecidos
        serializer = self.get_serializer(ticket, data=request.data, partial=True)
        
        # Validando os dados
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class TicketsCountView(APIView):

    def get(self, request):

        total_tickets = Tickets.objects.count()
        completed_tickets = Tickets.objects.filter(concluido=True).count()

        return Response({
            'total_tickets': total_tickets,
            'completed_tickets': completed_tickets,
        })
    

class TicketsStatsView(APIView):
    queryset = Tickets.objects.all()

    def get(self, request, *args, **kwargs):

        monthly_stats = (
            Tickets.objects.annotate(month=TruncMonth('criacao'))
            .values('month')
            .annotate(
                emitidos=Count('id'),
                concluidos=Count('id', filter=Q(concluido=True))
            )
            .order_by('month')
        )

        daily_stats = (
            Tickets.objects.annotate(day=TruncDay('criacao'))
            .values('day')
            .annotate(
                emitidos=Count('id'),
                concluidos=Count('id', filter=Q(concluido=True))
            )
            .order_by('day')
        )
        data = {
            'monthly_stats': list(monthly_stats),
            'daily_stats': list(daily_stats),
        }
        return Response(data)
    


class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.user
        
        # Verifica se existe o UserOperacao para o usuário
        try:
            user_empresa = Usuarios.objects.get(id=user.id)  
            empresas = user_empresa.empresa
        except Usuarios.DoesNotExist:
            empresas = []

        response_data = {
            'access': serializer.validated_data['access'],
            'refresh': serializer.validated_data['refresh'],
            'user_id': user.id,
            'username': user.username,
            'empresas': [empresas.id] if empresas else [],  # Correção aqui
        }
        
        return Response(response_data)


class ImagensViewSet(viewsets.ModelViewSet):
    queryset = Imagens.objects.all()
    serializer_class = ImagensSerializer