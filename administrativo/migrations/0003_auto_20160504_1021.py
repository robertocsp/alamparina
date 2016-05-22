# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0002_auto_20160504_1021'),
        ('operacional', '0002_auto_20160504_1021'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Espaco',
        ),
        migrations.AddField(
            model_name='miniloja',
            name='tipo',
            field=models.ForeignKey(to='administrativo.TipoMiniloja'),
        ),
        migrations.AddField(
            model_name='miniloja',
            name='unidade',
            field=models.ForeignKey(related_name='miniloja', blank=True, to='administrativo.Unidade', null=True),
        ),
        migrations.AddField(
            model_name='contrato',
            name='miniloja',
            field=models.ManyToManyField(related_name='contrato', to='administrativo.Miniloja'),
        ),
    ]
