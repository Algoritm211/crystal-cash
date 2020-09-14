from django.db import models
import datetime
from django.utils import timezone

# Create your models here.
class User(models.Model):
    user_id = models.CharField(max_length=200, unique=True, verbose_name='ID пользователя')
    name = models.CharField(max_length=200, blank=True, verbose_name='Имя пользователя')
    today_cash = models.FloatField(default=0, blank=True, verbose_name='Вложения сегодня')
    minigame_points = models.IntegerField(default=0, verbose_name='Очки за мини-игры')
    minigame_number = models.IntegerField(default=0, verbose_name='Число пользователя')
    minigame_counter = models.IntegerField(default=0, verbose_name='Кол-во проведенных игр')
    minigame_counter_date = models.DateField(default=timezone.now, verbose_name='Дата проведенных игр')
    luck_point = models.IntegerField(default=0, blank=True, verbose_name='Кол-во мест выигрыша')
    state_now = models.CharField(max_length=200, blank=True, verbose_name='Текущее состояние пользователя')

    def __str__(self):
        return self.user_id

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'