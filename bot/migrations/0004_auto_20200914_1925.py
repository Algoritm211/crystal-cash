# Generated by Django 3.0.3 on 2020-09-14 16:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_auto_20200914_1925'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='minigame_counter_date',
            field=models.DateField(default=datetime.date(2020, 9, 14), verbose_name='Дата проведенных игр'),
        ),
    ]
