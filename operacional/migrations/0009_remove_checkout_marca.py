# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('operacional', '0008_checkout_cliente_unidade'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkout',
            name='marca',
        ),
    ]
