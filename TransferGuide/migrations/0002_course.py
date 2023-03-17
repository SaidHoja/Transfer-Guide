# Generated by Django 4.1.5 on 2023-03-17 19:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("TransferGuide", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Course",
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
                ("course_name", models.CharField(max_length=100)),
                ("course_number", models.CharField(max_length=5)),
                ("course_url", models.CharField(max_length=200)),
                ("course_description", models.CharField(max_length=500)),
                ("course_institution", models.CharField(max_length=100)),
            ],
        ),
    ]