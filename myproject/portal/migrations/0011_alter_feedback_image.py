# Generated by Django 5.1.6 on 2025-04-20 16:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('portal', '0010_alter_feedback_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='feedback_images/'),
        ),
    ]
