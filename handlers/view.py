from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import TIMEZONE
from services import meetings as svc

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


@router.message(Command("day"))
async def day(message: Message):
    now = datetime.now(TZ)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    meetings = await svc.get_meetings_between(int(start.timestamp()), int(end.timestamp()))
    await message.answer("📅 Встречи на сегодня:\n\n" + await render(meetings))


@router.message(Command("week"))
async def week(message: Message):
    now = datetime.now(TZ)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=7)
    meetings = await svc.get_meetings_between(int(start.timestamp()), int(end.timestamp()))
    await message.answer("📅 Встречи на неделю:\n\n" + await render(meetings))


@router.message(Command("my"))
async def my(message: Message):
    meetings = await svc.get_user_meetings(message.from_user.id)
    await message.answer("📅 Мои встречи:\n\n" + await render(meetings))
