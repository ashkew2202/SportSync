# Generated by Django 5.1.4 on 2025-04-11 05:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("portal", "0006_alter_singlescoring_scores"),
    ]

    operations = [
        migrations.CreateModel(
            name="SingleScoringForAthletics",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="portal.event"
                    ),
                ),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="portal.match"
                    ),
                ),
                (
                    "scores",
                    models.ManyToManyField(
                        through="portal.AthleticsScore", to="portal.participant"
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="athleticsscore",
            name="scoring",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="portal.singlescoringforathletics",
            ),
        ),
        migrations.CreateModel(
            name="SingleScoringForSwimming",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="portal.event"
                    ),
                ),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="portal.match"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SwimmingScore",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "verdict",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("Qualified", "Qualified"),
                            ("Disqualified", "Disqualified"),
                            ("Did Not Finish", "Did Not Finish"),
                        ],
                        default="Did Not Finish",
                        max_length=20,
                        null=True,
                    ),
                ),
                ("time", models.DurationField(blank=True, null=True)),
                (
                    "distance",
                    models.DecimalField(
                        blank=True, decimal_places=2, max_digits=10, null=True
                    ),
                ),
                ("position", models.IntegerField(blank=True, null=True)),
                (
                    "participant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="portal.participant",
                    ),
                ),
                (
                    "scoring",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="portal.singlescoringforswimming",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="singlescoringforswimming",
            name="scores",
            field=models.ManyToManyField(
                through="portal.SwimmingScore", to="portal.participant"
            ),
        ),
        migrations.DeleteModel(
            name="SingleScoring",
        ),
    ]
