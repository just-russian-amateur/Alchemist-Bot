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
from aiogram.types import Message, CallbackQuery, BufferedInputFile, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup

from flasks import flasks_solver
from test_found import found_colors_in_flasks, replace_in_json, create_image_for_replace, add_empty_flask, create_undef_buttons
import config

import asyncio
import logging
import os


API_TOKEN = '6948846805:AAHrKoOrSqOJJF_CNtTDRworIKUPh2qOcjg'  # Токен для работы с API
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
            InlineKeyboardButton(text='🚀Start solving', callback_data='start_solving')
        ]
    ]
    keyboard_buttons = InlineKeyboardMarkup(inline_keyboard=start_button_set)

    await message.answer(
        f"Hello, {message.from_user.first_name}!😁\nNow I'll tell you a little more about myself so that you know how to interact with me correctly. This is very important, because if you follow these few simple rules, you will get more accurate recognition of the colors inside the flasks, as well as the correct solutions for your specific level\nNow a few words about the functionality:\n✔️When you upload a screenshot, you need to upload it as a picture, not as a file, that is, in a chat with me, I should see your message as a full-fledged picture, about half the screen\n✔️The screenshot does not need to be cropped or compressed in any way, I will do it myself, so just send me the original image\n✔️If you usually use pattern mode, please turn it off before taking a screenshot and sending it to me, I'm not good at recognizing shapes inside colored rectangles, so I won't be able to recognize your level accurately (maybe I'll learn this in the future!)\n✔️Upload me an image with the initial position of the colors in the flasks (that is, 2 empty flasks and the rest are completely filled), this is the only way I can find a solution\nThat's probably all the subtleties that I wanted to tell you about working with me, good luck!🤞🤞🤞\n\nTo restart me, you can enter the /start command.",
        reply_markup=keyboard_buttons
    )


@dp.callback_query(F.data.in_([
    'start_solving', 'upload_new_image'
]))    #   Команды выбора режима распознавания
async def solve(callback: CallbackQuery):
    """Функция загрузки изображения"""
    if callback.data == 'start_solving':
        await callback.message.answer("So let's get started😎\nUpload the screenshot as an image, please")
        await callback.answer()
    elif callback.data == 'upload_new_image':
        await callback.message.answer('Upload a new screenshot as an image, please')
        await callback.answer()
    else:
        await callback.message.answer('Click on the button please :)')


# @dp.message(Command("share"))    #   Команда поделиться
# async def share(message: Message):
#     """Функция для распространения"""
#     await message.answer(F.data)


# @dp.message(Command("payment"))    #   Команда покупки попыток
# async def payment(message: Message):
#     """Функция для покупки попыток"""
#     await message.answer(F.data)


