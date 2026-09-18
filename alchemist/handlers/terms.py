from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InputRichMessage

import classes.all_my_classes as amc
from richmessages.all_my_rich_messages import create_rich_msg, build_terms_msg
from texts.all_my_texts import TermsTexts
from callbacks.all_my_callbacks import CallbacksData


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def handle_terms(update_type: Message | CallbackQuery):
    '''Вспомогательная функция для вывода текста в зависимости от формата сообщения'''

    user_id = update_type.from_user.id

    if isinstance(update_type, CallbackQuery):
        send_func = update_type.message.edit_text
    else:
        await update_type.delete()
        send_func = update_type.answer_rich
        
    logger.log_info(f'Пользователем {user_id} был вызван показ пользовательского соглашения')

    await send_func(
        rich_message=InputRichMessage(
            blocks=create_rich_msg(
                TermsTexts.TERMS,
                build_terms_msg()
            )
        )
    )
    
    if isinstance(update_type, CallbackQuery):
        await update_type.answer()


@rtr.message(Command(CallbacksData.TERMS))  # Команда для показа пользовательского соглашения
async def call_terms_message(message: Message):
    '''Функция для показа пользовательского соглашения'''
    await handle_terms(message)


@rtr.callback_query(
    amc.SolveFlasks.start_solving,
    F.data == CallbacksData.TERMS
)
async def call_terms_callback(callback: CallbackQuery):
    '''Функция для показа пользовательского соглашения'''
    await handle_terms(callback)
