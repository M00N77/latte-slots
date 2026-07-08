import calendar as _cal

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
MONTHS = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
]


def _prev_month(year, month):
    if month == 1:
        return year - 1, 12
    return year, month - 1


def _next_month(year, month):
    if month == 12:
        return year + 1, 1
    return year, month + 1


def build_calendar(year, month):
    py, pm = _prev_month(year, month)
    ny, nm = _next_month(year, month)
    rows = []
    rows.append([
        InlineKeyboardButton(text="◀️", callback_data=f"cal:nav:{py}-{pm:02d}"),
        InlineKeyboardButton(text=f"{MONTHS[month - 1]} {year}", callback_data="cal:ignore"),
        InlineKeyboardButton(text="▶️", callback_data=f"cal:nav:{ny}-{nm:02d}"),
    ])
    rows.append([InlineKeyboardButton(text=d, callback_data="cal:ignore") for d in WEEKDAYS])
    for week in _cal.Calendar().monthdayscalendar(year, month):
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(text=" ", callback_data="cal:ignore"))
            else:
                row.append(InlineKeyboardButton(
                    text=str(day),
                    callback_data=f"cal:day:{year:04d}-{month:02d}-{day:02d}",
                ))
        rows.append(row)
    rows.append([InlineKeyboardButton(text="✖️ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
