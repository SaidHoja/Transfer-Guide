# Generated by Django 4.1.5 on 2023-03-23 03:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("TransferGuide", "0004_course_course_delivery"),
    ]

    operations = [
        migrations.AddField(
            model_name="course",
            name="syllabus_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
