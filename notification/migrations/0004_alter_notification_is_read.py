# Generated by Django 4.2.2 on 2023-06-16 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("notification", "0003_rename_notification_content_notification_content"),
    ]

    operations = [
        migrations.AlterField(
            model_name="notification",
            name="is_read",
            field=models.BooleanField(default=False),
        ),
    ]
