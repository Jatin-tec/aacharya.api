# Generated by Django 4.2.4 on 2024-07-17 22:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interview', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='interview',
            name='parsed_resume',
            field=models.TextField(blank=True, null=True),
        ),
    ]
