# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-02-28 07:59


import jarvis.accounts.generators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20170223_1315'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField()),
                ('key', models.CharField(default=jarvis.accounts.generators.generate_client_key, help_text='Client Key', max_length=255)),
                ('secret', models.CharField(default=jarvis.accounts.generators.generate_client_secret, help_text='Client Secret', max_length=255)),
                ('organization', models.CharField(help_text='Organization Name', max_length=50, unique=True)),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='deleted_date',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='label',
            field=models.CharField(help_text='User Profile Label', max_length=50),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='limit',
            field=models.PositiveIntegerField(default=20, help_text='Access Limit'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profiles', to='accounts.Client'),
        ),
    ]
