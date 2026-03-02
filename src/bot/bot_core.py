"""
get_message_from_user

put_message_to_the_queue
parse_messages_from_queue
answer_to_queue
"""

# имя класса в единственном числе
# имя модуля во мн числе, кроме отдельных main config и тд

from pathlib import Path
import asyncio
import asyncpg
from asyncpg.exceptions import DataError
from datetime import datetime as dt
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
import os
from commands import allowed_commands, command_execute_os
from cut_tags import TorrentFileNameCleaner
from time import process_time


load_dotenv()  # Загружаем переменные из .env

TOKEN = os.getenv("BOT_TOKEN")
DEBUG = os.getenv("DEBUG")

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


async def save_message(user_id: int, username: str, text: str, is_command: bool, timestamp: dt):
    try:
        async with db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO messages (user_id, username, text, is_command, created_at)
                VALUES ($1, $2, $3, $4, $5)
            """, user_id, username, text, is_command, timestamp)
    except DataError as e:
        print('Error', e)


async def execute_command(command, message):
    if command in allowed_commands:
        func = allowed_commands[command]['func']
        answer = func(command, message.text)
        
        if command == 'td':
            tfc = TorrentFileNameCleaner()
            answer = tfc.get_clean_numbered_text(answer)
        await message.reply(answer)
    else:
        await message.reply(f"⛔ Неизвестная команда")


@dp.message(F.document)
async def send_file(message: Message):

    document = message.document
    file_id = document.file_id
    file = await message.bot.get_file(file_id)

    file_type = file.file_path.split(".")[-1]
    file_name = dt.now().strftime('%Y-%m-%d_%H_%M_%H_%S.%f') + '.' + file_type
    file_size = file.file_size
    
    Path(f"downloads/{file_type}").mkdir(parents=True, exist_ok=True)
    download_path = os.path.join('downloads', file_type, file_name)
   
    await message.bot.download_file(file.file_path, download_path)
    answer = f"Получен файл формата '{file_type}' размер {file_size/1024:.1f}Kb"

    if file_type == 'torrent':
        result, _ = command_execute_os('add', message, f'\"{download_path}\"')
        status = "статус неизвестен"
        if "error" in result.lower():
            status = f"ошибка ({result})"
        if "success" in result.lower():
            status = "добавлен"
        answer += f'\nTransmission - {status}'
    await message.reply(answer)



@dp.message()
async def message_router(message: Message):
    if not message.text:
        return
    if DEBUG == '1':
        print("CHAT ID:", message.chat.id)
    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text
    timestamp = message.date.replace(tzinfo=None)
    
    is_command = text.startswith("/")

    if not await is_user_allowed(user_id):
        await message.reply(f"⛔ @{username}:{user_id} У вас нет доступа.")
        return
    if is_command:
        await save_message(user_id, username, text, is_command, timestamp)
        command = text[1:].split(' ')[0]
        await execute_command(command, message)
        
        # await message.reply(f"Записано ✅")
    # if DEBUG == '1':
    #     print('#'*80)
    #     print(message)
    #     print('#'*80)

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

GROUP_CHAT_ID = -5233701044
@dp.startup()
async def on_startup():
    await bot.send_message(GROUP_CHAT_ID, f"Я запустился за {process_time():3.03f}с ✅")


async def main():
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":

    asyncio.run(main())