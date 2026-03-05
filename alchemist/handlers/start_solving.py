from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import pay_attempts, continue_solving
from texts.all_my_texts import StartSolvingTexts
from texts.redis_keys import RedisKeys
from callbacks.all_my_callbacks import CallbacksData

import asyncio
from math import isnan


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def check_attempts(data: FSMContext, callback: CallbackQuery, state: FSMContext):
    '''Функция для проверки наличия попыток у пользователя'''

    await state.update_data(new_segment=0)

    logger.log_info(f'Пользователь {callback.from_user.id} приступил к загрузке изображения')

    free_attempts = data[RedisKeys.FREE_ATTEMPTS]
    paid_attempts = data[RedisKeys.PAID_ATTEMPTS]

    if paid_attempts == 0 and free_attempts == 0:
        logger.log_info(f'У пользователя {callback.from_user.id} закончились попытки')

        msg_text = StartSolvingTexts.OUT_ATTEMPTS
        msg_kb = pay_attempts()
        set_state = amc.SolveFlasks.pay_attempts
    else:
        msg_kb = None
        set_state = amc.SolveFlasks.send_photo

        if isnan(free_attempts):
            msg_text = StartSolvingTexts.START_SOLVING_FRIEND
        elif isnan(paid_attempts):
            msg_text = StartSolvingTexts.START_SOLVING_UNLIM
        elif paid_attempts > 0 and free_attempts > 0:
            msg_text = StartSolvingTexts.START_SOLVING_FREE_PAID.format(free_attempts=free_attempts, paid_attempts=paid_attempts)
        elif paid_attempts == 0 and free_attempts > 0:
            msg_text = StartSolvingTexts.START_SOLVING_FREE.format(free_attempts=free_attempts)
        elif paid_attempts > 0 and free_attempts == 0:
            msg_text = StartSolvingTexts.START_SOLVING_PAID.format(paid_attempts=paid_attempts)

    await callback.message.edit_text(
        msg_text,
        reply_markup=msg_kb
    )

    await state.set_state(set_state)


@rtr.callback_query(
    amc.SolveFlasks.start_solving,
    F.data.in_(
        [
            CallbacksData.START_SOLVING, CallbacksData.RULES, CallbacksData.BUY_ATTEMPTS,
            CallbacksData.CONTINUE, CallbacksData.OK
        ]
    )
)
async def start_solving(callback: CallbackQuery, state: FSMContext):
    """Функция загрузки изображения или покупки попыток"""

    # Получаем сведения о попытках и на их основе собираем дополнение к сообщению бота
    user_data = await state.get_data()
            
    if callback.data in [CallbacksData.START_SOLVING, CallbacksData.CONTINUE, CallbacksData.OK]:
        await check_attempts(
            data=user_data,
            callback=callback,
            state=state
        )
    elif callback.data == CallbacksData.RULES:
        await callback.message.edit_text(
            StartSolvingTexts.RULES,
            parse_mode='HTML',
            reply_markup=continue_solving()
        )
    elif callback.data == CallbacksData.BUY_ATTEMPTS:
        logger.log_info(f'Пользователь {callback.from_user.id} захотел купить попытки')

        await callback.message.edit_text(
            StartSolvingTexts.BUY_ATTEMPTS,
            reply_markup=pay_attempts()
        )

        await state.set_state(amc.SolveFlasks.pay_attempts)

    await callback.answer()



@rtr.callback_query(
    F.data.in_(
        [CallbacksData.OK, CallbacksData.CONTINUE]
    )
)
async def terms_agreement(callback: CallbackQuery):
    '''Функция обработки действий пользователя после ввода команды из меню'''
    await callback.message.delete()


@rtr.message(amc.SolveFlasks.start_solving)
async def start_solving_incorrectly(message: Message, state: FSMContext):
    '''Функция для отслеживания любых действий кроме нажатия кнопки'''

    # Получаем сведения о попытках и на их основе собираем дополнение к сообщению бота
    user_data = await state.get_data()

    logger.log_info(f'Пользователь {message.from_user.id} ввел неверную команду перед загрузкой изображения')

    if message.from_user.id in user_data[RedisKeys.FRIENDS_IDS]:
        msg = await message.answer(
            StartSolvingTexts.ERROR_ACTION_FREE,
            parse_mode='HTML'
        )
    else:
        msg = await message.answer(
            StartSolvingTexts.ERROR_ACTION,
            parse_mode='HTML'
        )

    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()
