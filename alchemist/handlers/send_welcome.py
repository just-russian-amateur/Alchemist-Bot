from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from math import nan

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import start_keyboard


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def check_user(user_id: int, state: FSMContext):
    '''Функция для проверки наличия пользователя в списке'''
    # Получаем списки id друзей и всех игроков
    with open('id_friends.txt', 'r') as id_friends:
        friends = list(int(friend.split('\n')[0]) for friend in id_friends.readlines())
    with open('id_users.txt', 'r') as id_users:
        users = list(int(user.split('\n')[0]) for user in id_users.readlines())
    await state.update_data(id_my_friends=friends)
    await state.update_data(id_users=users)
    if user_id in friends:
        await state.update_data(count_free_attempts=nan)
        await state.update_data(count_paid_attempts=0)
    if not user_id in users:
        if not user_id in friends:
            await state.update_data(count_free_attempts=5)
            await state.update_data(count_paid_attempts=0)
        with open('id_users.txt', 'a') as id_users:
            id_users.write(f'{user_id}\n')


@rtr.message(CommandStart())  # Команда для начала работы с ботом
async def send_welcome(message: Message,  state: FSMContext):
    """Приветственная функция"""
    await state.set_state(None)

    logger.log_info(f'Пользователем {message.from_user.id} был запущен или перезапущен бот')
    await check_user(message.from_user.id, state)
    all_users = await state.get_data()

    if message.from_user.id in all_users['id_my_friends']:
        await message.answer(
            f"Hello, <b>{message.from_user.first_name}</b>!😁\n\nIf this is your first time interacting with me, I strongly recommend that you read about some rules that you need to follow to work correctly by clicking the appropriate button below👇\nIf this is not the first time you have done this, then I just remind you that to restart me, you can enter the /start command.\n\nEvery month I will give you unlimited free 🎟️. You can see all the information in your account",
            parse_mode='HTML',
            reply_markup=start_keyboard()
        )
    else:
        await message.answer(
            f"Hello, <b>{message.from_user.first_name}</b>!😁\n\nIf this is your first time interacting with me, I strongly recommend that you read about some rules that you need to follow to work correctly by clicking the appropriate button below👇\nIf this is not the first time you have done this, then I just remind you that to restart me, you can enter the /start command.\n\nEvery month I will give you 5 free 🎟️, if they are not enough for you, you can buy more for a small fee. You can see all the information in your account",
            parse_mode='HTML',
            reply_markup=start_keyboard()
        )
    await state.set_state(amc.SolveFlasks.start_solving)
