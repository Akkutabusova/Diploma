# Generated by Django 3.0 on 2021-05-11 17:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_returnedvaluefromscript'),
    ]

    operations = [
        migrations.AddField(
            model_name='inside',
            name='exit_time',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='inside',
            name='spent_time',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
