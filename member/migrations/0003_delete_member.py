# Generated by Django 4.2.2 on 2023-06-13 10:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0002_rename_martial_status_member_marital_status_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Member',
        ),
    ]