import asyncio
import logging
import os
import random
import traceback

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7050738799:AAEUaTmFNYu3zKbesc8MapZI_w0zhM3SC6s'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Указываем путь к директории с изображениями
photo_directory = "Signal/"

is_registered = False
is_valid_registration_id = False


# Функция для проверки подписки пользователя
async def check_subscription(user_id):
    try:
        # Получаем информацию о пользователе в канале
        chat_member = await bot.get_chat_member(chat_id=-1001865221905, user_id=user_id)

        # Проверяем статус пользователя в канале
        if chat_member.status in ['administrator', 'member', 'creator']:
            return True  # Пользователь подписан на канал
        else:
            return False  # Пользователь не подписан на канал
    except Exception as e:
        print("Ошибка при проверке подписки:", e)
        return False  # Если возникла ошибка, считаем, что пользователь не подписан на канал


@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_name = message.from_user.first_name
    welcome_message = f"Добро пожаловать, {user_name}!\n\nДля использования бота - подпишись на наш канал 🤝"
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Подписаться", url="https://t.me/+A1m5z86gf5BkNmUy"))
    keyboard.add(InlineKeyboardButton("Проверить подписку", callback_data="check_subscription"))
    await message.answer(welcome_message, reply_markup=keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'check_subscription')
async def check_subscription_callback(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_subscription(user_id):
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton("📱 Регистрация", callback_data="registration"),
            InlineKeyboardButton("📚 Инструкция", callback_data="instruction")
        )
        keyboard.add(InlineKeyboardButton("💣 Получить сигнал", callback_data="signal"))
        menu_text = (
            "Добро пожаловать в 🔸HAKERMINES V3.0🔸!\n\n"
            "💣Mines - это гэмблинг игра в букмекерской конторе 1win, которая основывается на классическом “Сапёре”.\n"
            "Ваша цель - открывать безопасные ячейки и не попадаться в ловушки.\n\n"
            "`\n"
            "Наш бот основан на нейросети от OpenAI.\n"
            "Он может предугадать расположение звёзд с вероятностью 90%.\n"
            "`\n"
        )
        await bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.message_id,
            text=menu_text,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
    else:
        await callback_query.answer("Вы не подписаны на канал. Пожалуйста, подпишитесь, чтобы продолжить.")


@dp.message_handler(lambda message: len(message.text) == 8 and message.text.isdigit())
async def process_registration_id(message: types.Message):
    global is_valid_registration_id
    is_valid_registration_id = True
    registration_id = message.text
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Инструкция", callback_data="instruction"),
        InlineKeyboardButton("💣 Выдать сигнал 💣", callback_data="signal")
    )
    keyboard.add(InlineKeyboardButton("Закрыть меню", callback_data="close_menu"))  # Добавляем кнопку "Закрыть меню"
    await message.answer("Вы успешно зарегистрировались!", reply_markup=keyboard)


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'close_menu')
async def close_menu_callback(callback_query: types.CallbackQuery):
    await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)


@dp.message_handler(lambda message: len(message.text) != 8 or not message.text.isdigit())
async def invalid_registration_id(message: types.Message):
    await message.answer("Неверный ID")


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'registration')
async def registration_callback(callback_query: types.CallbackQuery):
    # Текст с картинкой и кнопками
    registration_text = (
        "🔷 <b>1. Для начала зарегистрируйтесь на сайте</b> <a "
        "href='https://1wwbnd.com/casino/list?open=register'>1WIN (CLICK)</a>\n"
        "<b>ДЛЯ СТАБИЛЬНОЙ РАБОТЫ СОЗДАЙТЕ НОВЫЙ АККАУНТ - с секретным промокодом</b> <code>MINES19</code>\n"
        "🔷 <b>2. После успешной регистрации cкопируйте ваш айди на сайте</b> (Вкладка 'пополнение' и в правом "
        "верхнем углу"
        "будет ваши цифры).\n"
        "🔷 <b>3. И отправьте его боту в ответ на это сообщение.</b>"
    )
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Регистрация", url='https://1wwbnd.com/casino/list?open=register'),
        InlineKeyboardButton("Вернуться в меню", callback_data="back_to_menu")
    )
    # Удаление старого сообщения
    await bot.delete_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
    )
    # Отправка нового сообщения с фото и кнопками
    await bot.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=open("REGISTERPHOTO.jpg", "rb"),
        caption=registration_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'back_to_menu')
