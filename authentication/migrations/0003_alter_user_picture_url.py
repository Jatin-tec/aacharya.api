# Generated by Django 4.2.4 on 2024-07-16 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_user_email_verified_user_picture_user_picture_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='picture_url',
            field=models.URLField(blank=True, max_length=1000, null=True),
        ),
    ]