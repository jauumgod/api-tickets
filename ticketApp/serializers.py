from rest_framework import serializers
from .models import Empresas, Grupos, Sequencia, Tickets, Usuarios, Imagens
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer



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
        fields = ['id', 'sequencia', 'criacao', 'placa','produto', 'transportadora', 'motorista','operador', 'cliente', 
                  'peso_entrada', 'peso_saida','umidade','concluido', 'peso_liquido', 'lote_leira', 'ticket_cancelado',
                  'usuario','empresa']
        read_only_fields = ['sequencia', 'criacao', 'empresa','usuario']
        extra_kwargs = {
            'concluido' : {'required': False}
        }

class UsuarioSerializer(serializers.ModelSerializer):
    empresa = serializers.PrimaryKeyRelatedField(queryset=Empresas.objects.all(), many=True)  # Permite selecionar múltiplas empresas
    password = serializers.CharField(write_only=True)  # Campo para password

    class Meta:
        model = Usuarios  # Refere-se ao seu modelo de usuários personalizado
        fields = ['id', 'username', 'password', 'empresa', 'grupo']  # Certifique-se de incluir 'empresas' nos fields

    def create(self, validated_data):
        # Remove empresas do validated_data para tratar separadamente
        empresas = validated_data.pop('empresa', [])  # Note o plural aqui
        
        # Faz o hash da senha
        password = validated_data['password']
        hashed_password = make_password(password)

        # Cria o usuário com a senha hasheada
        usuario = Usuarios(**validated_data)
        usuario.password = hashed_password
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
    class Meta:
        model = Imagens
        fields = ['id', 'nome', 'imagem', 'ticket']