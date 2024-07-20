# Generated by Django 4.2.4 on 2024-07-17 22:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Interview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('resume', models.FileField(upload_to='resumes/')),
                ('parsed_resume', models.JSONField(blank=True, null=True)),
                ('job_title', models.CharField(blank=True, max_length=255, null=True)),
                ('job_description', models.TextField(blank=True, null=True)),
                ('company_name', models.CharField(blank=True, max_length=255, null=True)),
                ('interview_type', models.CharField(blank=True, choices=[('HR', 'HR'), ('Technical', 'Technical'), ('Managerial', 'Managerial')], max_length=255, null=True)),
                ('interview_status', models.CharField(blank=True, choices=[('Scheduled', 'Scheduled'), ('Rescheduled', 'Rescheduled'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], max_length=255, null=True)),
                ('interview_date', models.DateTimeField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True, null=True)),
                ('feedback_rating', models.IntegerField(blank=True, null=True)),
                ('stage', models.CharField(choices=[(1, 'Step 1'), (2, 'Step 2'), (3, 'Step 3'), (4, 'Step 4')], default='Step 1', max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
