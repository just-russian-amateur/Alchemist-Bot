from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, InputRichMessage
from aiogram.fsm.context import FSMContext

import classes.all_my_classes as amc
from richmessages.all_my_rich_messages import create_rich_msg, build_feedback_msg
from texts.all_my_texts import SupportTexts
from callbacks.all_my_callbacks import CallbacksData


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.message(Command(CallbacksData.SUPPORT))  # Команда для вызова ссылки на чат с разработчиком
async def call_support(message: Message, state: FSMContext):
    '''Функция для вызова кнопки-ссылки на чат с разработчиком'''

    logger.log_info(f'Пользователем {message.from_user.id} была вызвана поддержка')

    await message.delete()

    await message.answer_rich(
        InputRichMessage(
            blocks=create_rich_msg(
                SupportTexts.SUPPORT,
                build_feedback_msg()
            )
        )
    )
    
    await state.set_state(amc.SolveFlasks.start_solving)
