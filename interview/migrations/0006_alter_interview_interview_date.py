# Generated by Django 4.2.4 on 2024-07-19 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0005_alter_interview_interview_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='interview_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
