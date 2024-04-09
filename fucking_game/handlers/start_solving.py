from aiogram import Router, F  # Подключение библиотек
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import classes.solve_flasks as sf

import asyncio
import logging


rtr = Router()


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
        await callback.message.answer("So let's get started😎\nUpload the screenshot as an image, please")
        await callback.answer()
    elif callback.data == 'upload_new_image':
        await callback.message.answer('Upload a new screenshot as an image, please')
        await callback.answer()
    await state.set_state(sf.SolveFlasks.send_photo)


@rtr.message(sf.SolveFlasks.start_solving)
async def start_solving_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме нажатия кнопки'''
    msg = await message.answer('To get started, click the "🚀Start solving" button, please')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()