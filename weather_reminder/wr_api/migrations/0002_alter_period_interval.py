# Generated by Django 4.2.2 on 2023-07-24 14:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wr_api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='period',
            name='interval',
            field=models.IntegerField(unique=True),
        ),
    ]
