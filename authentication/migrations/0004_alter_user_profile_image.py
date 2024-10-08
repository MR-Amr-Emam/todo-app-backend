# Generated by Django 5.1 on 2024-09-09 14:11

import authentication.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_user_profile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(default='default/profile-image.png', upload_to=authentication.models.profile_image_storage),
        ),
    ]
