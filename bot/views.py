
__author__ = '@Alexey_Horbunov'
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from collections import defaultdict
import telebot
import datetime
from .models import User
from .config import TOKEN

bot = telebot.TeleBot(TOKEN)



class UpdateBot(APIView):

    def post(self, request):
        json_string = request.body.decode('UTF-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])

        return Response({'code': 200})


keyboard_1 = telebot.types.ReplyKeyboardMarkup(True, False, row_width=1)
keyboard_1.row('Начать играть')
keyboard_1.row('Мой счет')
keyboard_1.row('Следующий розыгрыш')

DEFAULT, GOTOSET, FINAL = range(3)

USER_STATE = defaultdict(lambda: DEFAULT)


def get_state(message):
    return USER_STATE[message.chat.id]

def update_state(message, state):
    USER_STATE[message.chat.id] = state


@bot.message_handler(commands=['start'])
def message_start(message):
    bot.send_message(message.chat.id, '🤖Здравствуйте, ' + message.from_user.first_name + '!\n' \
                        '💵Я бот, который поможет Вам заработать \n\n' +
                     'Для просмотра инструкции пользователя нажмите /help.\n\n\n', reply_markup=keyboard_1)
    user = User()
    user.user_id = message.chat.id
    user.name = message.from_user.first_name
    user.state_now = 'DEFAULT'
    user.save()

@bot.message_handler(commands=['help'])
def message_help(message):
    # markup_author.add(item_author)
    bot.send_message(message.chat.id, 'Тут должен быть текст помощи' ,reply_markup=keyboard_1)


@bot.message_handler(content_types=['text'], func=lambda message: get_state(message) != FINAL)
def answer_for_text(message):
    if 'начать играть' in message.text.lower():
        send_money_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        send_money_button = telebot.types.InlineKeyboardButton('Выслать средства', callback_data='send_money')
        send_money_keyboard.add(send_money_button)
        bot.send_message(message.chat.id, 'Правила игры', reply_markup=send_money_keyboard)

    if 'мой счет' in message.text.lower():
        user = User.objects.get(user_id=message.chat.id)
        user_money = str(user.today_cash)
        bot.send_message(message.chat.id, f'Вы вложили в следующую игру {user_money} грн', reply_markup=keyboard_1)

    if 'следующий розыгрыш' in message.text.lower():
        bot.send_message(message.chat.id, 'Следующий розыгрыш будет проведен в 18:00 по киевскому времени', reply_markup=keyboard_1)

# @bot.message_handler(func=lambda message: get_state(message) == GOTOSET)
def message_to_send_money(message):
    bot.send_message(message.chat.id, 'Отправьте нужную сумму')
    update_state(message, FINAL)

@bot.message_handler(func=lambda message: get_state(message) == FINAL)
def confirm_sending_money(message):
    user = User.objects.get(user_id=message.chat.id)
    user.today_cash = float(message.text)
    user.save()
    bot.send_message(message.chat.id, 'Средства получены')
    update_state(message, DEFAULT)

@bot.callback_query_handler(func=lambda call: True)
def inline_buttons(call):
    if call.message:
        if call.data == 'send_money':
            message_to_send_money(call.message)