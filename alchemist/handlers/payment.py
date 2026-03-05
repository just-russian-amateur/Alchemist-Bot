from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, LabeledPrice, PreCheckoutQuery
from aiogram.fsm.context import FSMContext

from math import nan, isnan

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import payment_kb, continue_solving
from config import scheduler, redis
from texts.all_my_texts import PaymentTexts, KeyboardTexts, LabelsForPrices
from texts.redis_keys import RedisKeys
from callbacks.all_my_callbacks import CallbacksData

import asyncio
from datetime import datetime, timedelta
from pytz import utc
import json
import uuid


rtr = Router()
logger = amc.ConfigLogger(__name__)


# Словарь со всеми необходимыми для формирования цены данными
PACKAGES_INFO = {
    CallbacksData.ATTEMPTS_5: {
        "price_label": LabelsForPrices.SMALL_PACK,
        "payment_text": PaymentTexts.BUY_5_ATTEMPTS,
        "keyboard_text": KeyboardTexts.PAY_50,
        "count_attempts": 5,
        "amount": 50
    },
    CallbacksData.ATTEMPTS_12: {
        "price_label": LabelsForPrices.MIDDLE_PACK,
        "payment_text": PaymentTexts.BUY_12_ATTEMPTS,
        "keyboard_text": KeyboardTexts.PAY_100,
        "count_attempts": 12,
        "amount": 100
    },
    CallbacksData.ATTEMPTS_20: {
        "price_label": LabelsForPrices.BIG_PACK,
        "payment_text": PaymentTexts.BUY_20_ATTEMPTS,
        "keyboard_text": KeyboardTexts.PAY_150,
        "count_attempts": 20,
        "amount": 150
    },
    CallbacksData.ATTEMPTS_UNLIM: {
        "price_label": LabelsForPrices.UNLIM_PACK,
        "payment_text": PaymentTexts.BUY_UNLIM_ATTEMPTS,
        "keyboard_text": KeyboardTexts.PAY_350,
        "count_attempts": nan,
        "amount": 350
    }
}


async def reset_unlimited_attempts(user_id: int):
    '''Функция сброса безлимита'''

    # Пропускаем пользователей из списка друзей
    key = f"fsm:{user_id}:{user_id}:data"

    # Получаем строку с переменными для пользователя
    value = await redis.get(key)

    if value:

        try:
            # Парсим строку на отдельные параметры и сбрасываем безлимит
            data = json.loads(value)
            data[RedisKeys.PAID_ATTEMPTS] = 0

            await redis.set(key, json.dumps(data))

            logger.log_info(f'Безлимит для пользователя {user_id} обнулен')
        except:
            logger.log_error(f'Ошибка при обнулении безлимита для пользователя {user_id}')


@rtr.callback_query(
    amc.SolveFlasks.pay_attempts,
    F.data.in_(
        [
            CallbacksData.ATTEMPTS_5, CallbacksData.ATTEMPTS_12, CallbacksData.ATTEMPTS_20,
            CallbacksData.ATTEMPTS_UNLIM, CallbacksData.CANCEL, CallbacksData.OK, CallbacksData.CONTINUE
        ]
    )
)
async def payment(callback: CallbackQuery, state: FSMContext):
    """Функция для покупки попыток"""

    if callback.data in [CallbacksData.CANCEL, CallbacksData.OK, CallbacksData.CONTINUE]:

        logger.log_info(f'Пользователь {callback.from_user.id} отменил покупку')

        await callback.message.delete()
        await callback.answer()

        return

    package = PACKAGES_INFO.get(callback.data)
    price = [LabeledPrice(label=package["price_label"], amount=package["amount"])]
    # Генерация уникального payload для пользователя
    payload = str(uuid.uuid4())
    
    await state.update_data(add_attempts=package["count_attempts"])

    # Данные о процессе оплаты
    payment_data = {
        "user_id": callback.from_user.id,
        "package": callback.data,
        "amount": package["amount"],
        "status": "pending"
    }

    # Сохраняем данные о процессе оплаты в Redis на 1 час
    await redis.set(f'payment:{payload}', json.dumps(payment_data), ex=3600)
    
    await callback.message.answer_invoice(
        title='Payment attempts',
        description=package["payment_text"],
        payload=payload,
        provider_token='',
        currency='XTR',
        prices=price,
        start_parameter='buy_attempts',
        reply_markup=payment_kb(package["keyboard_text"])
    )

    await callback.answer()


