# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.CharField(max_length=300)),
                ('largura', models.IntegerField()),
                ('altura', models.IntegerField()),
                ('profundidade', models.IntegerField()),
                ('marca', models.ForeignKey(to='administrativo.Marca')),
            ],
        ),
    ]