@dp.message(F.photo)
async def get_photo(message: Message, bot: Bot):
    '''Функция получения и обработки фотографий'''
    config.image_for_load = f'./images/{message.photo[-1].file_id}.jpg'   # Сохраняем на всякий случай путь к картинке
    in_file, out_file = f"./tmp/start_level_{message.from_user.id}.json", f"./tmp/result_level_{message.from_user.id}.txt"
    level_file = f'./tmp/level_for_{message.from_user.id}.jpg'
    await bot.download(
        message.photo[-1],
        destination=config.image_for_load
    )
    await message.answer("I'll try to recognize colors in the photo😓😓😓")
    
    try:
        # Распознаем цвета и добавляем их в список с последующей сериализации в json
        config.undefined_colors = found_colors_in_flasks(image_for_search=config.image_for_load, id=message.from_user.id)
    except:
        reload_img = [
                [
                    InlineKeyboardButton(text='📩🖼️Upload new image', callback_data='upload_new_image')
                ]
            ]
        reload_button = InlineKeyboardMarkup(inline_keyboard=reload_img)
        await message.answer(
            'Something went wrong...🤷‍♂️ Please upload another picture',
            reply_markup=reload_button
        )

    if len(config.undefined_colors) != 0:
        color_buttons_list = []
        # Создание списка кнопок с цветмаи, которыми можно будет заменить неопределенные значения
        for color in config.undefined_colors.keys():
            for _ in range(config.undefined_colors[color]):
                if color == 'LIGHTGREEN':
                    color_buttons_list.append(InlineKeyboardButton(text='LIGHT GREEN', callback_data='LIGHT GREEN'))
                elif color == 'LIGHTBLUE':
                    color_buttons_list.append(InlineKeyboardButton(text='LIGHT BLUE', callback_data='LIGHT BLUE'))
                else:
                    color_buttons_list.append(InlineKeyboardButton(text=color, callback_data=color))
        color_buttons = create_undef_buttons(color_buttons_list)

        keyboard_buttons = InlineKeyboardMarkup(inline_keyboard=color_buttons)

        # Подготавливаем картинку, в которой подсвечиваем неопределенные области
        create_image_for_replace(json_name=in_file, id_client=message.from_user.id)

        feedback_button_set = [
            [
                InlineKeyboardButton(text='Feedback to me🙃', url=f"tg://user?id={984089348}")
            ]
        ]
        feedback_button = InlineKeyboardMarkup(inline_keyboard=feedback_button_set)

        # Изображение, где подсвечивается первый неопределенный цвет
        with open(level_file, 'rb') as open_image:
            await message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption="Please check if I recognized everything correctly? If I misrecognized some colors or you noticed some other error, then feel free to let me know about the problem\nTo do this, click the button below the message (send a photo with which the error occurred and describe the problem)🙂",
                reply_markup=feedback_button
            )
        await message.answer(
            'Please select from the options provided the color that should be in place of the green circle',
            reply_markup=keyboard_buttons
        )
    else:
        # Формируем итоговый json
        create_image_for_replace(json_name=in_file, id_client=message.from_user.id)
        # Итоговое изображение
        await message.delete()
        with open(level_file, 'rb') as open_image:
            await message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption="I'll look for a solution from this position. Wait, this may take a while"
            )

        flasks_solver(input_file=in_file, output_file=out_file)

        download_again = [
            [
                InlineKeyboardButton(text='📩🖼️Upload new image', callback_data='upload_new_image')
            ]
        ]
        download_buttons = InlineKeyboardMarkup(inline_keyboard=download_again)

        errors = [
            [
                InlineKeyboardButton(text='🔄️🖼️Reload image', callback_data='reload_image'),
                InlineKeyboardButton(text='➕🧪Add an empty flask', callback_data='add_an_empty_flask')
            ],
            [
                InlineKeyboardButton(text='Upload new image', callback_data='upload_new_image')
            ]
        ]
        error_buttons = InlineKeyboardMarkup(inline_keyboard=errors)

        if os.stat(out_file).st_size == 0 or os.path.isfile(out_file) == False:
            await message.answer(
                f"😖😖😖Unfortunately, I was unable to find a solution for this arrangement.\nIf you want to change the order of undefined colors, click 'Reload image'.\nIf you know all the colors, but the solution still hasn't been found, then I can add another empty flask, to do this, click 'Add an empty flask'\nOr you can upload a new image, to do this, click 'Upload new image'",
                reply_markup=error_buttons
            )
        else:
            with open(out_file, "r") as result:
                await message.answer(
                    f'Yay!🥳🥳🥳I found a solution for you!!!🥳🥳🥳\nPlease note that the flasks are numbered starting from 0, not 1!\n{result.read()}\nLet me know if you want a solution for another screenshot🙂',
                    reply_markup=download_buttons
                )
        # Удаление временных файлов
        os.remove(out_file)
        os.remove(in_file)
        os.remove(level_file)
    

