# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-22 05:45


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resume', '0017_auto_20170522_0542'),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='company',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='resume.Company'),
        ),
        migrations.AddField(
            model_name='resume',
            name='institution',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='resume.Institution'),
        ),
        migrations.AddField(
            model_name='resume',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='resume.Location'),
        ),
    ]
