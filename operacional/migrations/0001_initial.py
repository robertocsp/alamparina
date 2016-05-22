# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('administrativo', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipo', models.CharField(default=b'chin', max_length=15, choices=[(b'chin', b'CheckIn'), (b'chout', b'CheckOut')])),
                ('status', models.CharField(default=b'emprocessamento', max_length=20, choices=[(b'emprocessamento', b'EmProcessamento'), (b'enviado', b'Enviado'), (b'emanalise', b'EmAnalise'), (b'confirmado', b'Confirmado')])),
                ('dia_agendamento', models.DateField()),
                ('hora_agendamento', models.TimeField(null=True)),
                ('observacao', models.TextField(blank=True)),
                ('motivo', models.CharField(default=b'creditarestoque', max_length=20, choices=[(b'creditarestoque', b'CreditarEstoque'), (b'comprafornecedor', b'CompraFornecedor')])),
                ('canal', models.ManyToManyField(to='administrativo.Canal')),
                ('marca', models.ForeignKey(blank=True, to='administrativo.Marca', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Checkout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('motivo', models.CharField(max_length=20, choices=[(b'emprestimo', b'Emprestimo'), (b'consignacao', b'Consignacao'), (b'avaria', b'Avaria'), (b'venda', b'Venda')])),
                ('dia', models.DateField(auto_now_add=True)),
                ('hora', models.TimeField(auto_now_add=True)),
                ('observacao', models.TextField(blank=True)),
                ('dtrealizado', models.DateField(null=True, blank=True)),
                ('quantidade', models.IntegerField()),
                ('preco_venda', models.FloatField(null=True, verbose_name=b'pre\xc3\xa7o venda', blank=True)),
                ('canal', models.ForeignKey(blank=True, to='administrativo.Canal', null=True)),
                ('marca', models.ForeignKey(to='administrativo.Marca')),
                ('periodo', models.ForeignKey(blank=True, to='administrativo.Periodo', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Estoque',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantidade', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Expedicao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantidade', models.IntegerField()),
                ('status', models.CharField(blank=True, max_length=20, null=True, choices=[(b'ok', b'ProdutoOK'), (b'avariado', b'ProdutoAvariado'), (b'ausente', b'Ausente')])),
                ('observacao', models.TextField(blank=True)),
                ('checkin', models.ForeignKey(to='operacional.Checkin')),
            ],
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, verbose_name=b'nome')),
                ('codigo', models.CharField(max_length=20, verbose_name=b'codigo', blank=True)),
                ('descricao', models.CharField(max_length=300, verbose_name=b'Descricao')),
                ('largura', models.IntegerField(verbose_name=b'largura')),
                ('altura', models.IntegerField(verbose_name=b'altura')),
                ('profundidade', models.IntegerField(verbose_name=b'profundidade')),
                ('quantidade', models.IntegerField(default=0, verbose_name=b'quantidade')),
                ('preco_base', models.FloatField(null=True, verbose_name=b'pre\xc3\xa7o base', blank=True)),
                ('preco_venda', models.FloatField(null=True, verbose_name=b'pre\xc3\xa7o venda', blank=True)),
                ('em_estoque', models.CharField(default=b'nao', max_length=5, choices=[(b'sim', b'Sim'), (b'nao', b'Nao')])),
                ('espaco', models.ForeignKey(blank=True, to='administrativo.Espaco', null=True)),
                ('marca', models.ForeignKey(to='administrativo.Marca')),
                ('unidade', models.ManyToManyField(to='administrativo.Unidade', through='operacional.Estoque')),
            ],
        ),
        migrations.CreateModel(
            name='Recomendacao',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=100, verbose_name=b'nome')),
                ('email', models.CharField(max_length=30, verbose_name=b'email', blank=True)),
                ('website', models.CharField(max_length=30, verbose_name=b'website', blank=True)),
                ('telefone', models.CharField(max_length=20, verbose_name=b'telefone', blank=True)),
                ('comentario', models.CharField(max_length=200, verbose_name=b'comentario', blank=True)),
                ('marca', models.ForeignKey(to='administrativo.Marca')),
            ],
        ),
        migrations.AddField(
            model_name='expedicao',
            name='produto',
            field=models.ForeignKey(to='operacional.Produto'),
        ),
        migrations.AddField(
            model_name='estoque',
            name='produto',
            field=models.ForeignKey(to='operacional.Produto'),
        ),
        migrations.AddField(
            model_name='estoque',
            name='unidade',
            field=models.ForeignKey(to='administrativo.Unidade'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='produto',
            field=models.ForeignKey(to='operacional.Produto'),
        ),
        migrations.AddField(
            model_name='checkout',
            name='unidade',
            field=models.ForeignKey(to='administrativo.Unidade'),
        ),
        migrations.AddField(
            model_name='checkin',
            name='produto',
            field=models.ManyToManyField(to='operacional.Produto', through='operacional.Expedicao'),
        ),
        migrations.AddField(
            model_name='checkin',
            name='unidade',
            field=models.ForeignKey(to='administrativo.Unidade'),
        ),
        migrations.AlterUniqueTogether(
            name='expedicao',
            unique_together=set([('checkin', 'produto')]),
        ),
        migrations.AlterUniqueTogether(
            name='estoque',
            unique_together=set([('produto', 'unidade')]),
        ),
    ]
