# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0004_auto_20160506_1757'),
    ]

    operations = [
        migrations.AlterField(
            model_name='periodo',
            name='pagamento_ate',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='periodo',
            name='pagamento_de',
            field=models.DateField(null=True, blank=True),
        ),
    ]
