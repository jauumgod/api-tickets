from django.apps import AppConfig
from django.db import connection


class TicketappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticketApp'

    def ready(self):
        with connection.cursor() as cursor:
            cursor.execute("SET time_zone = '+3:00';")
