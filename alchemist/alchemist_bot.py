from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.redis import RedisStorage

from redis.exceptions import WatchError

from handlers import send_welcome, start_solving, payment, fill_undefined_colors, get_image, terms, support, autofill, account, check_updates
import config
import classes.all_my_classes as amc
from texts.all_my_texts import KeyboardTexts, AlchemistBot
from texts.redis_keys import RedisKeys
from callbacks.all_my_callbacks import CallbacksData

import asyncio
import shutil
import json
import os


logger = amc.ConfigLogger(__name__)


async def update_redis_data(key: str, updater: callable) -> bool:
    '''Функция для безопасного обновления полей в Redis'''
    while True:
        # Цикл для безопасного обновления попыток для каждого игрока
        async with config.redis.pipeline() as pipe:

            try:
                await pipe.watch(key)
                # Получаем строку с переменными для пользователя
                value = await pipe.get(key)

                if not value:
                    return False
                
                # Парсим строку на отдельные параметры и восстанавливаем попытки
                data = json.loads(value)
                updater(data)

                pipe.multi()
                pipe.set(key, json.dumps(data))
                await pipe.execute()
                return True
            
            except WatchError:
                # Повторяем попытку обновления попыток в случае неудачи
                continue

            except Exception:
                # Обработка остальных ошибок
                return False


async def recovery_attempts():
    '''Функция для восстановления количества бесплатных попыток для всех пользователей сразу (кроме друзей)'''

    async for key in config.redis.scan_iter("fsm:*:*:data"):

        # Пропускаем пользователей из списка друзей
        user_id = int(key.decode().split(':')[1])

        if await config.redis.sismember(RedisKeys.FRIENDS, user_id):
            continue

        succes_update = await update_redis_data(key, lambda data: data.update({RedisKeys.FREE_ATTEMPTS.value: 5}))
        if succes_update:
            logger.log_info(f'Попытки для пользователя {user_id} восстановлены')
        else:
            logger.log_error(f'Ошибка при восстановлении попыток для пользователя {user_id}')


async def clue(bot: Bot):

    # Реализация меню команд
    bot_commands = [
        BotCommand(command=CallbacksData.CLUE_START, description=KeyboardTexts.CLUE_RESTART),
        BotCommand(command=CallbacksData.CLUE_ACCOUNT, description=KeyboardTexts.CLUE_ACCOUNT),
        BotCommand(command=CallbacksData.CLUE_TERMS, description=KeyboardTexts.CLUE_TERMS),
        BotCommand(command=CallbacksData.CLUE_SUPPORT, description=KeyboardTexts.CLUE_SUPPORT)
    ]

    await bot.set_my_commands(bot_commands)
    # Реализация описания бота
    await bot.set_my_description(AlchemistBot.FULL_DESCRIPTION)
    await bot.set_my_short_description(AlchemistBot.SHORT_DESCRITPION)


async def main():
    """Главная функция с инициализацией бота"""

    # Определяем количество свободного пространства на диске в Гб
    if os.name == 'nt':
        free_space = shutil.disk_usage('C:/').free / 10**9
    elif os.name == 'posix':
        free_space = shutil.disk_usage('/').free / 10**9

    # Создаем папку для хранения временных файлов
    if not os.path.isdir('./tmp'):
        os.mkdir('./tmp')

    # Логгируем предупреждение, если свободного места меньше 0.2 Гб
    if free_space < 0.2:
        logger.log_warning(f'Заканчивается свободное место на диске, осталось свободно: {free_space} Гб')

    # Инициализация диспетчера
    storage = RedisStorage(redis=config.redis)
    dp = Dispatcher(storage=storage)
    bot = Bot(token=config.API_TOKEN)

    # Добавляем задачу в расписание
    config.scheduler.add_job(recovery_attempts, 'cron', month='*', id='recovery_attempts', replace_existing=True, misfire_grace_time=300)
    
    dp.startup.register(clue)
    dp.include_routers(send_welcome.rtr, account.rtr, terms.rtr, support.rtr, start_solving.rtr, payment.rtr, get_image.rtr, autofill.rtr, fill_undefined_colors.rtr, check_updates.rtr)
    
    try:
        config.scheduler.start()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
        
    except TelegramNetworkError:
        logger.log_error('Ошибка подключения клиента к API')


if __name__ == '__main__':
    """Запуск"""
    asyncio.run(main())
