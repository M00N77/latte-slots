from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from db import upsert_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await upsert_user(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username,
    )
    await message.answer(
        "Привет! Ты зарегистрирован. Теперь тебя можно приглашать на встречи.\n"
        "Команды: /add — добавить встречу, /day, /week, /my — просмотр."
    )
