# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0002_auto_20160504_1021'),
        ('operacional', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produto',
            name='espaco',
        ),
        migrations.AddField(
            model_name='produto',
            name='miniloja',
            field=models.ForeignKey(blank=True, to='administrativo.Miniloja', null=True),
        ),
    ]
