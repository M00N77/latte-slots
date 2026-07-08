from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def hours_keyboard():
    rows = []
    row = []
    for h in range(24):
        row.append(InlineKeyboardButton(text=f"{h:02d}", callback_data=f"time:h:{h:02d}"))
        if len(row) == 6:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text="✖️ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def minutes_keyboard(hour):
    rows = [[
        InlineKeyboardButton(text=f"{hour}:00", callback_data="time:m:00"),
        InlineKeyboardButton(text=f"{hour}:15", callback_data="time:m:15"),
        InlineKeyboardButton(text=f"{hour}:30", callback_data="time:m:30"),
        InlineKeyboardButton(text=f"{hour}:45", callback_data="time:m:45"),
    ]]
    rows.append([InlineKeyboardButton(text="✖️ Отмена", callback_data="cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
