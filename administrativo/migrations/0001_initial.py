# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Alocacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_alocacao', models.DateField()),
                ('identificador', models.CharField(max_length=20, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Espaco',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identificador', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Loja',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=50)),
                ('endereco', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=50)),
                ('razao_social', models.CharField(max_length=100)),
                ('cnpj_cpf', models.IntegerField()),
                ('endereco', models.CharField(max_length=100)),
                ('contato', models.CharField(max_length=100, blank=True)),
                ('logo', models.ImageField(upload_to=b'/var/www/html/logos', blank=True)),
                ('user', models.ManyToManyField(related_name='marca', null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Periodo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=30)),
                ('de', models.DateField()),
                ('ate', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='TipoEspaco',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('largura', models.IntegerField()),
                ('altura', models.IntegerField()),
                ('profundidade', models.IntegerField()),
                ('tipo', models.CharField(max_length=10)),
                ('preco', models.FloatField()),
            ],
        ),
        migrations.AddField(
            model_name='espaco',
            name='loja',
            field=models.ForeignKey(blank=True, to='administrativo.Loja', null=True),
        ),
        migrations.AddField(
            model_name='espaco',
            name='tipo',
            field=models.ForeignKey(to='administrativo.TipoEspaco'),
        ),
        migrations.AddField(
            model_name='alocacao',
            name='espaco',
            field=models.ManyToManyField(to='administrativo.Espaco'),
        ),
        migrations.AddField(
            model_name='alocacao',
            name='marca',
            field=models.ForeignKey(to='administrativo.Marca'),
        ),
        migrations.AddField(
            model_name='alocacao',
            name='periodo',
            field=models.ManyToManyField(to='administrativo.Periodo'),
        ),
    ]
