# Generated by Django 4.2.4 on 2024-07-19 12:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0003_interview_interview_code'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='interview',
            options={'ordering': ['-created_at']},
        ),
    ]