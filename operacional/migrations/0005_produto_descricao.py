# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0004_remove_produto_descricao'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='descricao',
            field=models.CharField(default=datetime.datetime(2016, 3, 3, 19, 57, 36, 535093, tzinfo=utc), max_length=300),
            preserve_default=False,
        ),
    ]
