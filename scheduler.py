from datetime import datetime, timedelta
import asyncio
from aiogram import Bot
from config import WEBHOOK_URL
import logging
from aiogram.utils.exceptions import RetryAfter

class Scheduler:
    @staticmethod
    async def scheduled(wait_for, bot: Bot):
        while True:
            await asyncio.sleep(wait_for)
            now = datetime.now()
            target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
            if now > target_time:
                target_time += timedelta(days=1)
            await asyncio.sleep((target_time - now).total_seconds())
            await bot.send_message(chat_id=Handlers.user_id, text="Не забудьте проверить уведомления!")

    @staticmethod
    async def on_startup(dp, bot: Bot):
        try:
            await bot.set_webhook(WEBHOOK_URL)
            logging.info("Webhook is set.")
        except RetryAfter as e:
            logging.warning(f"Flood control exceeded. Retry in {e.timeout} seconds.")
            await asyncio.sleep(e.timeout)
            await bot.set_webhook(WEBHOOK_URL)
            logging.info("Webhook is set after waiting.")

    @staticmethod
    async def on_shutdown(dp, bot: Bot):
        await bot.delete_webhook()
        await dp.storage.close()
        await dp.storage.wait_closed()

    @staticmethod
    async def check_webhook(bot: Bot):
        try:
            webhook_info = await bot.get_webhook_info()
            if webhook_info.url == WEBHOOK_URL:
                return True
            else:
                await bot.set_webhook(WEBHOOK_URL)
                webhook_info = await bot.get_webhook_info()
                if webhook_info.url == WEBHOOK_URL:
                    return True
                else:
                    logging.warning(f"Failed to set webhook. Current webhook URL: {webhook_info.url}")
                    return False
        except RetryAfter as e:
            logging.warning(f"Flood control exceeded. Retry in {e.timeout} seconds.")
            await asyncio.sleep(e.timeout)
            try:
                await bot.set_webhook(WEBHOOK_URL)
                webhook_info = await bot.get_webhook_info()
                if webhook_info.url == WEBHOOK_URL:
                    return True
            except Exception as e:
                logging.error(f"Failed to set webhook after retry: {e}")
                return False
        except Exception as e:
            logging.error(f"Failed to set webhook: {e}")
            return False
