# Generated by Django 4.2.2 on 2023-07-25 10:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("events", "0007_remove_events_is_bookmarked_remove_events_is_liked_and_more"),
        ("news", "0005_news_is_reported"),
        ("notification", "0005_rename_notification_sendnotification"),
    ]

    operations = [
        migrations.AddField(
            model_name="sendnotification",
            name="event",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="events.events",
            ),
        ),
        migrations.AddField(
            model_name="sendnotification",
            name="news",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="news.news",
            ),
        ),
    ]
