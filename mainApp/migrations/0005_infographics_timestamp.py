# Generated by Django 5.0 on 2023-12-19 02:49

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0004_infographics_logmultimedia_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='infographics',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]