# Generated by Django 3.2.25 on 2024-11-12 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forum', '0008_message_is_read'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='full_name',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='location',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
