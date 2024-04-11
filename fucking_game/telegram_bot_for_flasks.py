from aiogram import Bot, Dispatcher  # Подключение библиотек
from aiogram.types import BotCommand
from aiogram.exceptions import TelegramNetworkError

from handlers import send_welcome, start_solving, get_photo, fill_undef_values
import config
import classes.all_my_classes as amc

import asyncio
import shutil
import os


"""
Список поддерживаемых команд (желательно все сделать в виде кнопок):
/start - начало работы с ботом
Надеюсь будут добавлены:
/payment - покупка попыток участия, если бот станет популярен
/share - ссылка для распространения бота в различных социальных сетях
"""


# @dp.message(Command("share"))    #   Команда поделиться
# async def share(message: Message):
#     """Функция для распространения"""
#     await message.answer(F.data)


# @dp.message(Command("payment"))    #   Команда покупки попыток
# async def payment(message: Message):
#     """Функция для покупки попыток"""
#     await message.answer(F.data)


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
    # Создание папки для логов
    if not os.path.isdir('./logs'):
        os.mkdir('./logs')

    logger = amc.ConfigLogger(__name__)
    # Определяем количество свободного пространства на диске в Гб
    if os.name == 'nt':
        free_space = shutil.disk_usage('C:/').free / 10**9
    elif os.name == 'posix':
        free_space = shutil.disk_usage('/dev/sda').free / 10**9

    # Логгируем предупреждение, если свободного места меньше 5 Гб
    if free_space < 5:
        logger.log_warning(f'Заканчивается свободное место на диске, осталось свободно: {free_space} Гб')

    # Инициализация диспетчера
    dp = Dispatcher()
    bot = Bot(token=config.API_TOKEN)

    dp.startup.register(clue)
    dp.include_routers(send_welcome.rtr, start_solving.rtr, get_photo.rtr, fill_undef_values.rtr)
    
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except TelegramNetworkError:
        logger.log_error('Ошибка подключения клиента к API')


if __name__ == '__main__':
    """Запуск"""
    asyncio.run(main())
