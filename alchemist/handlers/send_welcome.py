from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from math import nan

import classes.all_my_classes as amc
import config
from keyboards.all_my_keyboards import start_keyboard
from texts.all_my_texts import SendWelcomeTexts
from texts.redis_keys import RedisKeys

rtr = Router()
logger = amc.ConfigLogger(__name__)


async def check_user(user_id: int, state: FSMContext):
    '''Функция для проверки наличия пользователя в списке'''

    if user_id in config.friends:
        await state.update_data(**{
            RedisKeys.FREE_ATTEMPTS: nan,
            RedisKeys.PAID_ATTEMPTS: 0,
        })

    if not user_id in config.users:

        if not user_id in config.friends:
            await state.update_data(**{
                RedisKeys.FREE_ATTEMPTS: 5,
                RedisKeys.PAID_ATTEMPTS: 0,
            })
            
        with open('id_users.txt', 'a') as id_users:
            id_users.write(f'{user_id}\n')


@rtr.message(CommandStart())  # Команда для начала работы с ботом
async def send_welcome(message: Message,  state: FSMContext):
    """Приветственная функция"""
    
    await state.set_state(None)

    logger.log_info(f'Пользователем {message.from_user.id} был запущен или перезапущен бот')

    await check_user(message.from_user.id, state)

    if message.from_user.id in config.friends:
        condition_text = SendWelcomeTexts.CONDITION_TEXT_FREE
    else:
        condition_text = SendWelcomeTexts.CONDITION_TEXT

    await message.answer(
        SendWelcomeTexts.START_MESSAGE.format(first_name=message.from_user.first_name, condition_text=condition_text),
        parse_mode='HTML',
        reply_markup=start_keyboard()
    )

    await state.set_state(amc.SolveFlasks.start_solving)
