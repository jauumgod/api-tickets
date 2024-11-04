from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from cloudinary.models import CloudinaryField



class Empresas(models.Model):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=20)
    endereco = models.CharField(max_length=255)
    cidade = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
    
class Grupos(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nome
    
class UserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('O campo username é obrigatório')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

class Usuarios(AbstractBaseUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    empresa = models.ManyToManyField(Empresas, related_name='usuarios',blank=True)
    grupo = models.ForeignKey(Grupos, related_name='usuarios',null=True, blank=True, on_delete=models.CASCADE)


    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

class Sequencia(models.Model):
    empresa = models.OneToOneField(Empresas, on_delete=models.CASCADE, related_name='sequencia')
    proximo_numero = models.IntegerField(default=1)

    def gerar_sequencia(self):
        numero_atual = self.proximo_numero
        self.proximo_numero +=1
        self.save()
        return numero_atual
    
    def __str__(self):
        return f'Sequencia para {self.empresa.nome}'


class Tickets(models.Model):
    sequencia = models.IntegerField(null=True, blank=True)
    criacao = models.DateField(auto_now_add=True, blank=True)
    horario = models.TimeField(blank=True, null=True)
    placa = models.CharField(max_length=100)
    produto = models.CharField(max_length=255, blank=True)
    transportadora = models.CharField(max_length=255)
    motorista = models.CharField(max_length=255)
    operador = models.CharField(max_length=255, blank=True)
    cliente = models.CharField(max_length=255)
    peso_entrada = models.FloatField()
    peso_saida = models.FloatField()
    peso_liquido = models.FloatField()
    lote_leira = models.CharField(max_length=100)
    umidade = models.CharField(max_length=10, blank=True)
    concluido = models.BooleanField(blank=True, default=False)
    ticket_cancelado = models.BooleanField(default=False)
    usuario = models.ForeignKey(Usuarios,
                                on_delete=models.CASCADE,
                                related_name='tickets',
                                null=True,blank=True )
    empresa = models.ForeignKey(Empresas, on_delete=models.CASCADE, related_name='tickets')

    def save(self, *args, **kwargs):
        if self.pk is None:  # Somente gerar para um novo ticket
            sequencia_obj, created = Sequencia.objects.get_or_create(empresa=self.empresa)
            self.sequencia = sequencia_obj.gerar_sequencia()
        if not self.horario:
            self.horario = timezone.now().time()
        
        # Chama o método save do modelo pai corretamente
        super().save(*args, **kwargs)
    
    def __str__(self):
        return str(self.id)



class Imagens(models.Model):
    nome = models.CharField(max_length=255)
    ticket = models.ForeignKey(Tickets, on_delete=models.CASCADE, related_name='imagens')
    imagem = CloudinaryField('imagem', blank=True)
    pdf = CloudinaryField('pdf', blank=True)  # Campo para armazenar PDF

    def clean(self):
        if Imagens.objects.filter(ticket=self.ticket).exists():
            raise ValidationError("Este ticket já possui uma imagem associada.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


#================TABELA DE NOTAS EMITIDAS PARA VINCULAR AO TICKET.=============#

class NotaFiscal(models.Model):
    nfe = models.CharField(max_length=255, blank=True)
    criacao = models.DateField(auto_now=True)
    arquivo = CloudinaryField('arquivo', blank=True, resource_type='raw')  # Mudado para CloudinaryField
    ticket = models.ForeignKey(Tickets, on_delete=models.CASCADE, related_name='nf')

    def __str__(self):
        return self.nfe



