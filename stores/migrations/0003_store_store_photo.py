# Generated by Django 5.0.5 on 2024-07-03 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='store_photo',
            field=models.JSONField(blank=True, null=True),
        ),
    ]