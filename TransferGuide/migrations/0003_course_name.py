# Generated by Django 4.1.5 on 2023-03-17 19:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("TransferGuide", "0002_course"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
