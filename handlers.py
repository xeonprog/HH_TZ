from aiogram import types
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove

import requests
from PIL import Image
from database import Database
from config import WEATHER_API_KEY
import logging

db = Database()

class Form(StatesGroup):
    name = State()
    age = State()
    city = State()  # Добавлено состояние для запроса города

class Handlers:
    user_id = None

    @staticmethod
    def register_handlers(dp: Dispatcher, bot):
        dp.register_message_handler(lambda message: Handlers.send_welcome(message, bot), commands=['start'])
        dp.register_message_handler(Handlers.send_help, commands=['help'])
        dp.register_message_handler(Handlers.echo, commands=['echo'])
        dp.register_message_handler(Handlers.send_inline, commands=['inline'])
        dp.register_callback_query_handler(Handlers.process_callback, lambda c: c.data in ['choice1', 'choice2'])
        dp.register_message_handler(Handlers.cmd_register, commands=['register'])
        dp.register_message_handler(Handlers.process_name, state=Form.name)
        dp.register_message_handler(Handlers.process_age, state=Form.age)
        dp.register_message_handler(lambda message: Handlers.handle_docs_photo(message, bot), content_types=['photo'])
        dp.register_message_handler(Handlers.list_users, commands=['users'])
        dp.register_message_handler(Handlers.get_weather, commands=['weather'])
        dp.register_message_handler(Handlers.process_city, state=Form.city)  # Обработка состояния ввода города
        dp.register_message_handler(Handlers.clear_reply_keyboard, commands=['clear_keyb'])

    @staticmethod
    async def send_welcome(message: types.Message, bot):
        Handlers.user_id = message.from_user.id
        await message.reply(f"Добро пожаловать в наш бот! Ваш chat_id: {Handlers.user_id}")

    @staticmethod
    async def send_help(message: types.Message):
        await message.reply("Доступные команды: /start, /help, /echo, /inline, /weather, /photo, /register.\n Для проверки события исключения, например: можно ввести возраст не цифрми, а текстом")

    @staticmethod
    async def echo(message: types.Message):
        # Добавим логирование
        logging.info(f"Echo command received: {message.text}")
        # Получение текста после команды /echo
        text_to_echo = message.text[len("/echo"):].strip()
        logging.info(f"Text to echo: {text_to_echo}")

        if not text_to_echo:
            await message.reply("Пожалуйста, предоставьте текст для эха после команды.")
        else:
            await message.reply(text_to_echo)

    @staticmethod
    async def clear_reply_keyboard(message: types.Message):
        await message.reply("Обычная клавиатура очищена.", reply_markup=ReplyKeyboardRemove())

    @staticmethod
    async def send_inline(message: types.Message):
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("Выбор 1", callback_data='choice1'),
            InlineKeyboardButton("Выбор 2", callback_data='choice2')
        )
        await message.reply("Сделайте выбор:", reply_markup=markup)

    @staticmethod
    async def process_callback(callback_query: types.CallbackQuery):
        if callback_query.data == 'choice1':
            await callback_query.message.answer('Вы выбрали Выбор 1')
        elif callback_query.data == 'choice2':
            await callback_query.message.answer('Вы выбрали Выбор 2')
        await callback_query.answer()

    @staticmethod
    async def cmd_register(message: types.Message):
        await Form.name.set()
        await message.reply("Введите ваше имя:")

    @staticmethod
    async def process_name(message: types.Message, state: FSMContext):
        await state.update_data(name=message.text)
        await Form.next()
        await message.reply("Введите ваш возраст:")

    @staticmethod
    async def process_age(message: types.Message, state: FSMContext):
        try:
            age = int(message.text)
            if age < 0:
                raise ValueError("Возраст не может быть отрицательным")
            await state.update_data(age=age)
            user_data = await state.get_data()
            db.add_user(message.from_user.id, user_data['name'], user_data['age'])
            await message.reply(f"Ваше имя: {user_data['name']}\nВаш возраст: {user_data['age']}")
            await state.finish()
        except ValueError:
            await message.reply("Пожалуйста, введите корректный возраст (целое число).")

    @staticmethod
    async def handle_docs_photo(message: types.Message, bot):
        file_id = message.photo[-1].file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path

        await message.photo[-1].download(file_path)
        image = Image.open(file_path)
        width, height = image.size

        await message.reply(f"Размер изображения: {width}x{height} пикселей")

    @staticmethod
    async def list_users(message: types.Message):
        users = db.get_users()
        user_list = '\n'.join([f"ID: {user[0]}, Имя: {user[1]}, Возраст: {user[2]}" for user in users])
        await message.reply(user_list if user_list else "Нет зарегистрированных пользователей")

    @staticmethod
    async def get_weather(message: types.Message):
        await Form.city.set()
        await message.reply("Введите название города:")

    @staticmethod
    async def process_city(message: types.Message, state: FSMContext):
        city = message.text
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        try:
            response = requests.get(url)
            response.raise_for_status()  # Проверка на успешность запроса
            weather_data = response.json()

            if weather_data.get('main'):
                weather = weather_data['main']
                await message.reply(f"Погода в {city}:\nТемпература: {weather['temp']}°C\nВлажность: {weather['humidity']}%")
            else:
                await message.reply("Город не найден. Попробуйте снова.")
        except requests.exceptions.RequestException as e:
            await message.reply(f"Произошла ошибка при получении данных о погоде: {e}")
        await state.finish()
