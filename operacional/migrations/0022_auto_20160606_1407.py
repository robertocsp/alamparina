# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0021_auto_20160605_2052'),
    ]

    operations = [
        migrations.AlterField(
            model_name='importacao',
            name='arquivo',
            field=models.FileField(max_length=40, null=True, upload_to=b'', blank=True),
        ),
    ]
