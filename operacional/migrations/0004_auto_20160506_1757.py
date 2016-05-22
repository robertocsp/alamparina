# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0003_expedicao_gravou_estoque'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expedicao',
            name='gravou_estoque',
            field=models.BooleanField(default=False),
        ),
    ]
