# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0011_auto_20160516_2301'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='status',
            field=models.CharField(default=b'emprocessamento', max_length=20, choices=[(b'emprocessamento', b'EmProcessamento'), (b'confirmado', b'Confirmado')]),
        ),
    ]
