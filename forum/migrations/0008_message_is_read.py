# Generated by Django 3.2.25 on 2024-11-10 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0007_follow_like'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]