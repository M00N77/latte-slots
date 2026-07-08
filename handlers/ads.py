import io

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from states import AdsAnalysis
from keyboards.menu import ads_menu, cancel_kb
from services import ads as ads_svc

router = Router()


async def _send_long(message, text):
    limit = 3500
    for i in range(0, len(text), limit):
        await message.answer(text[i:i + limit])


@router.callback_query(F.data == "ads:info")
async def ads_info(callback: CallbackQuery):
    text = (
        "📊 Раздел «Анализ рекламы».\n\n"
        "Загрузи CSV-выгрузку кампаний — бот посчитает ДРР, пометит убыточные "
        "и даст рекомендации.\n\n"
        "Колонки (первая строка — заголовки): campaign, spend, revenue, buyout, orders\n"
        "или по-русски: Кампания, Расход, Выручка, Выкуп, Заказы.\n\n"
        "Нет файла? Нажми «Демо-анализ»."
    )
    await callback.message.edit_text(text, reply_markup=ads_menu())
    await callback.answer()


@router.callback_query(F.data == "ads:upload")
async def ads_upload(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdsAnalysis.waiting_file)
    await callback.message.answer(
        "Пришли CSV-файл с выгрузкой кампаний одним документом:",
        reply_markup=cancel_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "ads:demo")
async def ads_demo(callback: CallbackQuery):
    results, summary = ads_svc.analyze(ads_svc.SAMPLE_ROWS)
    await _send_long(callback.message, ads_svc.format_report(results, summary))
    await callback.message.answer("Меню раздела:", reply_markup=ads_menu())
    await callback.answer()


@router.message(AdsAnalysis.waiting_file, F.document)
async def ads_receive_file(message: Message, state: FSMContext):
    doc = message.document
    if not (doc.file_name or "").lower().endswith(".csv"):
        await message.answer("Нужен файл .csv. Пришли CSV или нажми Отмена.", reply_markup=cancel_kb())
        return
    file = await message.bot.get_file(doc.file_id)
    buf = io.BytesIO()
    await message.bot.download_file(file.file_path, buf)
    rows = ads_svc.parse_csv(buf.getvalue())
    if not rows:
        await message.answer("Не удалось прочитать данные. Проверь заголовки колонок.", reply_markup=ads_menu())
        await state.clear()
        return
    results, summary = ads_svc.analyze(rows)
    await _send_long(message, ads_svc.format_report(results, summary))
    await message.answer("Меню раздела:", reply_markup=ads_menu())
    await state.clear()


@router.message(AdsAnalysis.waiting_file)
async def ads_wrong_input(message: Message):
    await message.answer("Жду CSV-файл документом. Или нажми Отмена.", reply_markup=cancel_kb())
