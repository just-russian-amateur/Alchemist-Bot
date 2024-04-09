from aiogram import Router  # Подключение библиотек
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import classes.solve_flasks as sf
from keyboards.all_my_keyboards import start_keyboard

import logging


rtr = Router()


@rtr.message(CommandStart())  # Команда для начала работы с ботом
async def send_welcome(message: Message,  state: FSMContext):
    """Приветственная функция"""
    await state.clear()

    await message.answer(
        f"Hello, <b>{message.from_user.first_name}</b>!😁\nNow I'll tell you a little more about myself so that you know how to interact with me correctly. This is very important, because if you follow these few simple rules, you will get more accurate recognition of the colors inside the flasks, as well as the correct solutions for your specific level\nNow a few words about the functionality:\n✔️When you upload a screenshot, you need to upload it as a picture, not as a file, that is, in a chat with me, I should see your message as a full-fledged picture, about half the screen\n✔️The screenshot does not need to be cropped or compressed in any way, I will do it myself, so just send me the original image\n✔️<u><b>IF YOU USUALLY USE PATTERN MODE, PLEASE TURN IT OFF BEFORE TAKING A SCREENSHOT</b></u> and sending it to me, I'm not good at recognizing shapes inside colored rectangles, so I won't be able to recognize your level accurately (maybe I'll learn this in the future!)\n✔️Upload me an image with the initial position of the colors in the flasks (that is, 2 empty flasks and the rest are completely filled), this is the only way I can find a solution\nThat's probably all the subtleties that I wanted to tell you about working with me, good luck!🤞🤞🤞\n\nTo restart me, you can enter the /start command.",
        parse_mode='HTML',
        reply_markup=start_keyboard()
    )
    await state.set_state(sf.SolveFlasks.start_solving)