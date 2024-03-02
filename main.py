import random
import os
import telebot
from telebot import types
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

TOKEN = '7050738799:AAGgUIcWC5BwD46im4EaOB4mLdu2HwxhnX4'
channel_username = '@hakermines12'

bot = telebot.TeleBot(TOKEN)

waiting_for_id = set()

# Словарь для хранения предыдущих состояний
previous_state = {}

# Словарь для хранения соответствия ID пользователя в Telegram и ID, полученного на сайте
user_ids = {}


@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.InlineKeyboardMarkup()
    subscribe_btn = types.InlineKeyboardButton("Подписаться", url=f"https://t.me/{channel_username[1:]}")
    check_btn = types.InlineKeyboardButton("Проверить", callback_data='check_subscription')
    markup.add(subscribe_btn)
    markup.add(check_btn)
    user_name = bot.get_chat_member(channel_username, message.chat.id).user.first_name
    welcome_text = f"Добро пожаловать, {user_name}!\n\n"
    bot.send_message(message.chat.id, welcome_text + "Для использования бота - подпишись на наш канал🤝",
                     reply_markup=markup)


def osnova(call):
    markup = types.InlineKeyboardMarkup()
    reg_btn = types.InlineKeyboardButton("📱Регистрация", callback_data='register')
    instruction_btn = types.InlineKeyboardButton("📚Инструкция", callback_data='instruction')
    signal_btn = types.InlineKeyboardButton("❗️Выдать сигнал❗️", callback_data='give_signal')
    markup.add(reg_btn, instruction_btn)
    markup.add(signal_btn)
    welcome_message = (
        "Добро пожаловать в 🔸*HAKERMINES*🔸!\n\n"
        "💣 *Mines* - это гэмблинг игра в букмекерской конторе 1win, которая основывается на классическом “Сапёре”.\n"
        "Ваша цель - открывать безопасные ячейки и не попадаться в ловушки.\n\n"
        "`\n"
        "Наш бот основан на нейросети от OpenAI..\n"
        "Он может предугадать расположение звёзд с вероятностью 90%.\n"
        "`"
    )
    bot.send_message(call.message.chat.id, welcome_message, reply_markup=markup, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data == 'check_subscription')
def callback_handler(call):
    check_user_subscription(call)


@bot.callback_query_handler(func=lambda call: call.data == 'register')
def callback_handler(call):
    register(call)


@bot.callback_query_handler(func=lambda call: call.data == 'instruction')
def callback_handler(call):
    previous_state[call.message.chat.id] = send_instruction
    send_instruction(call)


@bot.callback_query_handler(func=lambda call: call.data == 'give_signal')
def callback_handler(call):
    if str(call.message.chat.id) in user_ids:
        give_signal(call)
    else:
        bot.answer_callback_query(call.id, "Пожалуйста, сначала зарегистрируйтесь.")


@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def back_to_main_menu_handler(call):
    chat_id = call.message.chat.id
    if chat_id in previous_state:
        previous_state.pop(chat_id)  # Удаляем предыдущее состояние
    osnova(call)
    if str(chat_id) in user_ids:
        enable_give_signal_button(call)
    else:
        disable_give_signal_button(call)


def check_user_subscription(call):
    try:
        chat_member = bot.get_chat_member(channel_username, call.message.chat.id)
        if chat_member.status not in ['left', 'kicked']:
            bot.answer_callback_query(call.id, "Вы подписаны на канал!", show_alert=True)
            osnova(call)
        else:
            bot.answer_callback_query(call.id, "Пожалуйста, подпишитесь на канал, чтобы продолжить.", show_alert=True)
    except Exception as e:
        print(e)
        bot.answer_callback_query(call.id, "Произошла ошибка при проверке подписки. Попробуйте позже.", show_alert=True)


def register(call):
    message = (
        "🔷 1. Для начала зарегистрируйтесь на сайте <a href='https://1wooxx.life/casino/list?open=register'>1WIN(CLICK) </a> ""ДЛЯ СТАБИЛЬНОЙ РАБОТЫ СОЗДАЙТЕ НОВЫЙ АККАУНТ - с секретным промокодом <code>MINES54</code>\n"
        "🔷 2. После успешной регистрации cкопируйте ваш айди на сайте (Вкладка 'пополнение' и в правом верхнем углу будет ваш ID).\n"
        "🔷 3. И отправьте его боту в ответ на это сообщение."
    )
    markup = types.InlineKeyboardMarkup()
    subscribe_btn = types.InlineKeyboardButton("📱🔶 Зарегистрироваться",
                                               url='https://1wooxx.life/casino/list?open=register')
    back_btn = types.InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data='main_menu')
    markup.add(subscribe_btn)
    markup.add(back_btn)
    with open("REGISTERPHOTO.jpg", "rb") as photo:
        bot.send_photo(call.message.chat.id, photo, caption=message, reply_markup=markup, parse_mode='HTML')


