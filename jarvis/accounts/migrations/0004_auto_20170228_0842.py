# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-02-28 08:42


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20170228_0759'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='deleted_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='deleted_date',
            field=models.DateTimeField(null=True),
        ),
    ]
