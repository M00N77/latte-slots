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
from keyboards.calendar import build_calendar
from keyboards.timepicker import hours_keyboard, minutes_keyboard
from keyboards.menu import meetings_menu, cancel_kb

router = Router()
TZ = ZoneInfo(TIMEZONE)


def participants_keyboard(users, selected):
    rows = []
    for uid, name in users:
        mark = "✅ " if uid in selected else ""
        rows.append([InlineKeyboardButton(text=f"{mark}{name}", callback_data=f"p:{uid}")])
    rows.append([InlineKeyboardButton(text="Готово ✅", callback_data="p:done")])
    rows.append([InlineKeyboardButton(text="✖️ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def _ask_title(target_message, state):
    await state.set_state(AddMeeting.title)
    await target_message.answer("Название встречи (или '-' если без названия):", reply_markup=cancel_kb())


@router.callback_query(F.data == "mtg:add")
async def add_from_menu(callback: CallbackQuery, state: FSMContext):
    await _ask_title(callback.message, state)
    await callback.answer()


@router.message(Command("add"))
async def add_from_cmd(message: Message, state: FSMContext):
    await _ask_title(message, state)


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
        if not selected:
            await callback.answer("Выбери хотя бы одного участника", show_alert=True)
            return
        await state.set_state(AddMeeting.date)
        now = datetime.now(TZ)
        await callback.message.answer("Выбери дату встречи:", reply_markup=build_calendar(now.year, now.month))
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
    await callback.message.edit_reply_markup(reply_markup=participants_keyboard(users, selected))
    await callback.answer()


@router.callback_query(F.data == "cal:ignore")
async def cal_ignore(callback: CallbackQuery):
    await callback.answer()


@router.callback_query(AddMeeting.date, F.data.startswith("cal:nav:"))
async def cal_nav(callback: CallbackQuery, state: FSMContext):
    ym = callback.data.split(":")[2]
    year, month = ym.split("-")
    await callback.message.edit_reply_markup(reply_markup=build_calendar(int(year), int(month)))
    await callback.answer()


@router.callback_query(AddMeeting.date, F.data.startswith("cal:day:"))
async def cal_day(callback: CallbackQuery, state: FSMContext):
    picked = callback.data.split(":", 2)[2]
    await state.update_data(date=picked)
    await state.set_state(AddMeeting.start_time)
    await callback.message.answer("Выбери ЧАС начала:", reply_markup=hours_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("time:h:"))
async def pick_hour(callback: CallbackQuery, state: FSMContext):
    hour = callback.data.split(":")[2]
    await state.update_data(temp_hour=hour)
    await callback.message.edit_text(f"Час {hour} выбран. Выбери минуты:", reply_markup=minutes_keyboard(hour))
    await callback.answer()


@router.callback_query(F.data.startswith("time:m:"))
async def pick_minute(callback: CallbackQuery, state: FSMContext):
    minute = callback.data.split(":")[2]
    data = await state.get_data()
    hour = data.get("temp_hour", "00")
    time_str = f"{hour}:{minute}"
    current = await state.get_state()
    if current == AddMeeting.start_time.state:
        await state.update_data(start_time=time_str)
        await state.set_state(AddMeeting.end_time)
        await callback.message.edit_text("Выбери ЧАС окончания:", reply_markup=hours_keyboard())
        await callback.answer()
        return
    await state.update_data(end_time=time_str)
    await _finalize(callback, state)
    await callback.answer()


async def _finalize(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    start_dt = datetime.strptime(
        f"{data['date']} {data['start_time']}", "%Y-%m-%d %H:%M"
    ).replace(tzinfo=TZ)
    end_dt = datetime.strptime(
        f"{data['date']} {data['end_time']}", "%Y-%m-%d %H:%M"
    ).replace(tzinfo=TZ)
    start_ts = int(start_dt.timestamp())
    end_ts = int(end_dt.timestamp())

    if start_ts < int(datetime.now(TZ).timestamp()):
        await callback.message.edit_text("Нельзя создать встречу в прошлом.")
        await callback.message.answer("Меню встреч:", reply_markup=meetings_menu())
        await state.clear()
        return

    if end_ts <= start_ts:
        await state.set_state(AddMeeting.end_time)
        await callback.message.edit_text(
            "Окончание должно быть позже начала. Выбери ЧАС окончания заново:",
            reply_markup=hours_keyboard(),
        )
        return

    selected = data["selected"]
    conflicts = await svc.has_conflict(selected, start_ts, end_ts)
    if conflicts:
        lines = []
        for c in conflicts:
            c_start = datetime.fromtimestamp(c[3], TZ).strftime("%d.%m %H:%M")
            c_end = datetime.fromtimestamp(c[4], TZ).strftime("%H:%M")
            lines.append(f"— {c[1]} занят(а) во встрече «{c[2]}» ({c_start}–{c_end})")
        await callback.message.edit_text("Не могу сохранить, есть пересечения:\n" + "\n".join(lines))
        await callback.message.answer("Меню встреч:", reply_markup=meetings_menu())
        await state.clear()
        return

    await svc.create_meeting(data["title"], callback.from_user.id, selected, start_ts, end_ts)
    await callback.message.edit_text("Встреча сохранена ✅")
    await callback.message.answer("Меню встреч:", reply_markup=meetings_menu())
    await state.clear()
