# Generated by Django 3.0 on 2021-05-12 08:09

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_auto_20210512_1041'),
    ]

    operations = [
        migrations.AddField(
            model_name='inside',
            name='door_id_exit',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='account',
            name='data_joined',
            field=models.DateTimeField(default=datetime.datetime.now, verbose_name='data_joined'),
        ),
        migrations.AlterField(
            model_name='inside',
            name='entry_time',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
        migrations.AlterField(
            model_name='qr',
            name='date_created',
            field=models.DateTimeField(default=datetime.datetime.now),
        ),
    ]
