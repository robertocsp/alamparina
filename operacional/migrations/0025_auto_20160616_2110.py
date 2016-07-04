# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0024_auto_20160616_2104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkout',
            name='erro',
        ),
        migrations.AlterField(
            model_name='checkout',
            name='formapagamento',
            field=models.CharField(blank=True, max_length=20, null=True, choices=[(b'credito', b'Cr\xc3\xa9dito'), (b'debito', b'D\xc3\xa9bito'), (b'dinheiro', b'Dinheiro'), (b'cheque', b'Cheque'), (b'erro', b'Erro')]),
        ),
    ]
