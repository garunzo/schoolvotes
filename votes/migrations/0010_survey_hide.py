# Generated by Django 2.0.7 on 2018-08-06 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('votes', '0009_remove_survey_hide'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='hide',
            field=models.BooleanField(default=False),
        ),
    ]
