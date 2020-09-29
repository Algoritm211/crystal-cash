from django.db import models
import datetime
from django.db.models.fields.related import ForeignKey
from django.utils import timezone

# Create your models here.
class User(models.Model):
    user_id = models.CharField(max_length=200, unique=True, verbose_name='ID пользователя')
    name = models.CharField(max_length=200, blank=True, verbose_name='Имя пользователя')
    today_cash = models.FloatField(default=0, blank=True, verbose_name='Вложения сегодня')
    minigame_points = models.IntegerField(default=0, verbose_name='Очки за мини-игры')
    minigame_random_list = models.CharField(max_length=200, blank=True, verbose_name='Рандомное данное число')
    minigame_number = models.CharField(max_length=200, blank=True, verbose_name='Число пользователя')
    minigame_counter = models.IntegerField(default=0, verbose_name='Кол-во проведенных игр')
    minigame_counter_date = models.DateField(default=timezone.now, verbose_name='Дата проведенных игр')
    state_now = models.CharField(max_length=200, blank=True, verbose_name='Текущее состояние пользователя')
    is_paid_for_minigame = models.BooleanField(default=False)
    

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

class Ticket(models.Model):
    number = models.IntegerField(unique=True, blank=False, verbose_name='Номер билета')
    user = models.ForeignKey('User', null=True, blank=True, on_delete=models.PROTECT, verbose_name='Пользователь', related_name='ticket')

    def __str__(self):
        return str(self.number)
