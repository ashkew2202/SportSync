# Generated by Django 5.1.6 on 2025-04-08 16:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0004_match_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='status',
            field=models.CharField(choices=[('Scheduled', 'Scheduled'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Scheduled', max_length=20),
        ),
    ]
