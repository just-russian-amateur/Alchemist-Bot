from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import pay_attempts, continue_solving

import asyncio
from math import isnan


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.callback_query(
    amc.SolveFlasks.start_solving,
    F.data.in_(
        [
            'start_solving', 'rules', 'buy_attempts', 'continue', 'ok'
        ]
    )
)
async def start_solving(callback: CallbackQuery, state: FSMContext):
    """Функция загрузки изображения или покупки попыток"""
    # Получаем сведения о попытках и на их основе собираем дополнение к сообщению бота
    attempts = await state.get_data()
            
    if callback.data in ['start_solving', 'continue', 'ok']:
        await state.update_data(new_segment=0)
        logger.log_info(f'Пользователь {callback.from_user.id} приступил к загрузке первого изображения')
        free_attempts = attempts['count_free_attempts']
        paid_attempts = attempts['count_paid_attempts']
        if paid_attempts == 0 and free_attempts == 0:
            msg_text = "Sorry, you've run out of attempts😞\nIf you want to continue now, you can buy multiple attempts for a small fee"
            msg_kb = pay_attempts()
            set_state = amc.SolveFlasks.pay_attempts
        else:
            msg_kb = None
            set_state = amc.SolveFlasks.send_photo
            if isnan(free_attempts):
                msg_text = f"So let's get started😎\nUpload the screenshot as an image, please\nNow you have an unlimited 🎟️"
            elif isnan(paid_attempts):
                msg_text = f"So let's get started😎\nUpload the screenshot as an image, please\nNow you have an unlimited 🎟️\n*Unlimited is available within two weeks from the date of payment"
            elif paid_attempts > 0 and free_attempts > 0:
                msg_text = f"So let's get started😎\nUpload the screenshot as an image, please\nNow you have:\nFree 🎟️: {free_attempts}\nPaid 🎟️: {paid_attempts}"
            elif paid_attempts == 0 and free_attempts > 0:
                msg_text = f"So let's get started😎\nUpload the screenshot as an image, please\nNow you have:\nFree 🎟️: {free_attempts}"
            elif paid_attempts > 0 and free_attempts == 0:
                msg_text = f"So let's get started😎\nUpload the screenshot as an image, please\nNow you have:\nPaid 🎟️: {paid_attempts}"

        await callback.message.edit_text(
            msg_text,
            reply_markup=msg_kb
        )
        await state.set_state(set_state)
    elif callback.data == 'rules':
        await callback.message.edit_text(
            "🙋‍♂️Now I'll tell you a little more about myself so that you know how to interact with me correctly. This is very important, because if you follow these few simple rules, you will get more accurate recognition of the colors inside the flasks, as well as the correct solutions for your specific level\nNow a few words about the functionality:\n✔️When you upload a screenshot, you need to upload it as a picture, not as a file, that is, in a chat with me, I should see your message as a full-fledged picture, about half the screen\n✔️The screenshot does not need to be cropped or compressed in any way, I will do it myself, so just send me the original image\n✔️<u><b>IF YOU USUALLY USE PATTERN MODE, PLEASE TURN IT OFF BEFORE TAKING A SCREENSHOT</b></u> and sending it to me, I'm not good at recognizing shapes inside colored rectangles, so I won't be able to recognize your level accurately (maybe I'll learn this in the future!)\n✔️Upload me an image with the initial position of the colors in the flasks (that is, 2 empty flasks and the rest are completely filled), this is the only way I can find a solution\nThat's probably all the subtleties that I wanted to tell you about working with me, good luck!🤞🤞🤞",
            parse_mode='HTML',
            reply_markup=continue_solving()
        )
    elif callback.data == 'buy_attempts':
        logger.log_info(f'Пользователь {callback.from_user.id} захотел купить попытки')
        await callback.message.edit_text(
            'You can choose one of the following offers for purchase',
            reply_markup=pay_attempts()
        )
        await state.set_state(amc.SolveFlasks.pay_attempts)
    await callback.answer()



@rtr.callback_query(
    F.data.in_(
        ['ok', 'continue']
    )
)
async def terms_agreement(callback: CallbackQuery):
    '''Функция обработки действий пользователя после ввода команды из меню'''
    await callback.message.delete()


@rtr.message(amc.SolveFlasks.start_solving)
async def start_solving_incorrectly(message: Message, state: FSMContext):
    '''Функция для отслеживания любых действий кроме нажатия кнопки'''
    # Получаем сведения о попытках и на их основе собираем дополнение к сообщению бота
    attempts = await state.get_data()
    logger.log_info(f'Пользователь {message.from_user.id} ввел неверную команду перед загрузкой изображения')
    if message.from_user.id in attempts['id_my_friends']:
        msg = await message.answer('To get started, click the "🚀Start solving" button, please')
    else:
        msg = await message.answer('To get started, click the "🚀Start solving" button or buy attempts by clicking the "🎟️Buy attempts" button, please')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()
