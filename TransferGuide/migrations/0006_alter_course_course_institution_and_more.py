# Generated by Django 4.1.5 on 2023-03-17 20:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("TransferGuide", "0005_remove_course_course_description_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="course",
            name="course_institution",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name="course",
            name="course_name",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
