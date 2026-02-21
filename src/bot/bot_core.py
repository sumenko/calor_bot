"""
get_message_from_user

put_message_to_the_queue
parse_messages_from_queue
answer_to_queue
"""

# имя класса в единственном числе
# имя модуля во мн числе, кроме отдельных main config и тд

import asyncio
import asyncpg

from datetime import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
import os

# CalorGroupBot
# calor_user_bot

load_dotenv()  # Загружаем переменные из .env

TOKEN = os.getenv("BOT_TOKEN")

DB_CONFIG = {
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "host": os.getenv("DB_HOST"),
    "port": int(os.getenv("DB_PORT")),
}

bot = Bot(token=TOKEN)
dp = Dispatcher()

db_pool = None

async def init_db():
    global db_pool
    db_pool = await asyncpg.create_pool(**DB_CONFIG)

# Функция для команд (все что начинается с "/")
async def handle_command(user_id: int, text: str, timestamp: datetime):
    print(f"[COMMAND] User: {user_id}, Text: {text} Time: {timestamp}")


# Функция для обычных сообщений
async def handle_text(user_id: int, text: str, timestamp: datetime):
    print(f"[TEXT] User: {user_id}, Text: {text} Time: {timestamp}")


# Обработчик всех сообщений
@dp.message()
async def message_router(message: Message):
    user_id = message.from_user.id
    timestamp = message.date
    text = message.text or ""
    if text.startswith("/"):
        await handle_command(user_id, text, timestamp)
    else:
        await handle_text(user_id, text, timestamp)


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())