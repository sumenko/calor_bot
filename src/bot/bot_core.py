"""
get_message_from_user

put_message_to_the_queue
parse_messages_from_queue
answer_to_queue
"""

# имя класса в единственном числе
# имя модуля во мн числе, кроме отдельных main config и тд

import asyncio
from datetime import datetime
from aiogram import Bot, Dispatcher, typesпше
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F

# CalorGroupBot
# calor_user_bot

TOKEN = "8388031780:AAHloexGBB2lwQitxc2mX_rDA2cpieHU3Tc"

bot = Bot(token=TOKEN)
dp = Dispatcher()


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
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())