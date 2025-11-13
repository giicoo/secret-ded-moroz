import asyncio
import logging
import os

from dotenv import load_dotenv
from maxapi import Bot, Dispatcher
from maxapi.types import BotStarted, Command, MessageCreated

# Загружаем переменные из .env файла
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Ответ бота при нажатии на кнопку "Начать"
@dp.bot_started()
async def bot_started(event: BotStarted):
    await event.bot.send_message(
        chat_id=event.chat_id,
        text='Привет! Отправь мне /start'
    )

# Ответ бота на команду /start
@dp.message_created(Command('start'))
async def hello(event: MessageCreated):
    await event.message.answer(f"Пример чат-бота для MAX 💙")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())