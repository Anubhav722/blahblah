# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-05-31 07:09


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resume', '0027_auto_20170530_1428'),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='job_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
