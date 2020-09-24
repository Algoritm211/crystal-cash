
__author__ = '@Alexey_Horbunov'
from ast import parse
from django.db.models import Sum
from django.db.utils import IntegrityError
from requests.models import parse_header_links
from bot.utils import numbers_emojify
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from collections import defaultdict
import telebot
import re
import os
import datetime
from .models import User
# from .config import TOKEN, PROVIDER_TOKEN
from telebot.types import LabeledPrice, Message, ShippingOption
from fuzzywuzzy import fuzz
import random

TOKEN = os.getenv('TOKEN')
PROVIDER_TOKEN = os.getenv('PROVIDER_TOKEN')

bot = telebot.TeleBot(TOKEN)


class UpdateBot(APIView):

    def post(self, request):
        json_string = request.body.decode('UTF-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])

        return Response({'code': 200})


keyboard_1 = telebot.types.ReplyKeyboardMarkup(True, False, row_width=1)
keyboard_1.row('💠🔥 Начать играть 🔥💠')
keyboard_1.row('🤑💲 Мой счет 💲🤑', '🏦 Общий банк за сегодня 🏦')
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
    try:
        user = User()
        user.user_id = message.chat.id
        user.name = message.from_user.first_name
        user.state_now = 'DEFAULT'
        user.save()
    except IntegrityError:
        pass


@bot.message_handler(commands=['help'])
def message_help(message):
    # markup_author.add(item_author)
    help_text = '💎<b> Наш сервис предлагает Вам 2 варианта игры </b>💎 \n\n' + \
        '🎯Первая игра является ежедневным розыгрышем 🏦Банка накопленного участниками в зависимости от их количества.  Размер 🏦 Банка будет увеличиваться в течении дня до момента его розыгрыша в 🕰 18:00 🕰 ( Киев )\n\n' + \
        'Вторая игра является моментальным лотереей в которой в зависимости от выбранных вами чисел будет производиться розыгрыш средств 💰 \n' + \
        '🎯Тут Вы можете выиграть очки 🔮, которые позже можно будет использовать в качестве 💵 оплаты 💰 части участия в розыгрыше. Вам дается сетка из 🔢 чисел и Вы должны собрать из четырех частей одно большое число . Насколько процентов оно будет совпадать с загаданным нами - столько очков Вы и получите 🎊(от 0 до 100).  🕰 Сыграть в игру можно 3 раза в сутки 🕰\n\n' + \
        '<i> 🍀 Наша команда желает Вам удачи 🍀 </i>'
    bot.send_message(
        message.chat.id, help_text, reply_markup=keyboard_1, parse_mode='HTML')


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
                         'Данная игра предназначена только для лиц старше 18 лет.</i>',
                         reply_markup=send_money_keyboard, parse_mode='HTML')

    if 'банк за сегодня' in message.text.lower():
        sum = User.objects.aggregate(Sum('today_cash'))['today_cash__sum']
        sum_for_user = sum - sum * 0.1
        bot.send_message(message.chat.id,
                         f'🏦 Банк сегодня уже {sum_for_user} грн!🏦 \n Нажимайте "Начать играть", чтобы вложить средства и принять участие в 💎розыгрыше💎',
                         parse_mode='HTML',
                         reply_markup=keyboard_1
                         )

    if 'мой счет' in message.text.lower():
        user = User.objects.get(user_id=message.chat.id)
        user_money = str(user.today_cash)
        bot.send_message(
            message.chat.id, f'💵Вы вложили в следующую игру 💎{user_money}💎 грн 💵', reply_markup=keyboard_1)

    if 'мои очки' in message.text.lower():
        user = User.objects.get(user_id=message.chat.id)
        user_scores = str(user.minigame_points)
        bot.send_message(
            message.chat.id, f'🔢 В настоящий момент у Вас {user_scores} очков 🔢')

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


def list_splitter(lst, size):
    return [lst[i: i+size] for i in range(0, len(lst), size)]


def run_minigame(message):
    user = User.objects.get(user_id=message.chat.id)
    if user.minigame_counter_date != datetime.date.today():
        user.minigame_counter_date = datetime.date.today()
        user.minigame_counter = 0
        user.save()
    if user.minigame_counter < 100000:
        list_of_numbers = [str(i) for i in random.sample(range(10, 99), 16)]
        user.minigame_random_list = '-'.join(list_of_numbers)
        user.minigame_counter = user.minigame_counter + 1
        user.save()
        # print(user.minigame_random_list)
        number_keyboard = telebot.types.InlineKeyboardMarkup(row_width=4)
        for item in list_splitter(list_of_numbers, 4):
            temp = []
            for elem in item:
                temp.append(telebot.types.InlineKeyboardButton(
                    elem, callback_data=f'game_number-{str(elem)}'))
            number_keyboard.add(*temp)

        exit_button = telebot.types.InlineKeyboardButton(
            '⬅ Выйти', callback_data='exit_minigame')
        number_keyboard.add(exit_button)
        text_start = '💎 <b>Привествуем Вас в мини-игре</b> 💎 \n\n' + \
            '🎯Тут Вы можете выиграть очки 🔮, которые позже можно будет использовать в качестве 💵 оплаты 💰 части участия в розыгрыше. Вам дается сетка из 🔢 чисел и Вы должны собрать из четырех частей одно большое число . Насколько процентов оно будет совпадать с загаданным нами - столько очков Вы и получите 🎊(от 0 до 100).\n\n' + \
            '🕰Сыграть в игру можно 3 раза в сутки 🕰\n\n' + \
            '<i>Удачи!</i> 🍀'
        bot.send_message(message.chat.id, text_start,
                         reply_markup=number_keyboard, parse_mode='HTML')
    else:
        bot.send_message(
            message.chat.id, '❌ Вы уже играли сегодня ❌', reply_markup=keyboard_1)
        update_state(message, DEFAULT)


