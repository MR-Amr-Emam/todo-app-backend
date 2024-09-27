# Generated by Django 5.1 on 2024-09-06 14:55

from django.db import migrations, models

def func(apps, shema):
    Month = apps.get_model("notes", "Month")
    for month in Month.objects.all():
        num_notes = 0
        for day in month.day_set.all():
            num_notes += day.num_notes
        month.num_notes = num_notes
        month.save()

class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0017_auto_20240906_1539'),
    ]

    operations = [
        migrations.AddField(
            model_name='month',
            name='num_notes',
            field=models.IntegerField(default=0),
        ),
        migrations.RunPython(func),
    ]