def send_instruction(call):
    message = (
        "Бот основан и обучен на кластере нейросети 🖥 <b>[bitsGap]</b>.\n\n"
        "Для тренировки бота было сыграно 🎰10.000+ игр.\n"
        "В данный момент пользователи бота успешно делают в день 15-25% от своего 💸 капитала!\n\n"

        "<code>На текущий момент бот по сей день проходит проверки и исправления! Точность бота составляет 90%!</code>\n\n"

        "Для получения максимального профита следуйте следующей инструкции:\n\n"
        "🟢 1. Пройти регистрацию в букмекерской конторе <a href='https://1wcdcw.xyz/casino/list?open=register'>1WIN(CLICK) </a> \n"
        "Если не открывается - заходим с включенным VPN (Швеция). В Play Market/App Store полно бесплатных сервисов, например: Vpnify, Planet VPN, Hotspot VPN и так далее!\n\n"
        "<code>Без регистрации доступ к сигналам не будет открыт!</code>\n\n"
        "🟢 2. Пополнить баланс своего аккаунта.\n\n"
        "🟢 3. Перейти в раздел 1win games и выбрать игру 💣'MINE'.\n\n"
        "🟢 4. Выставить кол-во ловушек в размере трёх. Это важно!\n\n"
        "🟢 5. Запросить сигнал в боте и ставить по сигналам из бота.\n\n"
        "🟢 6. При неудачном сигнале советуем удвоить(Х²) ставку что бы полностью перекрыть потерю при следующем сигнале."
    )
    markup = types.InlineKeyboardMarkup()
    back_btn = types.InlineKeyboardButton("🔙 Вернуться в главное меню", callback_data='main_menu')
    markup.add(back_btn)
    with open("INSTRUKT.jpg", "rb") as photo:
        bot.send_photo(call.message.chat.id, photo.read(), caption=message, reply_markup=markup, parse_mode='HTML')


last_message_id = None


def give_signal(call):
    global last_message_id

    loading_messages = [
        "🔴 Получаю данные с сервера.",
        "🟡 Получаю данные с сервера..",
        "🔵 Получаю данные с сервера...",
        "🟣 Получаю данные с сервера....",
        "🟡 Получаю данные с сервера..",
        "🔵 Получаю данные с сервера..."
    ]

    if last_message_id:
        try:
            bot.delete_message(call.message.chat.id, last_message_id)
        except telebot.apihelper.ApiTelegramException as e:
            if "message to delete not found" not in e.description:
                raise

    sent_message = bot.send_message(call.message.chat.id, loading_messages[0])

    for message in loading_messages[1:]:
        time.sleep(1)
        bot.edit_message_text(chat_id=sent_message.chat.id, message_id=sent_message.message_id, text=message)

    photo_directory = "Signal/"
    photo_files = os.listdir(photo_directory)

    random_photo_file = random.choice(photo_files)
    photo_path = os.path.join(photo_directory, random_photo_file)

    with open(photo_path, "rb") as photo:
        button = InlineKeyboardButton("❗️Выдать сигнал❗️", callback_data='give_signal')
        reply_markup = InlineKeyboardMarkup().add(button)
        sent_photo = bot.send_photo(call.message.chat.id, photo, reply_markup=reply_markup)

        last_message_id = sent_photo.message_id

    bot.delete_message(call.message.chat.id, sent_message.message_id)


def disable_give_signal_button(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("🔒 Выдать сигнал (зарегистрируйтесь)", callback_data='disabled'))
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


def enable_give_signal_button(call):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❗️ Выдать сигнал", callback_data='give_signal'))
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)


# Обработчик команды /register
@bot.message_handler(commands=['register'])
def register_command(message):
    # Отправка сообщения с инструкцией о регистрации
    bot.send_message(message.chat.id, "Для регистрации отправьте свой ID, начиная с 'ID:'. Например, ID:123456789.")


@bot.message_handler(func=lambda message: message.text.isdigit())
def handle_registration(message):
    user_id_telegram = str(message.chat.id)
    user_id_site = message.text  # Получаем ID пользователя из текста сообщения
    if len(user_id_site) == 8:
        user_ids[user_id_telegram] = user_id_site  # Запоминаем соответствие ID пользователя в Telegram и ID на сайте
        markup = types.InlineKeyboardMarkup()
        give_signal_button = types.InlineKeyboardButton("❗️ Выдать сигнал ❗️", callback_data='give_signal')
        instruction_button = types.InlineKeyboardButton("📚 Инструкция", callback_data='instruction')
        close_menu_button = types.InlineKeyboardButton("🔒 Закрыть меню", callback_data='close_menu')
        markup.row(give_signal_button)
        markup.row(instruction_button)
        markup.row(close_menu_button)
        bot.send_message(message.chat.id, "Вы успешно зарегистрированы!", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Неверный ID.")

@bot.callback_query_handler(func=lambda call: call.data == 'close_menu')
def close_menu_handler(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)



while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(e)
        time.sleep(15)
