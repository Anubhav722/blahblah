# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-22 05:34


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resume', '0015_auto_20170512_0749'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='resume',
            name='company',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='institution',
        ),
        migrations.RemoveField(
            model_name='resume',
            name='location',
        ),
    ]
