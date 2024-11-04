from datetime import timezone
from django.shortcuts import get_object_or_404, render
from rest_framework.decorators import action
from rest_framework import generics
from rest_framework.response import Response
from .models import Empresas, Grupos, NotaFiscal, Usuarios, Tickets, Imagens
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncDay, TruncDate, TruncTime
from rest_framework.views import APIView
from .serializers import (
    EmpresaSerializers, GroupSerializer, NotaFiscalSerializer, UsuarioSerializer,
    TicketSerializers, ImagensSerializer, CustomTokenObtainPairSerializer
)
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import permissions, status, viewsets
from rest_framework.permissions import IsAuthenticated
from cloudinary import uploader
from django.utils import timezone



#FIRST HTML

def homepage(request):
    return render(request, 'index.html')


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

#==============Grupos ===============
class GroupCreateView(generics.ListCreateAPIView):
    queryset = Grupos.objects.all()
    serializer_class = GroupSerializer

class GroupRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Grupos.objects.all()
    serializer_class = GroupSerializer


#===========================TICKETS V2 - CREATE TICKET BASED ON TOKEN =========================

class TicketsListCreateView(generics.ListCreateAPIView):
    serializer_class = TicketSerializers
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        try:
            user_empresas = Usuarios.objects.get(id=user.id).empresa.all()
        except Usuarios.DoesNotExist:
            return Tickets.objects.none()

        queryset = Tickets.objects.filter(empresa__in=user_empresas)

        # Obtendo parâmetros de filtragem adicionais
        empresa = self.request.query_params.get('empresa')
        sequencia = self.request.query_params.get('sequencia')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        cliente = self.request.query_params.get('cliente')  # Novo parâmetro para busca por cliente

        if empresa:
            queryset = queryset.filter(empresa__nome__icontains=empresa)

        if sequencia:
            queryset = queryset.filter(sequencia=sequencia)

        if start_date and end_date:
            queryset = queryset.filter(criacao__gte=start_date, criacao__lte=end_date)

        if cliente:
            queryset = queryset.filter(cliente__icontains=cliente)  # Filtro para cliente

        return queryset.order_by('-criacao')

    def perform_create(self, serializer):
        user = self.request.user

        try:
            user_empresas = Usuarios.objects.get(id=user.id).empresa.all()
        except Usuarios.DoesNotExist:
            return Response({'error': 'Usuário não encontrado'}, status=status.HTTP_400_BAD_REQUEST)

        if not user_empresas.exists():
            return Response(
                {'error': 'Usuário não está associado a nenhuma empresa.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        empresa = user_empresas.first()
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
            Tickets.objects.annotate(month=TruncDay('criacao'))
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
        time_stats = (
            Tickets.objects.annotate(hour=TruncTime('horario'))
            .values('hour')
            .annotate(
                emitidos=Count('id'),
                concluidos=Count('id', filter=Q(concluido=True))
            )
            .order_by('hour')
        )

        data = {
            'monthly_stats': list(monthly_stats),
            'daily_stats': list(daily_stats),
            'time_stats' : list(time_stats),
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
            empresas = user_empresa.empresa.all() 
            grupo = user_empresa.grupo
        except Usuarios.DoesNotExist:
            empresas = []
            grupo = None

        response_data = {
            'access': serializer.validated_data['access'],
            'refresh': serializer.validated_data['refresh'],
            'user_id': user.id,
            'username': user.username,
            'empresas': [empresa.id for empresa in empresas], 
            'grupo': grupo.id if grupo else None,  
        }
        
        return Response(response_data)



class ImagensViewSet(viewsets.ModelViewSet):
    queryset = Imagens.objects.all()
    serializer_class = ImagensSerializer

    def create(self, request, *args, **kwargs):
        ticket_id = request.data.get('ticket')
        
        # Obtém o objeto ticket
        ticket = get_object_or_404(Tickets, id=ticket_id)
        
        # Verifica se o ticket já tem uma imagem
        if Imagens.objects.filter(ticket=ticket).exists():
            return Response({'error': 'Este ticket já possui uma imagem associada.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtém o arquivo da imagem
        arquivo = request.FILES.get('imagem')  # Supondo que o campo se chama 'imagem'

        if not arquivo:
            return Response({'error': 'Arquivo de imagem não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)

        # Salva a imagem no banco de dados com o CloudinaryField gerenciando o upload
        try:
            imagem = Imagens(
                nome=arquivo.name,
                imagem=arquivo,  # O CloudinaryField faz o upload automaticamente
                ticket=ticket
            )
            imagem.save()
            serializer = self.get_serializer(imagem)
            return Response( serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def list_by_ticket(self, request, ticket_id):
        ticket = get_object_or_404(Tickets, id=ticket_id)
        imagens = Imagens.objects.filter(ticket=ticket)
        serializer = self.get_serializer(imagens, many=True)
        return Response(serializer.data)   
        

class NotaFiscalViewSet(viewsets.ModelViewSet):
    queryset = NotaFiscal.objects.all()
    serializer_class = NotaFiscalSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Salva o objeto NotaFiscal com o PDF e associa ao ticket
        nota_fiscal = self.perform_create(serializer)

        # Gera a URL completa para o PDF
        pdf_url = request.build_absolute_uri(nota_fiscal.arquivo.url)

        headers = self.get_success_headers(serializer.data)
        data_with_pdf_url = serializer.data
        data_with_pdf_url['pdf_url'] = pdf_url

        return Response(data_with_pdf_url, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        # Este método é chamado durante a criação para salvar o objeto e retornar o objeto salvo
        return serializer.save()