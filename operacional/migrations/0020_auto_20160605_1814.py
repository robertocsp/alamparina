# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0019_importacao'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='altura',
            field=models.FloatField(verbose_name=b'altura'),
        ),
        migrations.AlterField(
            model_name='produto',
            name='largura',
            field=models.FloatField(verbose_name=b'largura'),
        ),
        migrations.AlterField(
            model_name='produto',
            name='profundidade',
            field=models.FloatField(verbose_name=b'profundidade'),
        ),
    ]
