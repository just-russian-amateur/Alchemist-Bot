from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import account

from math import isnan


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.message(Command('account'))    # Команда для вызова профиля пользователя
async def my_account(message: Message, state: FSMContext):
    '''Функция для показа информации о пользователе'''
    all_users = await state.get_data()
    await message.delete()

    if not message.from_user.id in all_users['id_my_friends']:
        free_attempts_note = '<i><b>❗Free 5 attempts are restored on the first of every month</b></i>\n'
        if isnan(all_users['count_paid_attempts']):
            paid_attempts = "unlimited"
            added_text = f"\n<i><b>🗓️Unlimited plan end date:</b> {all_users['end_unlimited']}</i>"
        else:
            paid_attempts = all_users['count_paid_attempts']
            added_text = ""

        await message.answer(
            f"🔐<b>Your personal account</b>\n\n👤<b>Username:</b> {message.from_user.full_name}\n🆔<b>ID:</b> {message.from_user.id}\n\n<b>Free 🎟️:</b> {all_users['count_free_attempts']}\n{free_attempts_note}<b>Paid 🎟️:</b> {paid_attempts}{added_text}\n\nYou can continue by clicking one of the buttons below",
            parse_mode='HTML',
            reply_markup=account(False)
        )
    else:
        free_attempts_note = '<i><b>❗You have an unlimited 🎟️ forever</b></i>\n'
        await message.answer(
            f"🔐<b>Your personal account</b>\n\n👤<b>Username:</b> {message.from_user.full_name}\n🆔<b>ID:</b> {message.from_user.id}\n\n<b>Free 🎟️:</b> {free_attempts_note}\n\nYou can continue by clicking one of the buttons below",
            parse_mode='HTML',
            reply_markup=account(True)
        )
        
    await state.set_state(amc.SolveFlasks.start_solving)
    

@rtr.callback_query(
    amc.SolveFlasks.pay_attempts,
    F.data == 'account'
)
@rtr.callback_query(
    amc.SolveFlasks.start_solving,
    F.data == 'account'
)
async def my_account(callback: CallbackQuery, state: FSMContext):
    '''Функция для показа информации о пользователе'''
    attempts = await state.get_data()
    current_state = await state.get_state()

    if not callback.from_user.id in attempts['id_my_friends']:
        free_attempts_note = '<i><b>❗Free 5 attempts are restored on the first of every month</b></i>\n'
        if isnan(attempts['count_paid_attempts']):
            paid_attempts = "unlimited"
            added_text = f"\n<i><b>🗓️Unlimited plan end date:</b> {attempts['end_unlimited']}</i>"
        else:
            paid_attempts = attempts['count_paid_attempts']
            added_text = ""

        await callback.message.edit_text(
            f"🔐<b>Your personal account</b>\n\n👤<b>Username:</b> {callback.from_user.full_name}\n🆔<b>ID:</b> {callback.from_user.id}\n\n<b>Free 🎟️:</b> {attempts['count_free_attempts']}\n{free_attempts_note}<b>Paid 🎟️:</b> {paid_attempts}{added_text}\n\nYou can continue by clicking one of the buttons below",
            parse_mode='HTML',
            reply_markup=account(False)
        )
    else:
        free_attempts_note = '<i><b>❗You have an unlimited 🎟️ forever</b></i>\n'
        await callback.message.edit_text(
            f"🔐<b>Your personal account</b>\n\n👤<b>Username:</b> {callback.from_user.full_name}\n🆔<b>ID:</b> {callback.from_user.id}\n\n<b>Free 🎟️:</b> {free_attempts_note}\n\nYou can continue by clicking one of the buttons below",
            parse_mode='HTML',
            reply_markup=account(True)
        )
    if current_state == amc.SolveFlasks.pay_attempts:
        await state.set_state(amc.SolveFlasks.start_solving)
