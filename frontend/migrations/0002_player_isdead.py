# Generated by Django 3.2.9 on 2021-12-01 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frontend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='isDead',
            field=models.BooleanField(default=False),
        ),
    ]