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

    if await config.redis.sismember(RedisKeys.FRIENDS, user_id):
        await state.update_data(**{
            RedisKeys.FREE_ATTEMPTS: nan,
            RedisKeys.PAID_ATTEMPTS: 0,
        })

    if not await config.redis.sismember(RedisKeys.USERS, user_id):

        if not await config.redis.sismember(RedisKeys.FRIENDS, user_id):
            await state.update_data(**{
                RedisKeys.FREE_ATTEMPTS: 5,
                RedisKeys.PAID_ATTEMPTS: 0,
            })
            
        await config.redis.sadd(RedisKeys.USERS, user_id)


@rtr.message(CommandStart())  # Команда для начала работы с ботом
async def send_welcome(message: Message,  state: FSMContext):
    """Приветственная функция"""
    
    await state.set_state(None)

    logger.log_info(f'Пользователем {message.from_user.id} был запущен или перезапущен бот')

    await check_user(message.from_user.id, state)

    if await config.redis.sismember(RedisKeys.FRIENDS, message.from_user.id):
        condition_text = SendWelcomeTexts.CONDITION_TEXT_FREE
    else:
        condition_text = SendWelcomeTexts.CONDITION_TEXT

    await message.answer(
        SendWelcomeTexts.START_MESSAGE.format(first_name=message.from_user.first_name, condition_text=condition_text),
        parse_mode='HTML',
        reply_markup=start_keyboard()
    )

    await state.set_state(amc.SolveFlasks.start_solving)
