from django.contrib import admin
from .models import Usuarios, Empresas, Grupos, Tickets, Produto

admin.site.register(Empresas)
admin.site.register(Usuarios)
admin.site.register(Grupos)
admin.site.register(Tickets)
admin.site.register(Produto)