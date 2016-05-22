# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0012_checkout_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkout',
            name='produto',
            field=models.ForeignKey(blank=True, to='operacional.Produto', null=True),
        ),
    ]
