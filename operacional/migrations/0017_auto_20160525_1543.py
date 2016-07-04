# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0016_auto_20160522_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produto',
            name='itens_inclusos',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Itens inclusos', blank=True),
        ),
        migrations.AlterField(
            model_name='produto',
            name='ncm',
            field=models.CharField(max_length=100, null=True, verbose_name=b'NCM', blank=True),
        ),
        migrations.AlterField(
            model_name='produto',
            name='palavras_chaves',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Palavras chaves', blank=True),
        ),
    ]
