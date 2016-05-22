# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0013_auto_20160516_1518'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('telefone', models.CharField(max_length=13)),
                ('nome', models.CharField(max_length=50)),
                ('aniversario', models.DateField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cliente_Unidade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cliente', models.ForeignKey(to='administrativo.Cliente')),
                ('unidade', models.ForeignKey(to='administrativo.Unidade')),
            ],
        ),
        migrations.AddField(
            model_name='cliente',
            name='unidades',
            field=models.ManyToManyField(to='administrativo.Unidade', through='administrativo.Cliente_Unidade'),
        ),
    ]
