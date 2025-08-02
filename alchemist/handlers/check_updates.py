from aiogram import Router
from aiogram.types import Message, CallbackQuery

import classes.all_my_classes as amc


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.callback_query()
async def after_update_database(callback: CallbackQuery):
    '''Функция для обработки нажатий любых кнопок пользователем после изменений параметров пользователя в базе данных'''
    logger.log_info(f'Данные пользователя {callback.from_user.id} были изменены в redis-хранилище')
    await callback.message.answer('I have received important updates, to continue using me please restart me by typing /start🙂')
    await callback.answer()


@rtr.message()
async def after_update_database(message: Message):
    '''Функция для обработки любых сообщений пользователея после изменений параметров пользователя в базе данных'''
    logger.log_info(f'Данные пользователя {message.from_user.id} были изменены в redis-хранилище')
    await message.answer('I have received important updates, to continue using me please restart me by typing /start🙂')
