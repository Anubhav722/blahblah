# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-04-04 12:10


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20170228_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='deleted_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='deleted_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
