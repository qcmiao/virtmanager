# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-24 04:54
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0002_virtmachine_vm_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtmachine',
            name='description',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
