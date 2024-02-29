"""
Done! Congratulations on your new bot. You will find it at t.me/flasks_solver_bot.
You can now add a description, about section and profile picture for your bot, see
/help for a list of commands. By the way, when you've finished creating your cool bot,
ping our Bot Support if you want a better username for it. Just make sure the bot is
fully operational before you do this.

Use this token to access the HTTP API:
6987578051:AAG4TCXhhdMG1xSX2AjRJqu7Pqp4krpit_8
Keep your token secure and store it safely, it can be used by anyone to control your bot.

For a description of the Bot API, see this page: https://core.telegram.org/bots/api
"""

from aiogram import Bot, Dispatcher, Router, F  # Подключение библиотек
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, FSInputFile, BufferedInputFile

import asyncio
import logging
import sys
import os


API_TOKEN = '6987578051:AAG4TCXhhdMG1xSX2AjRJqu7Pqp4krpit_8'  # Токен для работы с API
"""Инициализация диспетчера"""
dp = Dispatcher()

"""
Список поддерживаемых команд (желательно все сделать в виде кнопок):
/start - начало работы с ботом
/help - вызов помощника с описанием команд
/resolve - команда для решения, если картинка не изменилась, но предыдущее решение не сработало
/download_picture - загрузка изображения с текущей расстановкой цветов в колбах
/mode - режим работы (обычные цвета/паттерн фигур)
Надеюсь будут добавлены:
/payment - покупка попыток участия, если бот станет популярен
/share - ссылка для распространения бота в различных социальных сетях
"""


@dp.message(CommandStart())  # Команда для начала работы с ботом
@dp.message(Command('finish'))
async def send_welcome(message: Message):
    """Приветственная функция"""
    start_button_set = [
        [
            KeyboardButton(text='Начало работы'),
            KeyboardButton(text='Помощь')
        ]
    ]
    keyboard_buttons = ReplyKeyboardMarkup(
        keyboard=start_button_set,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "Привет!\nЯ бот, который поможет тебе решить эти гребаные колбы какими бы сложными они ни были:)\nТут должны быть указаны допустимые команды и что делать\nВведи /finish, если хочешь закончить решение",
        reply_markup=keyboard_buttons
    )


@dp.message(F.text == 'Помощь')    #   Команда помощи
async def help(message: Message):
    """Функция помощи"""
    after_help_button_set = [
        [
            KeyboardButton(text='Выбор режима распознавания')
        ]
    ]
    keyboard_buttons = ReplyKeyboardMarkup(
        keyboard=after_help_button_set,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    if message.text == 'Помощь':
        await message.answer(
            'Тут будет текст помощника',
            reply_markup=keyboard_buttons
        )
    else:
        await message.answer('Введите любой из предложенных вариантов')


@dp.message(F.text == 'Начало работы')    #   Команды выбора режима распознавания
@dp.message(F.text == 'Выбор режима распознавания')
async def mode_menu(message: Message):
    """Функция выбора режима распознавания"""
    after_mode_button_set = [
        [
            KeyboardButton(text='Режим паттерна'),
            KeyboardButton(text='Классические цвета')
        ]
    ]
    keyboard_buttons = ReplyKeyboardMarkup(
        keyboard=after_mode_button_set,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    if message.text == 'Начало работы' or message.text == 'Выбор режима распознавание':
        await message.answer(
            'Выбери, пожалуйста режим распознавания',
            reply_markup=keyboard_buttons
        )
    else:
        await message.answer('Введите любой из предложенных вариантов')


@dp.message(F.text == 'Режим паттерна')    #   Команды загрузки изображения
@dp.message(F.text == 'Классические цвета')
async def mode(message: Message):
    """Функция загрузки изображения"""
    if message.text == 'Режим паттерна':
        await message.answer('Ты выбрал паттерн режим, я запомнил\nЗагрузи изображение как картинку, пожалуйства')
    elif message.text == 'Классические цвета':
        await message.answer('Ты выбрал классический режим, я запомнил\nЗагрузи изображение как картинку, пожалуйства',)
    else:
        await message.answer('Введите любой из предложенных вариантов, пожалуйста')


@dp.message(Command("resolve"))    #   Команда перерешения
async def resolve(message: Message):
    """Функция перерешивания"""
    await message.answer(message.text)


# @dp.message(Command("share"))    #   Команда поделиться
# async def share(message: Message):
#     """Функция для распространения"""
#     await message.answer(message.text)


# @dp.message(Command("payment"))    #   Команда покупки попыток
# async def payment(message: Message):
#     """Функция для покупки попыток"""
#     await message.answer(message.text)
    

@dp.message(F.photo)
async def download_photoes(message:Message, bot: Bot):
    '''Функция получения и обработки фотографий'''
    await bot.download(
        message.photo[-1],
        destination=f'./images/{message.photo[-1].file_id}.jpg'
    )
    await message.answer('Ты отправил фото, я понял')
    
    with open(f'./images/{message.photo[-1].file_id}.jpg', 'rb') as open_image:
        await message.answer_photo(
            BufferedInputFile(
                open_image.read(),
                filename='solve_flasks'
            ),
            caption='Я верно распознал цвета?'
        )
    
    agreement_buttons = [
        [
            KeyboardButton(text='Да'),
            KeyboardButton(text='Нет')
        ]
    ]
    agreement = ReplyKeyboardMarkup(
        keyboard=agreement_buttons,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer('Да или нет?', reply_markup=agreement)


@dp.message(F.text == "Да")
async def agreement(message: Message):
    await message.answer('Хорошо, я начинаю решать')


@dp.message(F.text == "Нет")
async def disagreement(message: Message):
    await message.answer('Ох, я лох, попробую еще раз')


async def main():
    """Главная функция с инициализацией бота"""
    bot = Bot(token=API_TOKEN)
    await dp.start_polling(bot)


if __name__ == '__main__':
    """Запуск, логгирование и прочие вещи"""
    asyncio.run(main())
