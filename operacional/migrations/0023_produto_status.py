# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0022_auto_20160606_1407'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='status',
            field=models.CharField(default=b'inativo', max_length=20, choices=[(b'ativo', b'Ativo'), (b'inativo', b'Inativo')]),
        ),
    ]
