from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from texts.all_my_texts import KeyboardTexts
from callbacks.all_my_callbacks import CallbacksData


def payment_kb(btn_text: str) -> list:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=btn_text, pay=True)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.CANCEL, callback_data=CallbacksData.CANCEL)
            ]
        ]
    )
