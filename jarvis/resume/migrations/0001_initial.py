# -*- coding: utf-8 -*-
# Generated by Django 1.9.3 on 2017-03-08 07:20


import autoslug.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BitBucket',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('user_name', models.CharField(help_text="User's BitBucket Username", max_length=50)),
                ('display_name', models.CharField(help_text="User's full name", max_length=50)),
                ('account_created_at', models.DateTimeField(help_text="Date of user's account creation")),
                ('total_no_public_repos', models.PositiveIntegerField()),
                ('following', models.PositiveIntegerField()),
                ('followers', models.PositiveIntegerField()),
                ('blog_url', models.URLField(blank=True, help_text="uses's website/blog url", null=True)),
                ('profile_url', models.URLField(help_text="User's BitBucket Url")),
                ('repositories_url', models.URLField(blank=True, help_text="Url to list all the user's repositories")),
                ('snippet_url', models.URLField(help_text="User's bit bucket snippet url")),
                ('location', models.CharField(blank=True, help_text="User's Location", max_length=100)),
                ('reputation_score', models.FloatField(default=0)),
                ('contribution_score', models.FloatField(default=0)),
                ('activity_score', models.FloatField(default=0)),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='Blog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('reputation_score', models.FloatField()),
                ('contribution_score', models.FloatField()),
                ('activity_score', models.FloatField()),
                ('url', models.URLField()),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='GitHub',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('user_id', models.IntegerField(help_text="User's Github id")),
                ('user_name', models.CharField(help_text="User's Github Username", max_length=50)),
                ('profile_name', models.CharField(blank=True, help_text="User's Full Name", max_length=50)),
                ('email', models.EmailField(help_text="User's Email", max_length=254, null=True)),
                ('profile_url', models.URLField(help_text="User's Github Url")),
                ('profile_image_url', models.URLField(help_text="User's profile image url")),
                ('gists_url', models.URLField(help_text="Github's API url for all user gists")),
                ('location', models.CharField(blank=True, help_text="User's Location", max_length=100, null=True)),
                ('blog_url', models.URLField(blank=True, help_text="User's Website/Blog Url", null=True)),
                ('company', models.CharField(help_text='Company the user is currently working in.', max_length=50)),
                ('followers', models.PositiveIntegerField()),
                ('following', models.PositiveIntegerField()),
                ('hireable', models.NullBooleanField()),
                ('public_repos', models.PositiveIntegerField(help_text='Number of Public repository')),
                ('total_private_repos', models.PositiveIntegerField(help_text='Total Number of Private repository', null=True)),
                ('owned_private_repos', models.PositiveIntegerField(help_text='Private repositories owned by User', null=True)),
                ('public_gists', models.PositiveIntegerField(help_text='Public gists owned by User', null=True)),
                ('private_gists', models.PositiveIntegerField(help_text='Private gists owned by User', null=True)),
                ('account_created_at', models.DateField(help_text="Date of User's Account Creation")),
                ('repo_updated_at', models.DateTimeField(help_text='Date when user updated a repository')),
                ('account_modified_at', models.DateTimeField(help_text='Date when user modified the account')),
                ('reputation_score', models.FloatField(default=0)),
                ('contribution_score', models.FloatField(default=0)),
                ('activity_score', models.FloatField(default=0)),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='GitHubRepo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('repo_id', models.IntegerField(unique=True)),
                ('repo_name', models.CharField(max_length=50)),
                ('repo_url', models.URLField(help_text="Repository's github url")),
                ('repo_owner', models.CharField(help_text='Username of the user who owns the repo', max_length=50)),
                ('is_forked', models.BooleanField(default=False)),
                ('repo_organization', models.CharField(blank=True, help_text='Name of organisation', max_length=50, null=True)),
                ('no_of_forks', models.IntegerField()),
                ('no_of_stars', models.IntegerField()),
                ('no_of_watchers', models.IntegerField()),
                ('open_issue_counts', models.IntegerField()),
                ('repo_created_at', models.DateTimeField(help_text='Date and time when the repo was created')),
                ('repo_updated_at', models.DateTimeField(help_text='Date and time when the repo was last updated.')),
                ('last_pushed_at', models.DateTimeField(help_text='Date and time when last push was made.')),
                ('repo_size', models.PositiveIntegerField(blank=True, help_text='Repo size in bytes')),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='MobileApp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('app_type', models.CharField(choices=[('android', 'Android'), ('ios', 'iOS')], max_length=20)),
                ('app_url', models.CharField(blank=True, help_text='Application Website', max_length=500)),
                ('reputation_score', models.FloatField(default=0)),
                ('contribution_score', models.FloatField(default=0)),
                ('activity_score', models.FloatField(default=0)),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('parse_status', models.PositiveIntegerField(choices=[(0, 'processing'), (1, 'processed')])),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('file_name', models.CharField(blank=True, max_length=50)),
                ('content_hash', models.TextField(db_index=True, default='', help_text='Hash generated from jarvis.resume and skills.')),
                ('content', models.TextField(help_text='Parsed text obtained from jarvis.resume.')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(blank=True, max_length=50)),
                ('email', models.CharField(blank=True, max_length=50)),
                ('phone_number', models.CharField(blank=True, max_length=50, null=True)),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='ResumeSkills',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('is_matched', models.BooleanField(default=False)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resume.Resume')),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('type', models.PositiveIntegerField(choices=[(0, 'coding'), (1, 'social'), (2, 'skill matching')], help_text='Type of Score')),
            ],
            options={
                'ordering': ('-type',),
            },
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('name', models.CharField(blank=True, max_length=250, null=True, unique=True)),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, editable=False, populate_from='name', unique=True)),
            ],
            options={
                'ordering': ('-name',),
            },
        ),
        migrations.CreateModel(
            name='StackOverflow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('user_id', models.PositiveIntegerField(help_text="User's StackOverflow id")),
                ('profile_name', models.CharField(blank=True, help_text="User's Display Name on StackOverflow", max_length=50)),
                ('location', models.CharField(blank=True, help_text="User's Location", max_length=100)),
                ('website_url', models.URLField(blank=True, help_text="User's Website/Blog Url", null=True)),
                ('profile_url', models.URLField(help_text="User's StackOverFlow Url")),
                ('profile_image_url', models.URLField(help_text="User's profile image Url.")),
                ('reputation', models.IntegerField()),
                ('gold_badges_count', models.PositiveIntegerField()),
                ('silver_badges_count', models.PositiveIntegerField()),
                ('bronze_badges_count', models.PositiveIntegerField()),
                ('account_creation_date', models.DateTimeField(help_text='Date when the Account was created')),
                ('last_access_date', models.DateTimeField(help_text='Date when the account was last accessed')),
                ('is_moderator', models.BooleanField(help_text='checks if the user is moderator')),
                ('total_no_questions', models.PositiveIntegerField()),
                ('total_no_answers', models.PositiveIntegerField()),
                ('reputation_change_month', models.IntegerField(blank=True, help_text='Reputation change this month', null=True)),
                ('reputation_change_quarter', models.IntegerField(blank=True, help_text='Reputation change this quarter', null=True)),
                ('reputation_change_year', models.IntegerField(blank=True, help_text='Reputation change this year', null=True)),
                ('reputation_score', models.FloatField(default=0)),
                ('contribution_score', models.FloatField(default=0)),
                ('activity_score', models.FloatField(default=0)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resume.Resume')),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('tag', models.CharField(help_text='Tag/Language Names', max_length=100)),
                ('slug', autoslug.fields.AutoSlugField(always_update=True, editable=False, populate_from='tag', unique=True)),
            ],
            options={
                'ordering': ('tag',),
            },
        ),
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('category', models.CharField(blank=True, choices=[('contribution', 'contribution'), ('coding', 'coding'), ('social', 'social'), ('blog', 'blog'), ('forums', 'forums'), ('other', 'other')], default='other', max_length=100, null=True)),
                ('url', models.URLField(blank=True, null=True)),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.CreateModel(
            name='Website',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('deleted_date', models.DateTimeField(null=True)),
                ('reputation_score', models.FloatField()),
                ('contribution_score', models.FloatField()),
                ('activity_score', models.FloatField()),
                ('url', models.URLField()),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resume.Resume')),
            ],
            options={
                'ordering': ('-created_date',),
            },
        ),
        migrations.AddField(
            model_name='stackoverflow',
            name='top_answer_tags',
            field=models.ManyToManyField(related_name='stackoverflowusers_answers', to='resume.Tag'),
        ),
        migrations.AddField(
            model_name='stackoverflow',
            name='top_question_tags',
            field=models.ManyToManyField(related_name='stackoverflowusers_questions', to='resume.Tag'),
        ),
        migrations.AddField(
            model_name='resumeskills',
            name='skill',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resume.Skill'),
        ),
        migrations.AddField(
            model_name='resume',
            name='scores',
            field=models.ManyToManyField(to='resume.Score'),
        ),
        migrations.AddField(
            model_name='resume',
            name='skills',
            field=models.ManyToManyField(through='resume.ResumeSkills', to='resume.Skill'),
        ),
        migrations.AddField(
            model_name='resume',
            name='urls',
            field=models.ManyToManyField(to='resume.Url'),
        ),
        migrations.AddField(
            model_name='resume',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='resumes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='mobileapp',
            name='resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resume.Resume'),
        ),
        migrations.AddField(
            model_name='githubrepo',
            name='repo_language',
            field=models.ManyToManyField(to='resume.Tag'),
        ),
        migrations.AddField(
            model_name='github',
            name='resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resume.Resume'),
        ),
        migrations.AddField(
            model_name='blog',
            name='resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resume.Resume'),
        ),
        migrations.AddField(
            model_name='bitbucket',
            name='resume',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='resume.Resume'),
        ),
        migrations.AlterUniqueTogether(
            name='resumeskills',
            unique_together=set([('resume', 'skill')]),
        ),
    ]
