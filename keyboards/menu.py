from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Встречи", callback_data="nav:meetings")],
        [InlineKeyboardButton(text="📊 Анализ рекламы", callback_data="nav:ads")],
    ])


def meetings_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить встречу", callback_data="mtg:add")],
        [InlineKeyboardButton(text="📅 На день", callback_data="mtg:day")],
        [InlineKeyboardButton(text="🗓 На неделю", callback_data="mtg:week")],
        [InlineKeyboardButton(text="👤 Мои встречи", callback_data="mtg:my")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:main")],
    ])


def ads_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ℹ️ О разделе", callback_data="ads:info")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="nav:main")],
    ])


def cancel_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✖️ Отмена", callback_data="cancel")]
    ])
