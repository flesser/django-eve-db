# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eve_db', '0002_auto_20140915_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planetschematicstypemap',
            name='is_input',
            field=models.BooleanField(default=False),
        ),
    ]
