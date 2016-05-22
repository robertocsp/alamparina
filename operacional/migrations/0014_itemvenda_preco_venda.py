# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0013_auto_20160517_0049'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemvenda',
            name='preco_venda',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
