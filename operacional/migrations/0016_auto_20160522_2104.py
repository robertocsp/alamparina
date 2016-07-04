# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0015_checkout_marca'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='estoque_minimo',
            field=models.IntegerField(default=0, verbose_name=b'Estoque M\xc3\xadnimo'),
        ),
        migrations.AddField(
            model_name='produto',
            name='garantia',
            field=models.IntegerField(default=0, verbose_name=b'Garantia'),
        ),
        migrations.AddField(
            model_name='produto',
            name='itens_inclusos',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Itens inclusos'),
        ),
        migrations.AddField(
            model_name='produto',
            name='ncm',
            field=models.CharField(max_length=100, null=True, verbose_name=b'NCM'),
        ),
        migrations.AddField(
            model_name='produto',
            name='palavras_chaves',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Palavras chaves'),
        ),
        migrations.AddField(
            model_name='produto',
            name='peso',
            field=models.FloatField(null=True, verbose_name=b'peso', blank=True),
        ),
        migrations.AddField(
            model_name='produto',
            name='unidade_venda',
            field=models.CharField(default=b'unidade', max_length=15, choices=[(b'unidade', b'UND (Unidade)'), (b'pacote', b'PCT (Pacote)'), (b'kit', b'Kit (Kit de presentes)')]),
        ),
    ]
