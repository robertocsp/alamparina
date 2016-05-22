# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Miniloja',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identificador', models.CharField(max_length=20)),
                ('disponivel', models.BooleanField(default=True)),
            ],
        ),
        migrations.RenameModel(
            old_name='TipoEspaco',
            new_name='TipoMiniloja',
        ),
        migrations.RemoveField(
            model_name='espaco',
            name='tipo',
        ),
        migrations.RemoveField(
            model_name='espaco',
            name='unidade',
        ),
        migrations.RemoveField(
            model_name='contrato',
            name='espaco',
        ),
    ]
