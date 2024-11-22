# Generated by Django 5.1.1 on 2024-10-23 19:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Empresas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('cnpj', models.CharField(max_length=20)),
                ('endereco', models.CharField(max_length=255)),
                ('cidade', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Grupos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('descricao', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Usuarios',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('empresa', models.ManyToManyField(blank=True, related_name='usuarios', to='ticketApp.empresas')),
                ('grupo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='usuarios', to='ticketApp.grupos')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Sequencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proximo_numero', models.IntegerField(default=1)),
                ('empresa', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sequencia', to='ticketApp.empresas')),
            ],
        ),
        migrations.CreateModel(
            name='Tickets',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sequencia', models.IntegerField(blank=True, null=True)),
                ('criacao', models.DateField(auto_now_add=True)),
                ('placa', models.CharField(max_length=100)),
                ('produto', models.CharField(blank=True, max_length=255)),
                ('transportadora', models.CharField(max_length=255)),
                ('motorista', models.CharField(max_length=255)),
                ('operador', models.CharField(blank=True, max_length=255)),
                ('cliente', models.CharField(max_length=255)),
                ('peso_entrada', models.FloatField()),
                ('peso_saida', models.FloatField()),
                ('peso_liquido', models.FloatField()),
                ('lote_leira', models.CharField(max_length=100)),
                ('umidade', models.CharField(blank=True, max_length=10)),
                ('concluido', models.BooleanField(blank=True, default=False)),
                ('ticket_cancelado', models.BooleanField(default=False)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to='ticketApp.empresas')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tickets', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Imagens',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('imagem', models.ImageField(blank=True, upload_to='imagens_tickets/')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='imagens', to='ticketApp.tickets')),
            ],
        ),
    ]
