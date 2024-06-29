from aiogram import Router, F  # Подключение библиотек
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import classes.all_my_classes as amc

import asyncio


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.callback_query(
    amc.SolveFlasks.start_solving,
    F.data.in_(
        [
            'start_solving', 'upload_new_image', 'continue', 'ok'
        ]
    )
)    #   Команды выбора режима распознавания
async def start_solving(callback: CallbackQuery, state: FSMContext):
    """Функция загрузки изображения"""
    if callback.data == 'start_solving':
        logger.log_info(f'Пользователь {callback.from_user.id} приступил к загрузке первого изображения')
        await callback.message.answer("So let's get started😎\nUpload the screenshot as an image, please")
        await callback.answer()
        await state.set_state(amc.SolveFlasks.send_photo)
    elif callback.data == 'upload_new_image' or callback.data == 'continue' or callback.data == 'ok':
        logger.log_info(f'Пользователь {callback.from_user.id} приступил к загрузке нового изображения')
        await callback.message.answer('Upload a new screenshot as an image, please')
        await callback.answer()
        await state.set_state(amc.SolveFlasks.send_photo)


@rtr.message(amc.SolveFlasks.start_solving)
async def start_solving_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме нажатия кнопки'''
    logger.log_info(f'Пользователь {message.from_user.id} ввел неверную команду перед загрузкой изображения')
    msg = await message.answer('To get started, click the "🚀Start solving" button, please')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()