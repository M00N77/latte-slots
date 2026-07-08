from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.menu import ads_menu

router = Router()


@router.callback_query(F.data == "ads:info")
async def ads_info(callback: CallbackQuery):
    text = (
        "📊 Раздел «Анализ рекламы» (в разработке).\n\n"
        "Задумка: ежедневно тянуть статистику кампаний Wildberries и Ozon, "
        "считать ДРР и ROAS, помечать убыточные кампании и присылать краткие "
        "рекомендации: снизить ставку / сузить аудиторию / отключить."
    )
    await callback.message.edit_text(text, reply_markup=ads_menu())
    await callback.answer()
