# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-05-30 09:22


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('resume', '0024_auto_20170525_0637'),
    ]

    operations = [
        migrations.RenameField(
            model_name='resume',
            old_name='company',
            new_name='companies',
        ),
        migrations.RenameField(
            model_name='resume',
            old_name='institution',
            new_name='institutions',
        ),
    ]
