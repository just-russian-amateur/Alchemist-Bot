from aiogram import Router, F  # Подключение библиотек
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import classes.solve_flasks as sf
from config_logger import ConfigLogger

import asyncio


rtr = Router()
logger = ConfigLogger(__name__)


@rtr.callback_query(
    sf.SolveFlasks.start_solving,
    F.data.in_(
        [
            'start_solving', 'upload_new_image'
        ]
    )
)    #   Команды выбора режима распознавания
async def start_solving(callback: CallbackQuery, state: FSMContext):
    """Функция загрузки изображения"""
    if callback.data == 'start_solving':
        logger.log_info('Пользователь %(callback.from_user.id)s приступил к загрузке первого изображения')
        await callback.message.answer("So let's get started😎\nUpload the screenshot as an image, please")
        await callback.answer()
        await state.set_state(sf.SolveFlasks.send_photo)
    elif callback.data == 'upload_new_image':
        logger.log_info('Пользователь %(callback.from_user.id)s приступил к загрузке нового изображения')
        await callback.message.answer('Upload a new screenshot as an image, please')
        await callback.answer()
        await state.set_state(sf.SolveFlasks.send_photo)


@rtr.message(sf.SolveFlasks.start_solving)
async def start_solving_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме нажатия кнопки'''
    logger.log_info('Пользователь %(message.from_user.id)s ввел неверную команду перед загрузкой изображения')
    msg = await message.answer('To get started, click the "🚀Start solving" button, please')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()