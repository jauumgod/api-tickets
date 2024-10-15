from django.contrib import admin
from .models import Usuarios, Empresas, Grupos

admin.site.register(Empresas)
admin.site.register(Usuarios)
admin.site.register(Grupos)