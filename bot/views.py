
__author__ = '@Alexey_Horbunov'
from requests.models import parse_header_links
from bot.utils import numbers_emojify
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from collections import defaultdict
import telebot
import datetime
from .models import User
from .config import TOKEN, PROVIDER_TOKEN
from telebot.types import LabeledPrice, Message, ShippingOption
from fuzzywuzzy import fuzz
import random

bot = telebot.TeleBot(TOKEN)


class UpdateBot(APIView):

    def post(self, request):
        json_string = request.body.decode('UTF-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])

        return Response({'code': 200})


keyboard_1 = telebot.types.ReplyKeyboardMarkup(True, False, row_width=1)
keyboard_1.row('💠🔥 Начать играть 🔥💠')
keyboard_1.row('🤑💲 Мой счет 💲🤑')
keyboard_1.row('🎳 Мои очки 🎳')
keyboard_1.row('🕰💣 Следующий розыгрыш 💣🕰')

minigame_keyboard = telebot.types.ReplyKeyboardMarkup(
    True, False, row_width=1)
minigame_keyboard.row('Проверить удачу')


DEFAULT, MINIGAMESTART, MINIGAMEFINAL, GOTOSET, FINAL = range(5)

USER_STATE = defaultdict(lambda: DEFAULT)


def get_state(message):
    return USER_STATE[message.chat.id]


def update_state(message, state):
    USER_STATE[message.chat.id] = state


@bot.message_handler(commands=['start'])
def message_start(message):
    text = '🤖' + message.from_user.first_name + ', Вас приветствует сервис 💎<b>Crystal Cash💎!</b> \n' +\
        '💵Я бот, который поможет Вам приумножить Ваши средства, а также проверить удачу 🔥.\n\n' +\
        '💠Суть проста: вы вкладываете средства в общий банк 💶, как и другие пользователи нашего сервиса. Раз в день происходить розыгрыш банка и именно Вы можете забрать весь куш 💰\n\n' +\
        '🍑Только представьте, сегодня вы вложите пару долларов и уже завтра сможете забрать в десятки раз больше!💣\n\n' +\
        '✅Дерзайте!✅\n\n' +\
        'ℹ️<i>Подробные правила вы можете узнать нажав команду /help</i>ℹ️\n\n' +\
        '⚜️С уважением команда 💎Crystal Cash💎⚜️'

    bot.send_message(message.chat.id, text,
                     reply_markup=keyboard_1, parse_mode='HTML')
    user = User()
    user.user_id = message.chat.id
    user.name = message.from_user.first_name
    user.state_now = 'DEFAULT'
    user.save()


@bot.message_handler(commands=['help'])
def message_help(message):
    # markup_author.add(item_author)
    bot.send_message(
        message.chat.id, 'Тут должен быть текст помощи', reply_markup=keyboard_1)


@bot.message_handler(content_types=['text'], func=lambda message: get_state(message) == DEFAULT)
def answer_for_text(message):
    if 'начать играть' in message.text.lower():
        send_money_keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        send_money_button = telebot.types.InlineKeyboardButton(
            '🔮💵💎Ворваться в игру💎💵🔮', callback_data='send_money')
        play_minigame_button = telebot.types.InlineKeyboardButton(
            'Играть в мини-игру', callback_data='play_minigame')
        send_money_keyboard.add(send_money_button)
        send_money_keyboard.add(play_minigame_button)
        bot.send_message(message.chat.id, '❇️Уже сейчас 🔷ИМЕННО ВЫ🔷  Вы можете начать играть и вложить частичку в банк 💰, который сможете через некоторое вресмя забрать и стать богаче!) 💲\n\n' +
                         '<i>Примечание:\n' +
                         'Данная игра предназначена только для лиц старше 18 лет. Администрация сервиса не несет ответственности за Ваши средства и не может гарантировать 100% выигрыш средств. Все операции Вы делаете на свой страх и риск</i>',
                         reply_markup=send_money_keyboard, parse_mode='HTML')

    if 'мой счет' in message.text.lower():
        user = User.objects.get(user_id=message.chat.id)
        user_money = str(user.today_cash)
        bot.send_message(
            message.chat.id, f'💵Вы вложили в следующую игру 💎{user_money}💎 грн 💵', reply_markup=keyboard_1)

    if 'мои очки' in message.text.lower():
        user = User.objects.get(user_id=message.chat.id)
        user_scores = str(user.minigame_points)
        bot.send_message(
            message.chat.id, f'В настоящий момент у Вас {user_scores} очков')

    if 'следующий розыгрыш' in message.text.lower():
        bot.send_message(
            message.chat.id, '🕓Следующий розыгрыш будет проведен в 18:00 по киевскому времени🕓', reply_markup=keyboard_1)

# @bot.message_handler(func=lambda message: get_state(message) == GOTOSET)


def message_to_send_money(message):
    bot.send_message(
        message.chat.id, '💸 Отправьте нужную сумму 💸 (Целое число в гривнах)')
    update_state(message, FINAL)


@bot.message_handler(func=lambda message: get_state(message) == FINAL)
def confirm_sending_money(message):
    amount = int(message.text + '00')
    prices = [LabeledPrice(label='Оплата Crystal Cash', amount=amount)]
    bot.send_invoice(message.chat.id, title='Оплата Crystal Cash',
                     description='✨🌟Оплата за участие в розыгрыше 💵средств💵🌟✨',
                     provider_token=PROVIDER_TOKEN,
                     currency='uah',
                     is_flexible=False,  # True If you need to set up Shipping Fee
                     prices=prices,
                     start_parameter='time-machine-example',
                     invoice_payload='Crystal Cash Payment')
    # user = User.objects.get(user_id=message.chat.id)
    # user.today_cash = float(message.text)
    # user.save()
    # bot.send_message(message.chat.id, 'Средства получены')
    update_state(message, DEFAULT)


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    print(pre_checkout_query)
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Произошла ошибка. Попробуйте позже или обратитесь в поддержку")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    paym_amount = message.successful_payment.total_amount / 100
    user = User.objects.get(user_id=message.chat.id)
    user.today_cash = paym_amount
    user.save()
    bot.send_message(message.chat.id,
                     '💰Отлично, Вы участвуете в розыгрыше!💰 Розыгрыш пройдет в 18:00 по 🕧Киевскому времени 🕧. \n\n🔮Мы обязательно Вас уведомим!🔮',
                     parse_mode='Markdown')

#'Спасибо! Платеж был успешно проведен'


def start_minigame(message):
    user = User.objects.get(user_id=message.chat.id)
    if user.minigame_counter_date != datetime.date.today():
            user.minigame_counter_date = datetime.date.today()
            user.minigame_counter = 0
            user.save()

    if user.minigame_counter < 3:
        number = str(random.randint(1000000, 99999999))
        number_to_user = numbers_emojify(number)
        user.minigame_counter = user.minigame_counter + 1
        user.minigame_number = int(number)
        user.save()
        bot.send_message(
            message.chat.id, f'Ваше число\n\n - {number_to_user}', reply_markup=minigame_keyboard)
        update_state(message, MINIGAMEFINAL)
    else:
        bot.send_message(
            message.chat.id, 'Вы уже играли сегодня', reply_markup=keyboard_1)
        update_state(message, DEFAULT)


@bot.message_handler(content_types=['text'], func=lambda message: get_state(message) == MINIGAMEFINAL)
def minigame_final(message):
    if 'проверить удачу' in message.text.lower():
        user = User.objects.get(user_id=message.chat.id)
        user_minigame_number = str(user.minigame_number)
        user_minigame_number_to_user = numbers_emojify(user_minigame_number)
        luck_number = str(random.randint(1000000, 99999999))
        luck_number_to_user = numbers_emojify(luck_number)
        coincidence = fuzz.ratio(user_minigame_number, luck_number)
        user.minigame_points = user.minigame_points + coincidence
        user.save()
        bot.send_message(
            message.chat.id, f'Вам было дано число {user_minigame_number_to_user}, выпало число {luck_number_to_user}, вы получили {str(coincidence)} очков', reply_markup=keyboard_1)
        update_state(message, DEFAULT)
    else:
        bot.send_message(
            message.chat.id, 'Нажмите на кнопку "Проверить удачу"', reply_markup=minigame_keyboard)


@bot.callback_query_handler(func=lambda call: True)
def inline_buttons(call):
    if call.message:
        if call.data == 'send_money':
            message_to_send_money(call.message)
        if call.data == 'play_minigame':
            start_minigame(call.message)
