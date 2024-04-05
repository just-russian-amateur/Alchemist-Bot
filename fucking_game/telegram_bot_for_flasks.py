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

from aiogram import Bot, Dispatcher, F  # Подключение библиотек
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, BufferedInputFile, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

from flasks import flasks_solver
from found_colors import found_colors_in_flasks, replace_in_json, create_image_for_replace, add_empty_flask, create_undef_buttons
import config

import asyncio
import logging
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
        one_time_keyboard=True,
        input_field_placeholder='Click on the button'
    )
    await message.answer(
        f"Hello, {message.from_user.first_name}!\nI am a bot that will help you pour liquid into flasks and, most importantly, do it correctly, in other words, I am your savior :)\nThere is nothing difficult in working with me, but if you are doing this for the first time, then click the help button on the right for instructions :)",
        reply_markup=keyboard_buttons
    )


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
        await message.answer(
            "So let's get started :)\nUpload the screenshot as an image, please",
            reply_markup=ReplyKeyboardRemove()
        )
        config.start_solve = True
    elif message.text == 'Upload new image':
        await message.answer(
            'Upload a new screenshot as an image, please',
            reply_markup=ReplyKeyboardRemove()
        )
        config.start_solve = True
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


@dp.message(F.text == 'Reload image')
@dp.message(F.text == 'Add an empty flask')
@dp.message(F.photo)
async def download_photoes(message:Message, bot: Bot):
    '''Функция получения и обработки фотографий'''
    if config.start_solve == True or config.reload_image == True:
        if config.reload_image == False:
            config.image_for_load = f'./images/{message.photo[-1].file_id}.jpg'   # Сохраняем на всякий случай путь к картинке
            await bot.download(
                message.photo[-1],
                destination=config.image_for_load
            )
            await message.answer("I'll try to recognize colors in the photo")
        
        # Распознаем цвета и добавляем их в список с последующей сериализации в json
        config.undefined_colors = found_colors_in_flasks(image_for_search=config.image_for_load, id=message.from_user.id)

        if len(config.undefined_colors) != 0:
            color_buttons_list = []
            # Создание списка кнопок с цветмаи, которыми можно будет заменить неопределенные значения
            for color in config.undefined_colors.keys():
                for _ in range(config.undefined_colors[color]):
                    if color == 'LIGHTGREEN':
                        color_buttons_list.append(KeyboardButton(text='LIGHT GREEN'))
                    elif color == 'LIGHTBLUE':
                        color_buttons_list.append(KeyboardButton(text='LIGHT BLUE'))
                    else:
                        color_buttons_list.append(KeyboardButton(text=color))
            color_buttons = create_undef_buttons(color_buttons_list)

            keyboard_buttons = ReplyKeyboardMarkup(
                keyboard=color_buttons,
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder='Choose a color'
            )

            if message.text == 'Add an empty flask':
                # Добавляем пустую колбу
                add_empty_flask(json_name=f"./tmp/start_level_{message.from_user.id}.json")

            # Подготавливаем картинку, в которой подсвечиваем неопределенные области
            create_image_for_replace(json_name=f"./tmp/start_level_{message.from_user.id}.json", id_client=message.from_user.id)

            feedback_button_set = [
                [
                    InlineKeyboardButton(text='Feedback to me', url=f"tg://user?id={984089348}")
                ]
            ]
            feedback_button = InlineKeyboardMarkup(inline_keyboard=feedback_button_set)

            # Изображение, где подсвечивается первый неопределенный цвет
            with open(f'./tmp/level_for_{message.from_user.id}.jpg', 'rb') as open_image:
                await message.answer_photo(
                    BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption="If I recognized some colors incorrectly, please give me feedback by clicking the button below the message (send a photo and describe the problem)",
                    reply_markup=feedback_button
                )
            await message.answer(
                'Please select from the options provided the color that should be in place of the green circle',
                reply_markup=keyboard_buttons
            )
            config.start_replace = True
        else:
            # Формируем итоговый json
            create_image_for_replace(json_name=f"./tmp/start_level_{message.from_user.id}.json", id_client=message.from_user.id)
            # Итоговое изображение
            with open(f'./tmp/level_for_{message.from_user.id}.jpg', 'rb') as open_image:
                await message.answer_photo(
                    BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption="I'll look for a solution from this position. Wait, this may take a while",
                    reply_markup=ReplyKeyboardRemove()
                )

            config.start_replace = False
            flasks_solver(input_file=f"./tmp/start_level_{message.from_user.id}.json", output_file=f"./tmp/result_level_{message.from_user.id}.txt")

            download_again = [
                [
                    KeyboardButton(text='Upload new image')
                ]
            ]
            download_buttons = ReplyKeyboardMarkup(
                keyboard=download_again,
                resize_keyboard=True,
                one_time_keyboard=True
            )

            errors = [
                [
                    KeyboardButton(text='Reload image'),
                    KeyboardButton(text='Add an empty flask'),
                    KeyboardButton(text='Upload new image')
                ]
            ]
            error_buttons = ReplyKeyboardMarkup(
                keyboard=errors,
                resize_keyboard=True,
                one_time_keyboard=True
            )

            if os.stat(f"./tmp/result_level_{message.from_user.id}.txt").st_size == 0:
                await message.answer(
                    f'Unfortunately, I was unable to find a solution for this arrangement.\nIf you want to change the order of undefined colors, click "Reload image".\nIf you know all the colors, but the solution still hasn’t been found, then I can add another empty flask, to do this, click “Add an empty flask”\nOr you can upload a new image, to do this, click "Upload new image"',
                    reply_markup=error_buttons
                )
                config.reload_image = True
            else:
                with open(f"./tmp/result_level_{message.from_user.id}.txt", "r") as result:
                    await message.answer(
                        f'I found a solution for you!\nPlease note that the flasks are numbered starting from 0, not 1!\n{result.read()}\nLet me know if you want a solution for another screenshot :)',
                        reply_markup=download_buttons
                    )
            # Удаление временных файлов
            os.remove(f"./tmp/result_level_{message.from_user.id}.txt")
            os.remove(f"./tmp/start_level_{message.from_user.id}.json")
            os.remove(f"./tmp/level_for_{message.from_user.id}.jpg")
    else:
        await message.answer('Click on the button below please :)')
    
    config.start_solve = False
    config.reload_image = False


