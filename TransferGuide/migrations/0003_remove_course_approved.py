# Generated by Django 4.1.5 on 2023-03-23 03:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("TransferGuide", "0002_course"),
    ]

    operations = [
        migrations.RemoveField(model_name="course", name="approved",),
    ]