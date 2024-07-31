import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from handlers import Handlers
from scheduler import Scheduler
from config import API_TOKEN, WEBHOOK_URL, WEBHOOK_PATH

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Установка middleware для логирования
dp.middleware.setup(LoggingMiddleware())

# Регистрация обработчиков
Handlers.register_handlers(dp, bot)

async def on_startup_webhook(dp):
    await Scheduler.on_startup(dp, bot)
    asyncio.create_task(Scheduler.scheduled(3600, bot))
    logging.info("Bot started using webhook mode.")

async def on_startup_polling(dp):
    asyncio.create_task(Scheduler.scheduled(3600, bot))
    logging.info("Bot started using polling mode.")

def main():
    loop = asyncio.get_event_loop()
    webhook_active = loop.run_until_complete(Scheduler.check_webhook(bot))

    if webhook_active:
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            skip_updates=True,
            on_startup=on_startup_webhook,
            on_shutdown=Scheduler.on_shutdown(dp,bot),
            host='127.0.0.1',
            port=8000,
        )
    else:
        logging.info("Switching to polling mode due to webhook being inaccessible.")
        executor.start_polling(
            dispatcher=dp,
            skip_updates=True,
            on_startup=on_startup_polling,
        )

if __name__ == '__main__':
    main()
