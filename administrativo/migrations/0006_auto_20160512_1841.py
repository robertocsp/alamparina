# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0005_auto_20160506_1941'),
    ]

    operations = [
        migrations.AlterField(
            model_name='canal',
            name='custo_embalagem',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='canal',
            name='custo_entrega',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='contrato',
            name='custo_embalagem',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='contrato',
            name='custo_entrega',
            field=models.FloatField(),
        ),
    ]
