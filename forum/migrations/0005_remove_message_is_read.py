# Generated by Django 3.2.25 on 2024-11-06 15:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0004_auto_20241106_1633'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='is_read',
        ),
    ]