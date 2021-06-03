# Generated by Django 3.0 on 2021-05-04 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20210504_2225'),
    ]

    operations = [
        migrations.CreateModel(
            name='Door',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('door_name', models.CharField(max_length=200, null=True)),
                ('qr_string', models.CharField(max_length=200, null=True)),
                ('status', models.BooleanField(default=False)),
            ],
        ),
    ]