def user_in_game_process(message):
    user = User.objects.get(user_id=message.chat.id)
    list_of_user_numbers = re.findall(r'\d\d', user.minigame_number)
    # print(list_of_user_numbers)
    user_number = user.minigame_random_list.split('-')
    # print(user_number)
    number_keyboard = telebot.types.InlineKeyboardMarkup(row_width=4)
    for item in list_splitter(user_number, 4):
        temp = []
        for elem in item:
            if elem in list_of_user_numbers:
                temp.append(telebot.types.InlineKeyboardButton(
                    str(elem) + '✅', callback_data=f'game_number-{str(elem)}'))
            else:
                temp.append(telebot.types.InlineKeyboardButton(
                    str(elem) + '', callback_data=f'game_number-{str(elem)}'))
        number_keyboard.add(*temp)
    exit_button = telebot.types.InlineKeyboardButton(
        '⬅ Выйти', callback_data='exit_minigame')
    number_keyboard.add(exit_button)

    text_start = '🍀 #️⃣ <i>Выберите еще одно число</i> #️⃣  🍀'
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text=text_start, reply_markup=number_keyboard, parse_mode='HTML')


def minigame_final(message):
    user = User.objects.get(user_id=message.chat.id)
    user_minigame_number = str(user.minigame_number)
    user_minigame_number_to_user = numbers_emojify(user_minigame_number)
    luck_number = str(random.randint(1000000, 99999999))
    luck_number_to_user = numbers_emojify(luck_number)
    coincidence = fuzz.ratio(user_minigame_number, luck_number)
    user.minigame_points = user.minigame_points + coincidence
    user.minigame_random_list = []
    user.minigame_number = ''
    user.save()
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text=f'Вы собрали число {user_minigame_number_to_user}, выпало число {luck_number_to_user}, вы получили {str(coincidence)} очков')
    update_state(message, DEFAULT)


@bot.callback_query_handler(func=lambda call: True)
def inline_buttons(call):
    if call.message:
        if call.data == 'send_money':
            message_to_send_money(call.message)
        if call.data == 'play_minigame':
            run_minigame(call.message)
        if call.data == 'exit_minigame':
            user = User.objects.get(user_id=call.message.chat.id)
            user.minigame_random_list = []
            user.minigame_number = ''
            user.save()
            bot.delete_message(chat_id=call.message.chat.id,
                               message_id=call.message.message_id)
            bot.send_message(call.message.chat.id,
                             text='🚪 Вы вышли из игры', reply_markup=keyboard_1)
        if 'game_number' in call.data:
            user = User.objects.get(user_id=call.message.chat.id)
            user_message_number = call.data.split('-')[1]
            list_of_user_numbers = re.findall(r'\d\d', user.minigame_number)
            if user_message_number in list_of_user_numbers:
                bot.answer_callback_query(
                    call.id, show_alert=False, text='❌Вы уже взяли это число')
                return
            user.minigame_number = str(
                user.minigame_number) + user_message_number
            user.save()
            bot.answer_callback_query(call.id)
            if len(user.minigame_number) < 8:
                user_in_game_process(call.message)
            else:
                minigame_final(call.message)
            # start_minigame(call.message)


# def start_minigame(message):
#     user = User.objects.get(user_id=message.chat.id)
    # if user.minigame_counter_date != datetime.date.today():
    #         user.minigame_counter_date = datetime.date.today()
    #         user.minigame_counter = 0
    #         user.save()

#     if user.minigame_counter < 3:
#         number = str(random.randint(1000000, 99999999))
#         number_to_user = numbers_emojify(number)
#         user.minigame_counter = user.minigame_counter + 1
#         user.minigame_number = int(number)
#         user.save()
#         bot.send_message(
#             message.chat.id, f'Ваше число\n\n - {number_to_user}', reply_markup=minigame_keyboard)
#         update_state(message, MINIGAMEFINAL)
#     else:
        # bot.send_message(
        #     message.chat.id, 'Вы уже играли сегодня', reply_markup=keyboard_1)
        # update_state(message, DEFAULT)


# @bot.message_handler(content_types=['text'], func=lambda message: get_state(message) == MINIGAMEFINAL)
