# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-03-16 07:55


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resume', '0004_auto_20170314_0556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='github',
            name='profile_name',
            field=models.CharField(blank=True, help_text="User's Full Name", max_length=50, null=True),
        ),
    ]
