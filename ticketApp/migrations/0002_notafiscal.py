# Generated by Django 5.1.1 on 2024-10-31 20:54

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ticketApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotaFiscal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nfe', models.CharField(blank=True, max_length=255)),
                ('criacao', models.DateField(auto_now=True)),
                ('arquivo', models.FileField(blank=True, upload_to='notas_fiscais/', validators=[django.core.validators.FileExtensionValidator(['pdf'])])),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notafiscal', to='ticketApp.tickets')),
            ],
        ),
    ]