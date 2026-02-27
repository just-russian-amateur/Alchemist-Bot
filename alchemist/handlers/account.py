from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, User
from aiogram.fsm.context import FSMContext

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import account

from math import isnan


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def create_account_message(user: User, data: FSMContext):
    '''Вспомогательная функция для создания сообщения'''
    if user.id in data['id_my_friends']:
        free_attempts_note = '<i><b>❗You have an unlimited 🎟️ forever</b></i>\n'
        text = f"🔐<b>Your personal account</b>\n\n👤<b>Username:</b> {user.full_name}\n🆔<b>ID:</b> {user.id}\n\n<b>Free 🎟️:</b> {free_attempts_note}\n\nYou can continue by clicking one of the buttons below"

        return text, True
    
    free_attempts_note = '<i><b>❗Free 5 attempts are restored on the first of every month</b></i>\n'

    if isnan(data['count_paid_attempts']):
        paid_attempts = "unlimited"
        added_text = f"\n<i><b>🗓️Unlimited plan end date:</b> {data['end_unlimited']}</i>"
        account_mode = True
    else:
        paid_attempts = data['count_paid_attempts']
        added_text = ""
        account_mode = False

    text = f"🔐<b>Your personal account</b>\n\n👤<b>Username:</b> {user.full_name}\n🆔<b>ID:</b> {user.id}\n\n<b>Free 🎟️:</b> {data['count_free_attempts']}\n{free_attempts_note}<b>Paid 🎟️:</b> {paid_attempts}{added_text}\n\nYou can continue by clicking one of the buttons below"

    return text, account_mode


async def show_account(update_type: Message | CallbackQuery, state: FSMContext):
    '''Вспомогательная функция для отображения сообщения'''
    data = await state.get_data()
    user = update_type.from_user

    text, mode = await create_account_message(user, data)

    if isinstance(update_type, CallbackQuery):
        send_func = update_type.message.edit_text
    else:
        await update_type.delete()
        send_func = update_type.answer

    await send_func(text, parse_mode='HTML', reply_markup=account(mode))

    if isinstance(update_type, CallbackQuery):
        await update_type.answer()
    
    logger.log_info(f"Пользователь {user.id} зашел в свой аккаунт")


@rtr.message(Command('account'))    # Команда для вызова профиля пользователя
async def my_account_message(message: Message, state: FSMContext):
    '''Функция для показа информации о пользователе'''
    await show_account(message, state)
    await state.set_state(amc.SolveFlasks.start_solving)
    

@rtr.callback_query(
    amc.SolveFlasks.pay_attempts,
    F.data == 'account'
)
@rtr.callback_query(
    amc.SolveFlasks.start_solving,
    F.data == 'account'
)
async def my_account_callback(callback: CallbackQuery, state: FSMContext):
    '''Функция для показа информации о пользователе'''
    await show_account(callback, state)
    current_state = await state.get_state()
    if current_state == amc.SolveFlasks.pay_attempts:
        await state.set_state(amc.SolveFlasks.start_solving)
