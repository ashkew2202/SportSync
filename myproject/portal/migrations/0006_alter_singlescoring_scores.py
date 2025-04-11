# Generated by Django 5.1.4 on 2025-04-11 05:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0005_remove_athleticsscore_event_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="singlescoring",
            name="scores",
            field=models.ManyToManyField(
                related_name="single_scoring_scores",
                through="portal.AthleticsScore",
                to="portal.participant",
            ),
        ),
    ]
