from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from config import TIMEZONE
from states import AddMeeting
from services import meetings as svc

router = Router()
TZ = ZoneInfo(TIMEZONE)


def participants_keyboard(users, selected):
    rows = []
    for uid, name in users:
        mark = "✅ " if uid in selected else ""
        rows.append([InlineKeyboardButton(text=f"{mark}{name}", callback_data=f"p:{uid}")])
    rows.append([InlineKeyboardButton(text="Готово", callback_data="p:done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("add"))
async def add_start(message: Message, state: FSMContext):
    await state.set_state(AddMeeting.title)
    await message.answer("Название встречи (или '-' если без названия):")


@router.message(AddMeeting.title)
async def add_title(message: Message, state: FSMContext):
    title = message.text.strip()
    if title == "-":
        title = "Без названия"
    await state.update_data(title=title, selected=[message.from_user.id])
    users = await svc.get_registered_users()
    await state.set_state(AddMeeting.participants)
    await message.answer(
        "Выбери участников (ты уже включён). Нажми 'Готово', когда закончишь:",
        reply_markup=participants_keyboard(users, [message.from_user.id]),
    )


@router.callback_query(AddMeeting.participants, F.data.startswith("p:"))
async def add_participants(callback: CallbackQuery, state: FSMContext):
    action = callback.data.split(":")[1]
    data = await state.get_data()
    selected = data.get("selected", [])
    if action == "done":
        await state.set_state(AddMeeting.date)
        await callback.message.answer("Дата встречи в формате ГГГГ-ММ-ДД:")
        await callback.answer()
        return
    uid = int(action)
    if uid in selected:
        if uid != callback.from_user.id:
            selected.remove(uid)
    else:
        selected.append(uid)
    await state.update_data(selected=selected)
    users = await svc.get_registered_users()
    await callback.message.edit_reply_markup(
        reply_markup=participants_keyboard(users, selected)
    )
    await callback.answer()


@router.message(AddMeeting.date)
async def add_date(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text.strip(), "%Y-%m-%d")
    except ValueError:
        await message.answer("Неверный формат. Введи дату как ГГГГ-ММ-ДД:")
        return
    await state.update_data(date=message.text.strip())
    await state.set_state(AddMeeting.start_time)
    await message.answer("Время начала в формате ЧЧ:ММ:")


@router.message(AddMeeting.start_time)
async def add_start_time(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text.strip(), "%H:%M")
    except ValueError:
        await message.answer("Неверный формат. Введи время как ЧЧ:ММ:")
        return
    await state.update_data(start_time=message.text.strip())
    await state.set_state(AddMeeting.end_time)
    await message.answer("Время окончания в формате ЧЧ:ММ:")


@router.message(AddMeeting.end_time)
async def add_end_time(message: Message, state: FSMContext):
    try:
        datetime.strptime(message.text.strip(), "%H:%M")
    except ValueError:
        await message.answer("Неверный формат. Введи время как ЧЧ:ММ:")
        return
    data = await state.get_data()
    start_dt = datetime.strptime(
        f"{data['date']} {data['start_time']}", "%Y-%m-%d %H:%M"
    ).replace(tzinfo=TZ)
    end_dt = datetime.strptime(
        f"{data['date']} {message.text.strip()}", "%Y-%m-%d %H:%M"
    ).replace(tzinfo=TZ)
    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())
    if end_ts <= start_ts:
        await message.answer("Окончание должно быть позже начала. Введи время окончания заново:")
        return
    selected = data["selected"]
    conflicts = await svc.has_conflict(selected, start_ts, end_ts)
    if conflicts:
        lines = [f"— {c[1]} занят(а) во встрече «{c[2]}»" for c in conflicts]
        await message.answer("Не могу сохранить, есть пересечения:\n" + "\n".join(lines))
        await state.clear()
        return
    await svc.create_meeting(data["title"], message.from_user.id, selected, start_ts, end_ts)
    await message.answer("Встреча сохранена ✅")
    await state.clear()