@dp.callback_query(F.data.in_([
    "LIGHT BLUE", "ORANGE", "YELLOW", "RED", "LIGHT GREEN", "BLUE", "BURGUNDY",
    "GREEN", "PINK", "CRIMSON", "CREAM", "PURPLE", "GRAY","LILAC",
    'reload_image', 'add_an_empty_flask'
]))
async def fill_undef_values(callback: CallbackQuery):
    '''Функция дозаполнения неопределенных цветов вручную'''
    in_file, out_file = f"./tmp/start_level_{callback.from_user.id}.json", f"./tmp/result_level_{callback.from_user.id}.txt"
    level_file = f'./tmp/level_for_{callback.from_user.id}.jpg'

    if callback.data == 'reload_image' or callback.data == 'add_an_empty_flask':
        try:
            # Распознаем цвета и добавляем их в список с последующей сериализации в json
            config.undefined_colors = found_colors_in_flasks(image_for_search=config.image_for_load, id=callback.from_user.id)
        except:
            reload_img = [
                    [
                        InlineKeyboardButton(text='📩🖼️Upload new image', callback_data='upload_new_image')
                    ]
                ]
            reload_button = InlineKeyboardMarkup(inline_keyboard=reload_img)
            await callback.message.answer(
                'Something went wrong...🤷‍♂️ Please upload another picture',
                reply_markup=reload_button
            )
            await callback.answer()

    if callback.data != 'reload_image' and callback.data != 'add_an_empty_flask':
        if len(config.undefined_colors) != 0:
            for variation in config.color_variations:
                if callback.data == variation:
                    if variation == 'LIGHT GREEN':
                        config.undefined_colors['LIGHTGREEN'] -= 1
                        if config.undefined_colors['LIGHTGREEN'] == 0:
                            config.undefined_colors.pop('LIGHTGREEN')
                        replace_in_json(json_name=in_file, color_name='LIGHTGREEN')
                        break
                    elif variation == 'LIGHT BLUE':
                        config.undefined_colors['LIGHTBLUE'] -= 1
                        if config.undefined_colors['LIGHTBLUE'] == 0:
                            config.undefined_colors.pop('LIGHTBLUE')
                        replace_in_json(json_name=in_file, color_name='LIGHTBLUE')
                        break
                    else:
                        config.undefined_colors[variation] -= 1
                        if config.undefined_colors[variation] == 0:
                            config.undefined_colors.pop(variation)
                        replace_in_json(json_name=in_file, color_name=variation)
                        break

    if len(config.undefined_colors) != 0:
        color_buttons_list = []
        # Создание списка кнопок с цветмаи, которыми можно будет заменить неопределенные значения
        for color in config.undefined_colors.keys():
            for _ in range(config.undefined_colors[color]):
                if color == 'LIGHTGREEN':
                    color_buttons_list.append(InlineKeyboardButton(text='LIGHT GREEN', callback_data='LIGHT GREEN'))
                elif color == 'LIGHTBLUE':
                    color_buttons_list.append(InlineKeyboardButton(text='LIGHT BLUE', callback_data='LIGHT BLUE'))
                else:
                    color_buttons_list.append(InlineKeyboardButton(text=color, callback_data=color))
        color_buttons = create_undef_buttons(color_buttons_list)

        keyboard_buttons = InlineKeyboardMarkup(inline_keyboard=color_buttons)

        if callback.data == 'add_an_empty_flask':
            # Добавляем пустую колбу
            add_empty_flask(json_name=in_file)

        # Подготавливаем картинку, в которой подсвечиваем неопределенные области
        create_image_for_replace(json_name=in_file, id_client=callback.from_user.id)

        if callback.data == 'reload_image' or callback.data == 'add_an_empty_flask':
            feedback_button_set = [
                [
                    InlineKeyboardButton(text='Feedback to me🙃', url=f"tg://user?id={984089348}")
                ]
            ]
            feedback_button = InlineKeyboardMarkup(inline_keyboard=feedback_button_set)

            # Изображение, где подсвечивается первый неопределенный цвет
            with open(level_file, 'rb') as open_image:
                await callback.message.answer_photo(
                    BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption="Please check if I recognized everything correctly? If I misrecognized some colors or you noticed some other error, then feel free to let me know about the problem\nTo do this, click the button below the message (send a photo with which the error occurred and describe the problem)🙂",
                    reply_markup=feedback_button
                )
            await callback.message.answer(
                'Please select from the options provided the color that should be in place of the green circle',
                reply_markup=keyboard_buttons
            )
            await callback.answer()
        else:
            # Изображение, где подсвечивается первый неопределенный цвет
            await callback.message.delete()
            with open(level_file, 'rb') as open_image:
                await callback.message.answer_photo(
                    BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption="Please select from the options provided the color that should be in place of the green circle",
                    reply_markup=keyboard_buttons
                )
                await callback.answer()
    else:
        # Формируем итоговый json
        create_image_for_replace(json_name=in_file, id_client=callback.from_user.id)
        # Итоговое изображение
        await callback.message.delete()
        with open(level_file, 'rb') as open_image:
            await callback.message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption="I'll look for a solution from this position. Wait, this may take a while"
            )
            await callback.answer()

        flasks_solver(input_file=in_file, output_file=out_file)

        download_again = [
            [
                InlineKeyboardButton(text='📩🖼️Upload new image', callback_data='upload_new_image')
            ]
        ]
        download_buttons = InlineKeyboardMarkup(inline_keyboard=download_again)

        errors = [
            [
                InlineKeyboardButton(text='🔄️🖼️Reload image', callback_data='reload_image'),
                InlineKeyboardButton(text='➕🧪Add an empty flask', callback_data='add_an_empty_flask')
            ],
            [
                InlineKeyboardButton(text='📩🖼️Upload new image', callback_data='upload_new_image')
            ]
        ]
        error_buttons = InlineKeyboardMarkup(inline_keyboard=errors)

        if os.stat(out_file).st_size == 0 or os.path.isfile(out_file) == False:
            await callback.message.answer(
                f'😖😖😖Unfortunately, I was unable to find a solution for this arrangement.\nIf you want to change the order of undefined colors, click "Reload image".\nIf you know all the colors, but the solution still hasn’t been found, then I can add another empty flask, to do this, click “Add an empty flask”\nOr you can upload a new image, to do this, click "Upload new image"',
                reply_markup=error_buttons
            )
        else:
            with open(out_file, "r") as result:
                await callback.message.answer(
                    f'Yay!🥳🥳🥳I found a solution for you!!!🥳🥳🥳\nPlease note that the flasks are numbered starting from 0, not 1!\n{result.read()}\nLet me know if you want a solution for another screenshot :)',
                    reply_markup=download_buttons
                )
        # Удаление временных файлов
        os.remove(out_file)
        os.remove(in_file)
        os.remove(level_file)


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
    bot = Bot(token=API_TOKEN)
    dp.startup.register(clue)
    await dp.start_polling(bot)


if __name__ == '__main__':
    """Запуск, логгирование и прочие вещи"""
    asyncio.run(main())
