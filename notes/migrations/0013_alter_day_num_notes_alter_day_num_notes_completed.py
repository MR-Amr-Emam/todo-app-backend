# Generated by Django 5.1 on 2024-08-31 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0012_alter_day_state_alter_month_state'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day',
            name='num_notes',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='day',
            name='num_notes_completed',
            field=models.IntegerField(default=0),
        ),
    ]
