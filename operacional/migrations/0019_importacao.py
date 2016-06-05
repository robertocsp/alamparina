# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import operacional.models


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0014_auto_20160516_1530'),
        ('operacional', '0018_produto_codigo_marca'),
    ]

    operations = [
        migrations.CreateModel(
            name='Importacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dia', models.DateField(auto_now_add=True)),
                ('hora', models.TimeField(auto_now_add=True)),
                ('arquivo', models.FileField(upload_to=operacional.models.get_upload_file_name)),
                ('status', models.CharField(blank=True, max_length=20, null=True, choices=[(b'recebido', b'Recebido'), (b'erronoarquivo', b'ErroNoArquivo'), (b'importadocomsucesso', b'ImportadoComSucesso')])),
                ('marca', models.ForeignKey(to='administrativo.Marca')),
            ],
        ),
    ]
