from django.contrib import admin
from .models import Usuarios, Empresas, Grupos, Tickets

admin.site.register(Empresas)
admin.site.register(Usuarios)
admin.site.register(Grupos)
admin.site.register(Tickets)