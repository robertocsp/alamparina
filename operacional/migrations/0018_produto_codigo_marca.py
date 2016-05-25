# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0017_auto_20160525_1543'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='codigo_marca',
            field=models.CharField(max_length=20, null=True, verbose_name=b'Descricao', blank=True),
        ),
    ]
