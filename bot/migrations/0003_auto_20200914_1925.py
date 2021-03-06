# Generated by Django 3.0.3 on 2020-09-14 16:25

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0002_user_minigame_points'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='minigame_counter',
            field=models.IntegerField(default=0, verbose_name='Кол-во проведенных игр'),
        ),
        migrations.AddField(
            model_name='user',
            name='minigame_counter_date',
            field=models.DateTimeField(default=datetime.date(2020, 9, 14), verbose_name='Дата проведенных игр'),
        ),
        migrations.AddField(
            model_name='user',
            name='minigame_number',
            field=models.IntegerField(default=0, verbose_name='Число пользователя'),
        ),
    ]
