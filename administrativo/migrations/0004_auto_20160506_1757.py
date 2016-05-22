# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0003_auto_20160504_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='periodo',
            name='pagamento_ate',
            field=models.DateField(default='2016-05-05'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='periodo',
            name='pagamento_de',
            field=models.DateField(default='2016-05-05'),
            preserve_default=False,
        ),
    ]
