# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0023_produto_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='erro',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Erro', blank=True),
        ),
        migrations.AlterField(
            model_name='checkout',
            name='motivo',
            field=models.CharField(max_length=20, choices=[(b'emprestimo', b'Emprestimo'), (b'consignacao', b'Consignacao'), (b'avaria', b'Avaria'), (b'venda', b'Venda'), (b'devolucao', b'Devolucao')]),
        ),
    ]
