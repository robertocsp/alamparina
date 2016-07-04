# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0020_auto_20160605_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importacao',
            name='arquivo',
            field=models.CharField(max_length=40, null=True, blank=True),
        ),
    ]
