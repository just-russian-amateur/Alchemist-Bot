from aiogram import Bot, Dispatcher  # Подключение библиотек
from aiogram.types import BotCommand
from aiogram.exceptions import TelegramNetworkError
from aiogram.fsm.storage.redis import RedisStorage

from redis import asyncio as aioredis

from handlers import send_welcome, start_solving, fill_undefined_colors, get_image
import config
import classes.all_my_classes as amc

import asyncio
import shutil
import os


async def clue(bot: Bot):
    # Реализация меню команд
    bot_commands = [
        BotCommand(command='/start', description='Restarting me and receiving instructions for working with me')
    ]
    await bot.set_my_commands(bot_commands)
    # Реализация описания бота
    await bot.set_my_description("Hello, I'm the Alchemist!🧪🧑‍🔬🧪🧑‍🔬🧪🧑‍🔬\nI can help you transfer the different colored liquids into your flasks so that you get flasks with liquids filtered by color.\nI can work with pictures so you don't have to fill the flasks completely by hand, and I can also change the level a little by adding an empty flask if your level cannot be solved with two empty flasks😊")
    await bot.set_my_short_description("Alchemist - telegram bot for solving your levels for games with transfusion of colored liquids")


async def main():
    """Главная функция с инициализацией бота"""
    # Определяем количество свободного пространства на диске в Гб
    if os.name == 'nt':
        free_space = shutil.disk_usage('C:/').free / 10**9
    elif os.name == 'posix':
        free_space = shutil.disk_usage('/dev/sda').free / 10**9

    logger = amc.ConfigLogger(__name__)
    # Логгируем предупреждение, если свободного места меньше 5 Гб
    if free_space < 5:
        logger.log_warning(f'Заканчивается свободное место на диске, осталось свободно: {free_space} Гб')

    # Объявляем хранилище Redis
    redis = aioredis.Redis()

    # Инициализация диспетчера
    dp = Dispatcher(storage=RedisStorage(redis=redis))
    bot = Bot(token=config.API_TOKEN)

    dp.startup.register(clue)
    dp.include_routers(send_welcome.rtr, start_solving.rtr, get_image.rtr, fill_undefined_colors.rtr)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except TelegramNetworkError:
        logger.log_error('Ошибка подключения клиента к API')


if __name__ == '__main__':
    """Запуск"""
    asyncio.run(main())