async def back_to_menu_callback(callback_query: types.CallbackQuery):
    # Текст с меню
    menu_text = (
        "Добро пожаловать в 🔸HAKERMINES V3.0🔸!\n\n"
        "💣Mines - это гэмблинг игра в букмекерской конторе 1win, которая основывается на классическом “Сапёре”.\n"
        "Ваша цель - открывать безопасные ячейки и не попадаться в ловушки.\n\n"
        "`\n"
        "Наш бот основан на нейросети от OpenAI.\n"
        "Он может предугадать расположение звёзд с вероятностью 90%.\n"
        "`\n"
    )
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("📱 Регистрация", callback_data="registration"),
        InlineKeyboardButton("📚 Инструкция", callback_data="instruction")
    )
    keyboard.add(InlineKeyboardButton("💣 Выдать сигнал! 💣", callback_data="signal"))

    # Удаление старого сообщения
    await bot.delete_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
    )

    # Отправка нового сообщения с меню
    await bot.send_message(
        chat_id=callback_query.message.chat.id,
        text=menu_text,
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'instruction')
async def instruction_callback(callback_query: types.CallbackQuery):
    # Текст с инструкцией
    instruction_text = (
        "Бот основан и обучен на кластере нейросети 🖥 <b>[bitsGap]</b>.\n\n"
        "Для тренировки бота было сыграно 🎰10.000+ игр.\n"
        "В данный момент пользователи бота успешно делают в день 15-25% от своего 💸 капитала!\n\n"
        "<code>На текущий момент бот по сей день проходит проверки и исправления! Точность бота составляет "
        "90%!</code>\n\n"
        "Для получения максимального профита следуйте следующей инструкции:\n\n"
        "🟢 1. Пройти регистрацию в букмекерской конторе <a href='https://1wwbnd.com/casino/list?open=register'>1WIN("
        "CLICK) </a> \n"
        "Если не открывается - заходим с включенным VPN (Швеция). В Play Market/App Store полно бесплатных сервисов, "
        "например: Vpnify, Planet VPN, Hotspot VPN и так далее!\n\n"
        "<code>Без регистрации доступ к сигналам не будет открыт!</code>\n\n"
        "🟢 2. Пополнить баланс своего аккаунта.\n\n"
        "🟢 3. Перейти в раздел 1win games и выбрать игру 💣'MINE'.\n\n"
        "🟢 4. Выставить кол-во ловушек в размере трёх. Это важно!\n\n"
        "🟢 5. Запросить сигнал в боте и ставить по сигналам из бота.\n\n"
        "🟢 6. При неудачном сигнале советуем удвоить(Х²) ставку что бы полностью перекрыть потерю при следующем "
        "сигнале."
    )
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Вернуться в меню", callback_data="back_to_menu")
    )
    # Удаление старого сообщения
    await bot.delete_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
    )
    # Отправка нового сообщения с инструкцией
    await bot.send_photo(
        chat_id=callback_query.message.chat.id,
        photo=open("INSTRUKT.jpg", "rb"),  # Путь к изображению
        caption=instruction_text,
        reply_markup=keyboard,
        parse_mode="HTML",
    )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'signal')
async def signal_callback(callback_query: types.CallbackQuery):
    if not is_valid_registration_id:
        await callback_query.answer(
            "Пожалуйста, сначала зарегистрируйтесь для доступа к Сигналам.",
            show_alert=True
        )
        return  # Выходим из функции, чтобы не выполнять дальнейший код
    # Удаляем меню
    await bot.delete_message(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.message_id,
    )

    # Проверяем, были ли введены 8 цифр пользователем
    if is_valid_registration_id:
        # Если да, отправляем сигнал
        # Отправляем сообщение о начале имитации загрузки
        loading_message = await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="🌐Анализирую базу данных..."
        )

        # Отправляем сообщение о начале имитации загрузки
        for loading_text in ["🛜Получаю данные с сервера...", "⚠️Изучаю запросы..."]:
            await asyncio.sleep(1)  # Задержка перед отправкой следующего сообщения
            await bot.edit_message_text(
                chat_id=callback_query.message.chat.id,
                message_id=loading_message.message_id,
                text=loading_text
            )

        # Получение случайного изображения и отправка
        photo_files = os.listdir(photo_directory)
        if photo_files:
            random_photo_file = random.choice(photo_files)
            photo_path = os.path.join(photo_directory, random_photo_file)
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=loading_message.message_id)
            await bot.send_photo(
                chat_id=callback_query.message.chat.id,
                photo=open(photo_path, "rb"),
                caption="Вот сигнал!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="💣 Выдать сигнал 💣", callback_data="signal")]
                ])
            )
        else:
            await bot.send_message(
                chat_id=callback_query.message.chat.id,
                text="В директории нет изображений."
            )
    else:
        # Если нет, уведомляем пользователя о необходимости ввести 8 цифр
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="Пожалуйста, сначала введите 8 цифр."
        )


@dp.callback_query_handler(lambda callback_query: callback_query.data == 'new_signal')
async def new_signal_callback(callback_query: types.CallbackQuery):
    # Получение случайного изображения и отправка
    photo_files = os.listdir(photo_directory)
    if photo_files:
        random_photo_file = random.choice(photo_files)
        photo_path = os.path.join(photo_directory, random_photo_file)
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
        await bot.send_photo(
            chat_id=callback_query.message.chat.id,
            photo=open(photo_path, "rb"),
            caption="Вот сигнал!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💣 Выдать сигнал 💣", callback_data="new_signal")]
            ])
        )
    else:
        await bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="В директории нет изображений."
        )


async def on_startup(dp):
    await bot.set_my_commands([
        types.BotCommand("start", "Начать")
    ])


async def on_shutdown(dp):
    # Close the bot's session and connector when the bot shuts down
    await bot.session.close()


if __name__ == '__main__':
    while True:
        try:
            loop = asyncio.get_event_loop()  # Получаем цикл событий
            loop.create_task(on_startup(dp))  # Создаем задачу для запуска на старте
            loop.run_until_complete(dp.start_polling())  # Запускаем бота
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            traceback.print_exc()  # Выводим traceback ошибки
            continue  # Продолжаем цикл даже после ошибки
