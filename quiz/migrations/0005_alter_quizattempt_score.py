# Generated by Django 5.0.7 on 2024-08-07 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_quizattempt_questionresponse'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizattempt',
            name='score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
