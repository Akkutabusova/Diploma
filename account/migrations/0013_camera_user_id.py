# Generated by Django 3.0 on 2021-05-06 08:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_camera'),
    ]

    operations = [
        migrations.AddField(
            model_name='camera',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
    ]
