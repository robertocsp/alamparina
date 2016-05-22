# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0010_checkout_formapagamento'),
    ]

    operations = [
        migrations.CreateModel(
            name='ItemVenda',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantidade', models.IntegerField()),
                ('status', models.CharField(blank=True, max_length=20, null=True, choices=[(b'ok', b'ProdutoOK'), (b'avariado', b'ProdutoAvariado'), (b'ausente', b'Ausente')])),
                ('observacao', models.TextField(blank=True)),
                ('gravou_estoque', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='checkout',
            name='formapagamento',
            field=models.CharField(blank=True, max_length=20, null=True, choices=[(b'credito', b'Cr\xc3\xa9dito'), (b'debito', b'D\xc3\xa9bito'), (b'dinheiro', b'Dinheiro'), (b'cheque', b'Cheque')]),
        ),
        migrations.AddField(
            model_name='itemvenda',
            name='checkout',
            field=models.ForeignKey(to='operacional.Checkout'),
        ),
        migrations.AddField(
            model_name='itemvenda',
            name='produto',
            field=models.ForeignKey(to='operacional.Produto'),
        ),
        migrations.AlterUniqueTogether(
            name='itemvenda',
            unique_together=set([('checkout', 'produto')]),
        ),
    ]
