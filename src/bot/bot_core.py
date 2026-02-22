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
from asyncpg.exceptions import DataError
from datetime import datetime, timezone
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
import os
import pytz

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

    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS allowed_users (
                user_id INT8 PRIMARY KEY,
                timezone TEXT            
            );
        """)

        await conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                username TEXT,
                text TEXT,
                is_command BOOLEAN,
                created_at TIMESTAMP
            );
        """)

async def is_user_allowed(user_id: int) -> bool:
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT user_id FROM allowed_users WHERE user_id = $1",
            user_id
        )
        return row is not None


async def save_message(user_id: int, username: str, text: str, is_command: bool, timestamp: datetime):
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO messages (user_id, username, text, is_command, created_at)
                VALUES ($1, $2, $3, $4, $5)
            """, user_id, username, text, is_command, timestamp)
    except DataError as e:
        print('Error', e)


@dp.message()
async def message_router(message: Message):
    if not message.text:
        return

    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text
    timestamp = message.date.replace(tzinfo=None)
    
    is_command = text.startswith("/")

    if not await is_user_allowed(user_id):
        await message.reply(f"⛔ @{username}:{user_id} У вас нет доступа.")
        return
    await save_message(user_id, username, text, is_command, timestamp)

    await message.reply(f"Записано ✅")

# # Функция для команд (все что начинается с "/")
# async def handle_command(user_id: int, text: str, timestamp: datetime):
#     print(f"[COMMAND] User: {user_id}, Text: {text} Time: {timestamp}")


# # Функция для обычных сообщений
# async def handle_text(user_id: int, text: str, timestamp: datetime):
#     print(f"[TEXT] User: {user_id}, Text: {text} Time: {timestamp}")


# Обработчик всех сообщений
# @dp.message()
# async def message_router(message: Message):
#     user_id = message.from_user.id
#     timestamp = message.date
#     text = message.text or ""
#     if text.startswith("/"):
#         await handle_command(user_id, text, timestamp)
#     else:
#         await handle_text(user_id, text, timestamp)


async def main():
    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":

    asyncio.run(main())