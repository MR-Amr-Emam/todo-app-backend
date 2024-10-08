# Generated by Django 5.1 on 2024-09-02 03:17

from django.db import migrations, models

import random
def forward_func(apps, schema):
    Notes = apps.get_model("notes", "Notes")
    choices = ["SD", "SL", "LS"]
    for note in Notes.objects.all():
        rand = random.randint(1,3)
        note.category = choices[rand]
        rand = random.randint(1,4)
        note.theme = rand
        note.save()

class Migration(migrations.Migration):

    dependencies = [
        ('notes', '0014_auto_20240831_1505'),
    ]

    operations = [
        migrations.AddField(
            model_name='notes',
            name='category',
            field=models.CharField(choices=[('SD', 'self_development'), ('SL', 'social_life'), ('LS', 'life_style')], default='SD', max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='notes',
            name='theme',
            field=models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4)], default=1),
            preserve_default=False,
        ),
    ]
