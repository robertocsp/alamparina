# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0007_auto_20160512_1916'),
    ]

    operations = [
        migrations.AddField(
            model_name='marca',
            name='agencia',
            field=models.CharField(max_length=6, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='marca',
            name='banco',
            field=models.CharField(max_length=4, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='marca',
            name='cnpj_cpf_titular_conta',
            field=models.CharField(max_length=18, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='marca',
            name='conta',
            field=models.CharField(max_length=8, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='marca',
            name='nome_titular_conta',
            field=models.CharField(max_length=150, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='marca',
            name='responsavel_cpf',
            field=models.CharField(max_length=18, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='marca',
            name='responsavel_telefone',
            field=models.CharField(max_length=20, null=True, blank=True),
        ),
    ]
