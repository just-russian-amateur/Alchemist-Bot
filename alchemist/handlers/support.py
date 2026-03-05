from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import feedback
from texts.all_my_texts import SupportTexts
from callbacks.all_my_callbacks import CallbacksData


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.message(Command(CallbacksData.SUPPORT))  # Команда для вызова ссылки на чат с разработчиком
async def call_support(message: Message, state: FSMContext):
    '''Функция для вызова кнопки-ссылки на чат с разработчиком'''

    logger.log_info(f'Пользователем {message.from_user.id} была вызвана поддержка')

    await message.delete()

    await message.answer(
        SupportTexts.SUPPORT,
        reply_markup=feedback()
    )
    
    await state.set_state(amc.SolveFlasks.start_solving)
