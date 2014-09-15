# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eve_db', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dgmattributecategory',
            name='description',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='dgmattributecategory',
            name='name',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
