from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from db import upsert_user
from keyboards.menu import main_menu

router = Router()

MAIN_TEXT = "Главное меню. Выбери раздел:"


@router.message(CommandStart())
async def cmd_start(message: Message):
    await upsert_user(
        message.from_user.id,
        message.from_user.full_name,
        message.from_user.username,
    )
    await message.answer(MAIN_TEXT, reply_markup=main_menu())


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    await message.answer(MAIN_TEXT, reply_markup=main_menu())
