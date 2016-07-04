# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0014_auto_20160516_1530'),
        ('operacional', '0014_itemvenda_preco_venda'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='marca',
            field=models.ForeignKey(blank=True, to='administrativo.Marca', null=True),
        ),
    ]
