# Generated by Django 5.2.3 on 2025-07-16 20:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0002_moodentry_affirmation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moodentry',
            name='intensity',
            field=models.CharField(choices=[('1', 'Subtle'), ('2', 'Mild'), ('3', 'Moderate'), ('4', 'Strong'), ('5', 'Intense')], max_length=100),
        ),
    ]