@rtr.pre_checkout_query()
async def pre_checkout(checkout: PreCheckoutQuery):
    '''Предобработка платежа'''

    # Сверяем уникальный payload транзакции
    payload_data = await redis.get(f'payment:{checkout.invoice_payload}')

    if not payload_data:
        await checkout.answer(ok=False)
        return
    
    # Проверяем соответствие стоимости покупки
    payment_data = json.loads(payload_data)

    if payment_data["amount"] != checkout.total_amount:
        await checkout.answer(ok=False)
        return
    
    if payment_data["user_id"] != checkout.from_user.id:
        await checkout.answer(ok=False)
        return
        
    await checkout.answer(ok=True)


@rtr.message(F.successful_payment)
async def succesful_payment(message: Message, state: FSMContext):
    '''Безопасная обработка успешного платежа'''

    payload = message.successful_payment.invoice_payload
    amount = message.successful_payment.total_amount

    # Сверяем уникальный payload транзакции
    payload_data = await redis.get(f'payment:{payload}')

    if not payload_data:
        logger.log_error(f"Payload {payload} для транзакции не соответствует invoice пользователя {message.from_user.id}")

        return
    
    payment_data = json.loads(payload_data)

    # Проверяем статус транзакции
    if payment_data["status"] != "pending":
        logger.log_error(f"Оплата уже была проведена пользователем {message.from_user.id}")

        return
    
    # Проверяем соответствие покупателя и плательщика
    if payment_data["user_id"] != message.from_user.id:
        logger.log_error(f"ID пользователя чата {message.from_user.id} и ID в деталях транзакции {payment_data['user_id']} не совпадают")

        return
    
    # Проверяем соответствие стоимостей
    if payment_data["amount"] != amount:
        logger.log_error(f"В транзакции для {message.from_user.id} указана неверная сумма")

        return
    
    # Получаем количкество попыток, которое надо добавить пользователю
    package = PACKAGES_INFO.get(payment_data["package"])

    if not package:
        logger.log_error(f"Пользователь {message.from_user.id} оплачивает некорректную позицию")

        return

    # Помечаем платеж как завершенный
    payment_data["status"] = "completed"

    await redis.set(f"payment:{payload}", json.dumps(payment_data), ex=86400)

    user_data = await state.get_data()
    paid_attempts = user_data[RedisKeys.PAID_ATTEMPTS]
    add_attempts = package["count_attempts"]

    if isnan(add_attempts):
        paid_attempts = nan
        # Добавляем расписание с бесконечным количеством попыток на 30 дней
        now = datetime.now(tz=utc)
        run_date = now + timedelta(days=30)

        scheduler.add_job(reset_unlimited_attempts, 'date', run_date=run_date, args=(message.from_user.id,), misfire_grace_time=300)

        await state.update_data(end_unlimited=run_date.isoformat(" ", "minutes"))

        text = PaymentTexts.SUCCESSFUL_UNLIM

    else:
        paid_attempts += add_attempts
        text = PaymentTexts.SUCCESSFUL_PAYMENT.format(paid_attempts=paid_attempts)

    await state.update_data(count_paid_attempts=paid_attempts)

    await message.answer(
        text=text,
        reply_markup=continue_solving()
    )

    logger.log_info(f'Пользователь {message.from_user.id} купил {add_attempts} дополнительных попыток')

    await state.set_state(amc.SolveFlasks.start_solving)


@rtr.message(amc.SolveFlasks.pay_attempts)
async def unfinished_payment(message: Message):
    '''Функция для отслеживания любых действий кроме оплаты'''

    logger.log_info(f'Пользователь {message.from_user.id} проигнорировал оплату')

    msg = await message.answer(PaymentTexts.OUT_ATTEMPTS)
    
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()
    