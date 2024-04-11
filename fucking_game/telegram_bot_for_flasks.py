from aiogram import Bot, Dispatcher  # Подключение библиотек
from aiogram.types import BotCommand

from handlers import send_welcome, start_solving, get_photo, fill_undef_values
import config

import asyncio


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
    """Инициализация диспетчера"""
    dp = Dispatcher()
    bot = Bot(token=config.API_TOKEN)

    dp.startup.register(clue)
    dp.include_routers(send_welcome.rtr, start_solving.rtr, get_photo.rtr, fill_undef_values.rtr)
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    """Запуск"""
    asyncio.run(main())
