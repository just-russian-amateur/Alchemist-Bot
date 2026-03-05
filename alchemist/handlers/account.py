from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, User
from aiogram.fsm.context import FSMContext

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import account
from texts.all_my_texts import AccountTexts
from texts.redis_keys import RedisKeys
from callbacks.all_my_callbacks import CallbacksData

from math import isnan


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def create_account_message(user: User, data: FSMContext) -> tuple[str, bool]:
    '''Вспомогательная функция для создания сообщения'''

    if user.id in data[RedisKeys.FRIENDS_IDS]:

        free_attempts_note = AccountTexts.FRIENDS_NOTE
        text = AccountTexts.FRIENDS_MESSAGE.format(
            full_name=user.full_name,
            id=user.id,
            note=free_attempts_note
        )

        return text, True
    
    free_attempts_note = AccountTexts.USERS_NOTE
    free_attempts = data[RedisKeys.FREE_ATTEMPTS]

    if isnan(data[RedisKeys.PAID_ATTEMPTS]):

        paid_attempts = "unlimited"
        end_unlimited = data[RedisKeys.END_UNLIM]
        added_text = AccountTexts.TIMEOUT_UNLIM.format(end_unlimited=end_unlimited)
        account_mode = True
        
    else:
        
        paid_attempts = data[RedisKeys.PAID_ATTEMPTS]
        added_text = ""

        if data[RedisKeys.PAID_ATTEMPTS] != 0:
            account_mode = True
        else:
            account_mode = False

    text = AccountTexts.USERS_MESSAGE.format(
        full_name=user.full_name,
        id=user.id,
        free_attempts=free_attempts,
        note=free_attempts_note,
        paid_attempts=paid_attempts,
        added_text=added_text
    )

    return text, account_mode


async def show_account(update_type: Message | CallbackQuery, state: FSMContext):
    '''Вспомогательная функция для отображения сообщения'''

    user_data = await state.get_data()
    user = update_type.from_user

    text, mode = await create_account_message(user, user_data)

    if isinstance(update_type, CallbackQuery):
        send_func = update_type.message.edit_text
    else:
        await update_type.delete()
        send_func = update_type.answer

    await send_func(text, parse_mode='HTML', reply_markup=account(mode))

    if isinstance(update_type, CallbackQuery):
        await update_type.answer()
    
    logger.log_info(f"Пользователь {user.id} зашел в свой аккаунт")


@rtr.message(Command(CallbacksData.ACCOUNT))    # Команда для вызова профиля пользователя
async def my_account_message(message: Message, state: FSMContext):
    '''Функция для показа информации о пользователе'''

    await show_account(message, state)
    await state.set_state(amc.SolveFlasks.start_solving)
    

@rtr.callback_query(
    amc.SolveFlasks.pay_attempts,
    F.data == CallbacksData.ACCOUNT
)
@rtr.callback_query(
    amc.SolveFlasks.start_solving,
    F.data == CallbacksData.ACCOUNT
)
async def my_account_callback(callback: CallbackQuery, state: FSMContext):
    '''Функция для показа информации о пользователе'''

    await show_account(callback, state)

    current_state = await state.get_state()

    if current_state == amc.SolveFlasks.pay_attempts:
        await state.set_state(amc.SolveFlasks.start_solving)
