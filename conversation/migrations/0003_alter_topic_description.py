# Generated by Django 4.2.4 on 2024-07-17 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversation', '0002_topic_alter_video_options_video_topic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='topic',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]