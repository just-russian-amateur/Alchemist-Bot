from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import ok
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
        send_func = update_type.answer
        
    logger.log_info(f'Пользователем {user_id} был вызван показ пользовательского соглашения')

    await send_func(TermsTexts.TERMS, parse_mode='HTML', reply_markup=ok())
    
    if isinstance(update_type, CallbackQuery):
        await update_type.answer()


@rtr.message(Command(CallbacksData.TERMS))  # Команда для показа пользовательского соглашения
async def terms_message(message: Message):
    '''Функция для показа пользовательского соглашения'''
    await handle_terms(message)


@rtr.callback_query(
    amc.SolveFlasks.start_solving,
    F.data == CallbacksData.TERMS
)
async def terms_callback(callback: CallbackQuery):
    '''Функция для показа пользовательского соглашения'''
    await handle_terms(callback)
