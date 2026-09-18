from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputRichMessage
from aiogram.fsm.context import FSMContext

import classes.all_my_classes as amc
import config
from richmessages.all_my_rich_messages import (
    create_rich_msg,
    build_pay_attempts_msg,
    build_continue_msg,
    fill_format
)
from texts.all_my_texts import StartSolvingTexts
from texts.redis_keys import RedisKeys
from callbacks.all_my_callbacks import CallbacksData

import asyncio
from math import isnan


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def check_attempts(
        data: dict,
        callback: CallbackQuery,
        state: FSMContext
):
    '''Функция для проверки наличия попыток у пользователя'''

    await state.update_data(**{RedisKeys.NEW_SEGMENTS: 0})

    logger.log_info(f'Пользователь {callback.from_user.id} приступил к загрузке изображения')

    free_attempts = data.get(RedisKeys.FREE_ATTEMPTS)
    paid_attempts = data.get(RedisKeys.PAID_ATTEMPTS)

    if paid_attempts == 0 and free_attempts == 0:
        logger.log_info(f'У пользователя {callback.from_user.id} закончились попытки')

        set_state = amc.SolveFlasks.pay_attempts
        await callback.message.edit_text(
            rich_message=InputRichMessage(
                blocks=create_rich_msg(
                    StartSolvingTexts.OUT_ATTEMPTS,
                    build_pay_attempts_msg()
                )
            )
        )
    else:
        set_state = amc.SolveFlasks.send_photo

        if isnan(free_attempts):
            msg_text = StartSolvingTexts.START_SOLVING_FRIEND
        elif isnan(paid_attempts):
            msg_text = StartSolvingTexts.START_SOLVING_UNLIM
        elif paid_attempts > 0 and free_attempts > 0:
            msg_text = fill_format(
                StartSolvingTexts.START_SOLVING_FREE_PAID,
                free_attempts=free_attempts,
                paid_attempts=paid_attempts
            )
        elif paid_attempts == 0 and free_attempts > 0:
            msg_text = fill_format(
                StartSolvingTexts.START_SOLVING_FREE,
                free_attempts=free_attempts
            )
        elif paid_attempts > 0 and free_attempts == 0:
            msg_text = fill_format(
                StartSolvingTexts.START_SOLVING_PAID,
                paid_attempts=paid_attempts
            )

        await callback.message.edit_text(rich_message=InputRichMessage(blocks=msg_text))

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
        await check_attempts(user_data, callback, state)
    elif callback.data == CallbacksData.RULES:
        await callback.message.edit_text(
            rich_message=InputRichMessage(
                blocks=create_rich_msg(
                    StartSolvingTexts.RULES,
                    build_continue_msg()
                )
            )
        )
    elif callback.data == CallbacksData.BUY_ATTEMPTS:
        logger.log_info(f'Пользователь {callback.from_user.id} захотел купить попытки')

        await callback.message.edit_text(
            rich_message=InputRichMessage(
                blocks=create_rich_msg(
                    StartSolvingTexts.BUY_ATTEMPTS,
                    build_pay_attempts_msg()
                )
            )
        )

        await state.set_state(amc.SolveFlasks.pay_attempts)

    await callback.answer()


@rtr.callback_query(
    F.data.in_(
        [CallbacksData.OK, CallbacksData.CONTINUE]
    )
)
async def accept_terms_agreement(callback: CallbackQuery):
    '''Функция обработки действий пользователя после ввода команды из меню'''
    await callback.message.delete()


@rtr.message(amc.SolveFlasks.start_solving)
async def start_solving_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме нажатия кнопки'''

    # Получаем сведения о попытках и на их основе собираем дополнение к сообщению бота

    logger.log_info(f'Пользователь {message.from_user.id} ввел неверную команду перед загрузкой изображения')

    if await config.redis.sismember(RedisKeys.FRIENDS, message.from_user.id):
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