@dp.message(F.text == "LIGHT BLUE")
@dp.message(F.text == "ORANGE")
@dp.message(F.text == "YELLOW")
@dp.message(F.text == "RED")
@dp.message(F.text == "LIGHT GREEN")
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
    if config.start_replace == True:
        if len(config.undefined_colors) != 0:
            for variation in config.color_variations:
                if message.text == variation:
                    if variation == 'LIGHT GREEN':
                        config.undefined_colors['LIGHTGREEN'] -= 1
                        if config.undefined_colors['LIGHTGREEN'] == 0:
                            config.undefined_colors.pop('LIGHTGREEN')
                        replace_in_json(json_name=f"./tmp/start_level_{message.from_user.id}.json", color_name='LIGHTGREEN')
                        break
                    elif variation == 'LIGHT BLUE':
                        config.undefined_colors['LIGHTBLUE'] -= 1
                        if config.undefined_colors['LIGHTBLUE'] == 0:
                            config.undefined_colors.pop('LIGHTBLUE')
                        replace_in_json(json_name=f"./tmp/start_level_{message.from_user.id}.json", color_name='LIGHTBLUE')
                        break
                    else:
                        config.undefined_colors[variation] -= 1
                        if config.undefined_colors[variation] == 0:
                            config.undefined_colors.pop(variation)
                        replace_in_json(json_name=f"./tmp/start_level_{message.from_user.id}.json", color_name=variation)
                        break
                
        if len(config.undefined_colors) == 0:
            # Формируем итоговый json
            create_image_for_replace(json_name=f"./tmp/start_level_{message.from_user.id}.json", id_client=message.from_user.id)
            # Итоговое изображение
            with open(f'./tmp/level_for_{message.from_user.id}.jpg', 'rb') as open_image:
                await message.answer_photo(
                    BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption="I'll look for a solution from this position. Wait, this may take a while",
                    reply_markup=ReplyKeyboardRemove()
                )

            config.start_replace = False
            flasks_solver(input_file=f"./tmp/start_level_{message.from_user.id}.json", output_file=f"./tmp/result_level_{message.from_user.id}.txt")

            download_again = [
                [
                    KeyboardButton(text='Upload new image')
                ]
            ]
            download_buttons = ReplyKeyboardMarkup(
                keyboard=download_again,
                resize_keyboard=True,
                one_time_keyboard=True
            )

            errors = [
                [
                    KeyboardButton(text='Reload image'),
                    KeyboardButton(text='Add an empty flask'),
                    KeyboardButton(text='Upload new image')
                ]
            ]
            error_buttons = ReplyKeyboardMarkup(
                keyboard=errors,
                resize_keyboard=True,
                one_time_keyboard=True
            )

            if os.stat(f"./tmp/result_level_{message.from_user.id}.txt").st_size == 0:
                await message.answer(
                    f'Unfortunately, I was unable to find a solution for this arrangement.\nIf you want to change the order of undefined colors, click "Reload image".\nIf you know all the colors, but the solution still hasn’t been found, then I can add another empty flask, to do this, click “Add an empty flask”\nOr you can upload a new image, to do this, click "Upload new image"',
                    reply_markup=error_buttons
                )
                config.reload_image = True
            else:
                with open(f"./tmp/result_level_{message.from_user.id}.txt", "r") as result:
                    await message.answer(
                        f'I found a solution for you!\nPlease note that the flasks are numbered starting from 0, not 1!\n{result.read()}\nLet me know if you want a solution for another screenshot :)',
                        reply_markup=download_buttons
                    )
            # Удаление временных файлов
            os.remove(f"./tmp/result_level_{message.from_user.id}.txt")
            os.remove(f"./tmp/start_level_{message.from_user.id}.json")
            os.remove(f"./tmp/level_for_{message.from_user.id}.jpg")
        else:
            color_buttons_list = []
            # Создание списка кнопок с цветмаи, которыми можно будет заменить неопределенные значения
            for color in config.undefined_colors.keys():
                for _ in range(config.undefined_colors[color]):
                    if color == 'LIGHTGREEN':
                        color_buttons_list.append(KeyboardButton(text='LIGHT GREEN'))
                    elif color == 'LIGHTBLUE':
                        color_buttons_list.append(KeyboardButton(text='LIGHT BLUE'))
                    else:
                        color_buttons_list.append(KeyboardButton(text=color))
            color_buttons = create_undef_buttons(color_buttons_list)

            keyboard_buttons = ReplyKeyboardMarkup(
                keyboard=color_buttons,
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder='Choose a color'
            )

            # Подготавливаем картинку, в которой подсвечиваем неопределенные области
            create_image_for_replace(json_name=f"./tmp/start_level_{message.from_user.id}.json", id_client=message.from_user.id)

            await message.answer(
                "Please fill in the next one",
                reply_markup=keyboard_buttons
            )
            # Изображение, где подсвечивается первый неопределенный цвет
            with open(f'./tmp/level_for_{message.from_user.id}.jpg', 'rb') as open_image:
                await message.answer_photo(
                    BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption="Please select from the options provided the color that should be in place of the green circle",
                    reply_markup=keyboard_buttons
                )
    else:
        await message.answer('Click on the button below please :)')


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
