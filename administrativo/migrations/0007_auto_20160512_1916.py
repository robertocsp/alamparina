# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0006_auto_20160512_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='marca',
            name='cnpj_cpf',
            field=models.CharField(max_length=18),
        ),
    ]
