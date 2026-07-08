from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.menu import main_menu, meetings_menu, ads_menu

router = Router()


@router.callback_query(F.data == "nav:main")
async def nav_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Главное меню. Выбери раздел:", reply_markup=main_menu())
    await callback.answer()


@router.callback_query(F.data == "nav:meetings")
async def nav_meetings(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("📅 Встречи. Выбери действие:", reply_markup=meetings_menu())
    await callback.answer()


@router.callback_query(F.data == "nav:ads")
async def nav_ads(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("📊 Анализ рекламы:", reply_markup=ads_menu())
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await callback.message.answer("Отменено.", reply_markup=meetings_menu())
    await callback.answer()
