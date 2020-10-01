import os
import sys

project = os.path.dirname(os.path.abspath('manage.py'))
sys.path.append(project)
os.environ['DJANGO_SETTINGS_MODULE'] = 'crystalcash.settings'

import django
django.setup()

import telebot
from bot.models import Ticket, User
# from bot.config import TOKEN

TOKEN = os.getenv('TOKEN')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')


bot = telebot.TeleBot(TOKEN)

users = User.objects.filter(today_cash__gt = -1)
tickets = Ticket.objects.all()

random_ticket = Ticket.objects.order_by('?').first()

# print(random_ticket.user.ticket.all())


text_to_user_all = f'Силы рандома выбрали пользователя с билетом {str(random_ticket.number)} и ником {random_ticket.user}. ' + \
    'Если это именно 💎 Вы 💎, то обратитесь к ADMIN и заберите свой 💵 куш 💵 \n\n' +\
    'Если это не Ваш 🎫 билет 🎫 - <b>не расстраивайтесь</b>. Выигрыш был <b>близко</b> к Вам.\n' +\
    '🍀 <i>В следующий раз обязательно повезет!</i> 🍀\n\n' + \
    'Банк и билеты были обнулены'


def send_message_to_all():
    for user in users:
        text_to_user = '🎫 Номера Ваших билетов:\n'
        for ticket in user.ticket.all():
            text_to_user += f'Билет №{ticket.number}\n'  
        text_to_user += '\n' + text_to_user_all
        bot.send_message(user.user_id, text_to_user, parse_mode='HTML')
        user.today_cash = 0
        user.save()


def clear_ticket_table():
    Ticket.objects.all().delete()


send_message_to_all()
try:
    clear_ticket_table()
except:
    pass
