# config.py
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Получение токена и ключа из переменных среды
API_TOKEN = os.getenv('tg_bot_KEY')
WEATHER_API_KEY = os.getenv('Servc_WEATHER_API_KEY')
NGROK_URL = os.getenv('NGROK_URL')

# Проверка значений переменных
if not API_TOKEN or not WEATHER_API_KEY or not NGROK_URL:
    raise ValueError("API_TOKEN, WEATHER_API_KEY и NGROK_URL должны быть инициализированы")

WEBHOOK_PATH = '/webhook/' + API_TOKEN
WEBHOOK_URL = f"{NGROK_URL}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)
