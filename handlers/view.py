from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config import TIMEZONE
from services import meetings as svc
from keyboards.menu import meetings_menu

router = Router()
TZ = ZoneInfo(TIMEZONE)


def fmt(ts):
    return datetime.fromtimestamp(ts, TZ).strftime("%d.%m %H:%M")


async def render(meetings):
    if not meetings:
        return "Встреч нет."
    lines = []
    for mid, title, start_ts, end_ts in meetings:
        names = await svc.get_attendee_names(mid)
        lines.append(
            f"🕒 {fmt(start_ts)}–{fmt(end_ts)} | {title}\n   Участники: {', '.join(names)}"
        )
    return "\n\n".join(lines)


async def day_text():
    now = datetime.now(TZ)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    meetings = await svc.get_meetings_between(int(start.timestamp()), int(end.timestamp()))
    return "📅 Встречи на сегодня:\n\n" + await render(meetings)


async def week_text():
    now = datetime.now(TZ)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    meetings = await svc.get_meetings_between(int(start.timestamp()), int(end.timestamp()))
    return "📅 Встречи на неделю:\n\n" + await render(meetings)


async def my_text(user_id):
    meetings = await svc.get_user_meetings(user_id)
    return "📅 Мои встречи:\n\n" + await render(meetings)


@router.callback_query(F.data == "mtg:day")
async def cb_day(callback: CallbackQuery):
    await callback.message.answer(await day_text(), reply_markup=meetings_menu())
    await callback.answer()


@router.callback_query(F.data == "mtg:week")
async def cb_week(callback: CallbackQuery):
    await callback.message.answer(await week_text(), reply_markup=meetings_menu())
    await callback.answer()


@router.callback_query(F.data == "mtg:my")
async def cb_my(callback: CallbackQuery):
    await callback.message.answer(await my_text(callback.from_user.id), reply_markup=meetings_menu())
    await callback.answer()


@router.message(Command("day"))
async def day(message: Message):
    await message.answer(await day_text())


@router.message(Command("week"))
async def week(message: Message):
    await message.answer(await week_text())


@router.message(Command("my"))
async def my(message: Message):
    await message.answer(await my_text(message.from_user.id))
