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
from found_colors import found_colors_in_flasks, replace_in_json
import config

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
            KeyboardButton(text='Start solving'),
            KeyboardButton(text='Help')
        ]
    ]
    keyboard_buttons = ReplyKeyboardMarkup(
        keyboard=start_button_set,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer(
        "Hello!\nI am a bot that will help you pour liquid into flasks and, most importantly, do it correctly, in other words, I am your savior :)\nThere is nothing difficult in working with me, but if you are doing this for the first time, then click the help button on the right for instructions :)",
        reply_markup=keyboard_buttons
    )

    config.id_client = message.from_user.id


@dp.message(F.text == 'Help')    #   Команда помощи
@dp.message(Command('help'))
async def help(message: Message):
    """Функция помощи"""
    after_help_button_set = [
        [
            KeyboardButton(text='Start solving')
        ]
    ]
    keyboard_buttons = ReplyKeyboardMarkup(
        keyboard=after_help_button_set,
        resize_keyboard=True,
        one_time_keyboard=True
    )
    if message.text == 'Help' or Command('help'):
        await message.answer(
            "Welcome to a short passage of information about me :)\nIn order to restart me, you can enter the /start command.\nTo access help, you can use the /help command instead of the button.\n\nNow a few words about functionality:\n\t1. When you upload a screenshot, you need to upload it as a picture, not as a file, that is, in a chat with me, I should see your message as a full-fledged picture in half the screen :)\n\t2. The screenshot does not need to be cropped or compressed in any way, I will do it myself, so just send me the original image :)\n\t3. Upload for me an image with the initial position of the colors in the flasks (that is, 2 empty flasks and the remaining flasks are completely filled), this is the only way I can find a solution :)\nThat's basically all I wanted to tell you about myself, good luck!",
            reply_markup=keyboard_buttons
        )
    else:
        await message.answer('Click on the button below please :)')


@dp.message(F.text == 'Start solving')    #   Команды выбора режима распознавания
@dp.message(F.text == 'Upload new image')
async def solve(message: Message):
    """Функция загрузки изображения"""
    if message.text == 'Start solving':
        await message.answer("So let's get started :)\nUpload the screenshot as an image, please")
        config.start_solve = True
    elif message.text == 'Upload new image':
        await message.answer('Upload a new screenshot as an image, please')
        config.solve_again = True
    else:
        await message.answer('Click on the button below please :)')


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
    if config.start_solve == True or config.solve_again == True:
        await bot.download(
            message.photo[-1],
            destination=f'./images/{message.photo[-1].file_id}.jpg'
        )
        await message.answer("I'll try to recognize colors in the photo")
        
        # Распознаем цвета и добавляем их в список с последующей сериализации в json
        config.undefined_colors = found_colors_in_flasks(image_for_search=f'./images/{message.photo[-1].file_id}.jpg', id=config.id_client)
        # Нужно нарисовать ответную картинку по json, где будет видно расположение цветов (вместо копирования этого же изображения)
        # with open(f'./images/{message.photo[-1].file_id}.jpg', 'rb') as open_image:
        #     await message.answer_photo(
        #         BufferedInputFile(
        #             open_image.read(),
        #             filename='solve_flasks'
        #         ),
        #         caption="I'll use this starting position in the solution\nPlease fill in the missing colors manually"
        #     )

        color_buttons = []
        for color in config.undefined_colors.keys():
            button_line = []
            for _ in range(config.undefined_colors[color]):
                if color == 'LIGHTLIGHT':
                    button_line.append(KeyboardButton(text='LIGHT LIGHT'))
                elif color == 'LIGHTBLUE':
                    button_line.append(KeyboardButton(text='LIGHT BLUE'))
                else:
                    button_line.append(KeyboardButton(text=color))
            color_buttons.append(button_line)

        keyboard_buttons = ReplyKeyboardMarkup(
            keyboard=color_buttons,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        # Изображение, где подсвечивается первый неопределенный цвет
        with open(f'./images/{message.photo[-1].file_id}.jpg', 'rb') as open_image:
            await message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption="Please choose from the suggested options the color that you think should be here",
                reply_markup=keyboard_buttons
            )
    else:
        await message.answer('Click on the button below please :)')
    
    config.start_solve = False
    config.solve_again = False


@dp.message(F.text == "LIGHT BLUE")
@dp.message(F.text == "ORANGE")
@dp.message(F.text == "YELLOW")
@dp.message(F.text == "RED")
@dp.message(F.text == "LIGHT LIGHT")
@dp.message(F.text == "BLUE")
@dp.message(F.text == "BURGUNDY")
@dp.message(F.text == "GREEN")
@dp.message(F.text == "PINK")
@dp.message(F.text == "CRIMSON")
@dp.message(F.text == "CREAM")
@dp.message(F.text == "PURPLE")
@dp.message(F.text == "GRAY")
@dp.message(F.text == "LILAC")
async def fill(message:Message):
    '''Функция дозаполнения неопределенных цветов вручную'''
    if len(config.undefined_colors) != 0:
        for variation in config.color_variations:
            if message.text == variation:
                if variation == 'LIGHT LIGHT':
                    config.undefined_colors['LIGHTLIGHT'] -= 1
                    if config.undefined_colors['LIGHTLIGHT'] == 0:
                        config.undefined_colors.pop('LIGHTLIGHT')
                    replace_in_json(json_name=f"./levels/start_level_{config.id_client}.json", color_name='LIGHTLIGHT')
                    break
                elif variation == 'LIGHT BLUE':
                    config.undefined_colors['LIGHTBLUE'] -= 1
                    if config.undefined_colors['LIGHTBLUE'] == 0:
                        config.undefined_colors.pop('LIGHTBLUE')
                    replace_in_json(json_name=f"./levels/start_level_{config.id_client}.json", color_name='LIGHTLIGHT')
                    break
                else:
                    config.undefined_colors[variation] -= 1
                    if config.undefined_colors[variation] == 0:
                        config.undefined_colors.pop(variation)
                    replace_in_json(json_name=f"./levels/start_level_{config.id_client}.json", color_name=variation)
                    break
            
    if len(config.undefined_colors) == 0:
        flasks_solver(input_file=f"./levels/start_level_{config.id_client}.json", output_file=f"./levels/result_level_{config.id_client}.txt")

        download_again = [
            [
                KeyboardButton(text='Upload new image')
            ]
        ]
        keyboard_buttons = ReplyKeyboardMarkup(
            keyboard=download_again,
            resize_keyboard=True,
            one_time_keyboard=True
        )

        with open(f"./levels/result_level_{config.id_client}.txt", "r") as result:
            await message.answer(
                f'I found a solution for you!\n{result.read()}\nLet me know if you want a solution for another screenshot :)',
                reply_markup=keyboard_buttons
            )
        os.remove(f"./levels/result_level_{config.id_client}.txt")
    else:
        color_buttons = []
        for color in config.undefined_colors.keys():
            button_line = []
            for _ in range(config.undefined_colors[color]):
                if color == 'LIGHTLIGHT':
                    button_line.append(KeyboardButton(text='LIGHT LIGHT'))
                elif color == 'LIGHTBLUE':
                    button_line.append(KeyboardButton(text='LIGHT BLUE'))
                else:
                    button_line.append(KeyboardButton(text=color))
            color_buttons.append(button_line)

        keyboard_buttons = ReplyKeyboardMarkup(
            keyboard=color_buttons,
            resize_keyboard=True,
            one_time_keyboard=True
        )
        await message.answer(
            "Fill the next one",
            reply_markup=keyboard_buttons
        )

        # Изображение, где подсвечивается первый неопределенный цвет
        # with open(f'./images/{message.photo[-1].file_id}.jpg', 'rb') as open_image:
        #     await message.answer_photo(
        #         BufferedInputFile(
        #             open_image.read(),
        #             filename='solve_flasks'
        #         ),
        #         caption="Please choose from the suggested options the color that you think should be here",
        #         reply_markup=keyboard_buttons
        #     )


async def clue(bot: Bot):
    bot_commands = [
        BotCommand(command='/start', description='Restart bot'),
        BotCommand(command='/help', description='Call for help on working with the bot')
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
