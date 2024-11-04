from django.shortcuts import get_object_or_404
from rest_framework import serializers
from .models import Empresas, Grupos, NotaFiscal, Sequencia, Tickets, Usuarios, Imagens
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response


class EmpresaSerializers(serializers.ModelSerializer):
    class Meta:
        model = Empresas
        fields = '__all__'

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grupos
        fields = '__all__'
    
class SequenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sequencia
        fields = '__all__'


class TicketSerializers(serializers.ModelSerializer):
    empresa = EmpresaSerializers(read_only=True)
    class Meta:
        model = Tickets
        fields = ['id', 'sequencia', 'criacao','horario', 'placa','produto', 'transportadora', 'motorista','operador', 'cliente', 
                  'peso_entrada', 'peso_saida','umidade','concluido', 'peso_liquido', 'lote_leira', 'ticket_cancelado',
                  'usuario','empresa', 'imagens', 'nf']
        read_only_fields = ['sequencia', 'criacao', 'empresa','usuario']
        extra_kwargs = {
            'concluido' : {'required': False}
        }
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if 'criacao' in rep:
            rep['criacao'] = instance.criacao.isoformat()  # Formato ISO 8601
        return rep


class UsuarioSerializer(serializers.ModelSerializer):
    empresa = serializers.PrimaryKeyRelatedField(queryset=Empresas.objects.all(), many=True)  # Permite múltiplas empresas
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Usuarios
        fields = ['id', 'username', 'password', 'empresa', 'grupo']

    def create(self, validated_data):
        # Remove empresas do validated_data para tratar separadamente
        empresas = validated_data.pop('empresa', [])  # Note o plural aqui
        
        # Faz o hash da senha usando make_password
        password = validated_data.pop('password')
        validated_data['password'] = make_password(password)  # Faz a criptografia aqui

        # Cria o usuário com a senha hasheada
        usuario = Usuarios(**validated_data)
        usuario.save()

        # Associa as empresas ao usuário
        usuario.empresa.set(empresas)  # Isso vai associar as empresas

        return usuario


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Adicione campos personalizados ao token, se necessário
        token['username'] = user.username
        token['email'] = user.email

        return token

    def validate(self, attrs):
        # Usar o modelo de usuário personalizado para autenticação
        data = super().validate(attrs)
        user = Usuarios.objects.get(username=attrs['username'])
        
        return data
        
class ImagensSerializer(serializers.ModelSerializer):
    imagem_url = serializers.SerializerMethodField()

    class Meta:
        model = Imagens
        fields = ['id', 'nome', 'imagem', 'ticket', 'imagem_url']

    def get_imagem_url(self, obj):
        # Construa a URL completa com o domínio do Cloudinary
        return f"https://res.cloudinary.com/dvesknzr8/{obj.imagem}"


    def validate(self, data):
        # Verifica se o ticket já tem uma imagem
        if Imagens.objects.filter(ticket=data['ticket']).exists():
            raise serializers.ValidationError("Este ticket já possui uma imagem associada.")
        return data
    
    



class NotaFiscalSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotaFiscal
        fields = ['nfe', 'arquivo', 'ticket']

    
    def validate(self, data):
        if NotaFiscal.objects.filter(ticket=data['ticket']).exists():
            raise serializers.ValidationError("Esse ticket ja possui NFs associada.")
        return data