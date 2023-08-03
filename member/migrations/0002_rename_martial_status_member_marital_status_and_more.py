# Generated by Django 4.2.2 on 2023-06-12 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('member', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='member',
            old_name='martial_status',
            new_name='marital_status',
        ),
        migrations.AlterField(
            model_name='member',
            name='currently_living_at',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='member',
            name='education',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='member',
            name='first_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='member',
            name='last_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='member',
            name='mobile_number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='member',
            name='relation_with_main_member',
            field=models.CharField(max_length=100),
        ),
    ]
