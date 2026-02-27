from aiogram import Router
from aiogram.types import Message, CallbackQuery

import classes.all_my_classes as amc


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def handle_updates(update_type: Message | CallbackQuery):
    '''Вспомогательная функция для вывода текста в зависимости от формата сообщения'''
    user_id = update_type.from_user.id
    logger.log_info(f'Данные пользователя {user_id} были изменены в redis-хранилище')
    await update_type.answer('I have received important updates, to continue using me please restart me by typing /start🙂')
    if isinstance(update_type, CallbackQuery):
        await update_type.answer()


@rtr.callback_query()
async def after_update_database_callback(callback: CallbackQuery):
    '''Функция для обработки нажатий любых кнопок пользователем после изменений параметров пользователя в базе данных'''
    await handle_updates(callback)


@rtr.message()
async def after_update_database_message(message: Message):
    '''Функция для обработки любых сообщений пользователея после изменений параметров пользователя в базе данных'''
    await handle_updates(message)
