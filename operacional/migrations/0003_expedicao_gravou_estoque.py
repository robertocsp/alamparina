# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0002_auto_20160504_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='expedicao',
            name='gravou_estoque',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
