# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0026_auto_20160616_2120'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkout',
            name='erro',
        ),
        migrations.AlterField(
            model_name='checkout',
            name='motivo',
            field=models.CharField(max_length=20, choices=[(b'emprestimo', b'Emprestimo'), (b'consignacao', b'Consignacao'), (b'avaria', b'Avaria'), (b'venda', b'Venda'), (b'devolucao', b'Devolucao'), (b'erro', b'Erro')]),
        ),
    ]
