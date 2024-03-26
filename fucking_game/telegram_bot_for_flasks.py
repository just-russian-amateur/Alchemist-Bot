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
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile, BotCommand

import json
from flasks import flasks_solver
from found_colors import found_colors_in_flasks
import global_names

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
Надеюсь будут добавлены:
/payment - покупка попыток участия, если бот станет популярен
/share - ссылка для распространения бота в различных социальных сетях
"""


@dp.message(CommandStart())  # Команда для начала работы с ботом
async def send_welcome(message: Message):
    """Приветственная функция"""
    start_button_set = [
        [
            KeyboardButton(text='Начало работы'),
            KeyboardButton(text='Справка')
        ]
    ]
    keyboard_buttons = ReplyKeyboardMarkup(
        keyboard=start_button_set,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "Привет!\nЯ бот, который поможет тебе перелить жидкость в колбах и, что самое главное, сделать это правильно, иначе говоря, я - твой спаситель:)\nВ работе со мной нет ничего сложного, но если ты делаешь это впервые, то прочитай мою справу сначала, пожалуйста, там совсем немного букв:)",
        reply_markup=keyboard_buttons
    )


@dp.message(F.text == 'Справка')    #   Команда помощи
@dp.message(Command('help'))
async def help(message: Message):
    """Функция помощи"""
    after_help_button_set = [
        [
            KeyboardButton(text='Начало работы')
        ]
    ]
    keyboard_buttons = ReplyKeyboardMarkup(
        keyboard=after_help_button_set,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    if message.text == 'Справка' or Command('help'):
        await message.answer(
            'Добро пожаловать в короткую справку обо мне:)\nДля того, чтобы меня перезапустить ты можешь ввести команду /start.\nДля доступа к справке ты можешь использовать команду /help вместо кнопки.\n\nТеперь пару слов о функциональности:\n1. Когда ты загружаешь скриншот, то нужно загрузить его как картинку, а не как файл, то есть в чате со мной я должен увидеть твое сообщение как полноценную картинку в половину экрана:)\n2. Скриншот не нужно никак обрезать или сжимать, я сделаю это самостояетельно, так что просто пришли мне исходное изображение:)\nВот, собственно, и все, что я хотел тебе рассказать о себе, удачи!',
            reply_markup=keyboard_buttons
        )
    else:
        await message.answer('Нажми на кнопку ниже, пожалуйста :)')


@dp.message(F.text == 'Начало работы')    #   Команды выбора режима распознавания
@dp.message(F.text == 'Загрузить новое изображение')
async def solve(message: Message):
    """Функция загрузки изображения"""
    if message.text == 'Начало работы':
        await message.answer('Итак, давай приступим :)\nЗагрузи скриншот как картинку, пожалуйства')
        global_names.start_solve = True
    elif message.text == 'Загрузить новое изображение':
        await message.answer('Загрузи новый скриншот как картинку, пожалуйста')
        global_names.solve_again = True
    else:
        await message.answer('Нажми на кнопку ниже, пожалуйста :)')


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
    if global_names.start_solve == True or global_names.solve_again == True:
        await bot.download(
            message.photo[-1],
            destination=f'./images/{message.photo[-1].file_id}.jpg'
        )
        await message.answer('Попробую распознать фото')
        
        # Распознаем цвета и добавляем их в список для последующей сериализации в json
        found_colors_in_flasks(image_for_search=f'./images/{message.photo[-1].file_id}.jpg', id=global_names.id_client)
        # Нужно нарисовать ответную картинку по json, где будет видно расположение цветов

        with open(f'./images/{message.photo[-1].file_id}.jpg', 'rb') as open_image:
            await message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption='Я буду использовать эту начальную позицию в решении'
            )
        
        flasks_solver(filename=f"./levels/this_level_{global_names.id_client}.json", id=global_names.id_client)

        download_again = [
            [
                KeyboardButton(text='Загрузить новое изображение')
            ]
        ]
        keyboard_buttons = ReplyKeyboardMarkup(
            keyboard=download_again,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        await message.answer(
            'Я нашел решение для тебя! Дай мне знать, если ты хочешь найти решение для другого скриншота:)',
            reply_markup=keyboard_buttons
        )
    else:
        await message.answer('Нажми на кнопку ниже, пожалуйста:)')
    
    global_names.start_solve = False
    global_names.solve_again = False


async def clue(bot: Bot):
    bot_commands = [
        BotCommand(command='/start', description='Перезапустить бота'),
        BotCommand(command='/help', description='Вызвать справку по работе с ботом')
    ]
    await bot.set_my_commands(bot_commands)


async def main():
    """Главная функция с инициализацией бота"""
    bot = Bot(token=API_TOKEN)
    dp.startup.register(clue)
    await dp.start_polling(bot)


if __name__ == '__main__':
    """Запуск, логгирование и прочие вещи"""
    asyncio.run(main())
