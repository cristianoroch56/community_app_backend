# Generated by Django 4.2.2 on 2023-07-24 13:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authentication", "0004_user_current_thread_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="country_code",
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="country_flag",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]