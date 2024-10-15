from rest_framework import serializers
from .models import Empresas, Grupos, Sequencia, Tickets, Usuarios, Imagens
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



class EmpresaSerializers(serializers.ModelSerializer):
    class Meta:
        model = Empresas
        fields = '__all__'
    
class SequenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sequencia
        fields = '__all__'


class TicketSerializers(serializers.ModelSerializer):
    empresa = EmpresaSerializers(read_only=True)
    class Meta:
        model = Tickets
        fields = ['id', 'sequencia', 'criacao', 'placa','produto', 'transportadora', 'motorista','operador', 'cliente', 
                  'peso_entrada', 'peso_saida','umidade','concluido', 'peso_liquido', 'lote_leira', 'ticket_cancelado',
                  'usuario','empresa']
        read_only_fields = ['sequencia', 'criacao', 'empresa','usuario']
        extra_kwargs = {
            'concluido' : {'required': False}
        }

class UsuarioSerializer(serializers.ModelSerializer):
    empresas = serializers.PrimaryKeyRelatedField(queryset=Empresas.objects.all(), many=True)  # Permite selecionar múltiplas empresas
    password = serializers.CharField(write_only=True)  # Campo para password

    class Meta:
        model = Usuarios  # Refere-se ao seu modelo de usuários personalizado
        fields = ['id', 'username', 'password', 'empresas', 'grupos']

    def create(self, validated_data):
        empresas = validated_data.pop('empresas', [])  # Remove empresas do validated_data
        
        # Faz o hash da senha
        password = validated_data['password']
        hashed_password = make_password(password)

        # Cria o usuário com a senha hasheada
        usuario = Usuarios(**validated_data)  # Cria uma instância do modelo
        usuario.password = hashed_password  # Define a senha hasheada
        usuario.save()  # Salva o usuário no banco de dados

        # Associar as empresas ao usuário, se necessário
        usuario.empresas.set(empresas)  # Isso irá criar as associações com as empresas

        return usuario

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grupos
        fields = ['id', 'name']


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
    class Meta:
        model = Imagens
        fields = ['id', 'nome', 'imagem', 'ticket']