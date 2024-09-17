from aiogram import Router  # Подключение библиотек
from aiogram.filters import Command
from aiogram.types import Message

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import feedback


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.message(Command('support'))  # Команда для вызова ссылки на чат с разработчиком
async def call_support(message: Message):
    '''Функция для вызова кнопки-ссылки на чат с разработчиком'''
    logger.log_info(f'Пользователем {message.from_user.id} была вызвана поддержка')
    await message.delete()
    await message.answer(
        "If you got here, it means you still needed advice from my developer, I'm very sorry that this happened😞\nI hope that together you can solve your problem as soon as possible🙏\nIn order to contact my developer you just need to click on the button below and he'll answer you within a day, good luck✊",
        reply_markup=feedback()
    )
