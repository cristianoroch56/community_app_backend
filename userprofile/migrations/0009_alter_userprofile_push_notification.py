# Generated by Django 4.2.2 on 2023-07-25 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userprofile", "0008_alter_userprofile_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userprofile",
            name="push_notification",
            field=models.BooleanField(default=True, null=True),
        ),
    ]