# Generated by Django 4.2.16 on 2024-09-19 18:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0021_month_bio'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goals',
            name='theme',
        ),
        migrations.RemoveField(
            model_name='notes',
            name='category',
        ),
        migrations.RemoveField(
            model_name='notes',
            name='theme',
        ),
    ]
