from aiogram import Router, F  # Подключение библиотек
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext

from math import nan, isnan

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import payment_kb, continue_solving
from config import scheduler, redis

import asyncio
from datetime import datetime, timedelta
from pytz import utc
import json


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def reset_unlimited_attempts(user_id: int):
    '''Функция сброса безлимита'''
    # Пропускаем пользователей из списка друзей
    key = f"fsm:{user_id}:{user_id}:data"
    target_user = int(key.split(':')[1])

    # Получаем строку с переменными для пользователя
    value = await redis.get(key)
    if value:
        try:
            # Парсим строку на отдельные параметры и сбрасываем безлимит
            data = json.loads(value)
            data['count_paid_attempts'] = 0
            await redis.set(key, json.dumps(data))
            logger.log_info(f'Безлимит для пользователя {target_user} обнулен')
        except:
            logger.log_error(f'Ошибка при обнулении безлимита для пользователя {target_user}')


@rtr.callback_query(
    amc.SolveFlasks.pay_attempts,
    F.data.in_(
        [
            '5_attempts', '12_attempts', '20_attempts', 'unlimited_attempts', 'cancel', 'ok', 'continue'
        ]
    )
)
async def payment(callback: CallbackQuery, state: FSMContext):
    """Функция для покупки попыток"""
    if callback.data in ['cancel', 'ok', 'continue']:
        logger.log_info(f'Пользователь {callback.from_user.id} отменил покупку')
        await callback.message.delete()
        await callback.answer()
        return
    
    Prices = [
        [
            LabeledPrice(label='5 attempts', amount=50)
        ],
        [
            LabeledPrice(label='12 attempts', amount=100)
        ],
        [
            LabeledPrice(label='20 attempts', amount=150)
        ],
        [
            LabeledPrice(label='Unlimited attempts', amount=350)
        ]
    ]
    
    if callback.data == '5_attempts':
        attempts_info = ('Please pay for 5🎟️', Prices[0], '💰Pay 50⭐')
        await state.update_data(add_attempts=5)
    elif callback.data == '12_attempts':
        attempts_info = ('Please pay for 12🎟️', Prices[1], '💰Pay 100⭐')
        await state.update_data(add_attempts=12)
    elif callback.data == '20_attempts':
        attempts_info = ('Please pay for 20🎟️', Prices[2], '💰Pay 150⭐')
        await state.update_data(add_attempts=20)
    elif callback.data == 'unlimited_attempts':
        attempts_info = ('Please pay for unlimited 🎟️ (unlimited is available within 30 days from the date of payment)', Prices[3], '💰Pay 350⭐')
        await state.update_data(add_attempts=nan)
    
    await callback.message.answer_invoice(
        title='Payment attempts',
        description=attempts_info[0],
        payload='example',
        provider_token='',
        currency='XTR',
        prices=attempts_info[1],
        start_parameter='buy_attempts_example',
        reply_markup=payment_kb(attempts_info[2])
    )
    await callback.answer()


@rtr.pre_checkout_query()
async def pre_checkout(checkout: PreCheckoutQuery):
    '''Предобработка платежа'''
    await checkout.answer(ok=True)


@rtr.message(F.successful_payment)
async def succesful_payment(message: Message, state: FSMContext):
    attemptes = await state.get_data()
    add_attempts = attemptes['add_attempts']
    paid_attempts = attemptes['count_paid_attempts']
    if isnan(add_attempts):
        paid_attempts = nan
        # Добавляем расписание с бесконечным количеством попыток на 30 дней
        now = datetime.now(tz=utc)
        run_date = now + timedelta(days=30)

        scheduler.add_job(reset_unlimited_attempts, 'date', run_date=run_date, args=(message.from_user.id,), misfire_grace_time=300)
        await state.update_data(end_unlimited=run_date.isoformat(" ", "minutes"))
    else:
        paid_attempts += add_attempts
    await state.update_data(count_paid_attempts=paid_attempts)
    attemptes = await state.get_data()
    paid_attempts = attemptes['count_paid_attempts']
    if isnan(paid_attempts):
        await message.answer(
            f'Payment was successful, you now have unlimited 🎟️.\nClick the button below if you want to start or continue the solution',
            reply_markup=continue_solving()
        )
    else:
        await message.answer(
            f'Payment was successful, you now have {paid_attempts} purchased 🎟️.\nClick the button below if you want to start or continue the solution',
            reply_markup=continue_solving()
        )
    logger.log_info(f'Пользователь {message.from_user.id} купил {add_attempts} дополнительных попыток')
    await state.set_state(amc.SolveFlasks.start_solving)


@rtr.message(amc.SolveFlasks.pay_attempts)
async def filling_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме оплаты'''
    logger.log_info(f'Пользователь {message.from_user.id} проигнорировал оплату')
    msg = await message.answer("Sorry, you've run out of attempts😞\nIf you want to continue now, you can buy multiple attempts for a small fee")
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()
    