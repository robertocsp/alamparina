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
            name='Canal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=30, verbose_name=b'Nome')),
                ('percentual_deflacao', models.FloatField(null=True, blank=True)),
                ('custo_embalagem', models.IntegerField(null=True, blank=True)),
                ('custo_entrega', models.IntegerField(null=True, blank=True)),
                ('acumulativo', models.BooleanField(default=False)),
                ('tipo', models.CharField(default=b'unidade', max_length=15, choices=[(b'unidade', b'Unidade'), (b'catalogo', b'Catalogo'), (b'ecommerce', b'Ecommerce'), (b'revenda', b'Revenda')])),
            ],
        ),
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('no_contrato', models.CharField(max_length=30, verbose_name=b'no_contrato')),
                ('data_contrato', models.DateField()),
                ('valor', models.FloatField(null=True, blank=True)),
                ('identificador', models.CharField(max_length=20, blank=True)),
                ('percentual_deflacao', models.FloatField()),
                ('custo_embalagem', models.IntegerField()),
                ('custo_entrega', models.IntegerField()),
                ('observacao', models.CharField(max_length=200, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Espaco',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('identificador', models.CharField(max_length=20)),
                ('disponivel', models.BooleanField(default=True)),
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
                ('codigo', models.CharField(max_length=5, blank=True)),
                ('sequencial_atual', models.IntegerField(default=0)),
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
        migrations.CreateModel(
            name='Unidade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=50)),
                ('endereco', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='espaco',
            name='tipo',
            field=models.ForeignKey(to='administrativo.TipoEspaco'),
        ),
        migrations.AddField(
            model_name='espaco',
            name='unidade',
            field=models.ForeignKey(related_name='espaco', blank=True, to='administrativo.Unidade', null=True),
        ),
        migrations.AddField(
            model_name='contrato',
            name='espaco',
            field=models.ManyToManyField(related_name='contrato', to='administrativo.Espaco'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='marca',
            field=models.ForeignKey(to='administrativo.Marca'),
        ),
        migrations.AddField(
            model_name='contrato',
            name='periodo',
            field=models.ManyToManyField(to='administrativo.Periodo'),
        ),
    ]
