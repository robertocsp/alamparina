# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0009_remove_checkout_marca'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkout',
            name='formapagamento',
            field=models.CharField(blank=True, max_length=20, null=True, choices=[(b'credito', b'Credito'), (b'debito', b'Debito'), (b'dinheiro', b'Dinheiro'), (b'cheque', b'Cheque')]),
        ),
    ]
