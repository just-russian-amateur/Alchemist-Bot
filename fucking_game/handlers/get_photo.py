from aiogram import Bot, Router, F  # Подключение библиотек
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from flasks import flasks_solver
from found_colors import found_colors_in_flasks, create_image_for_replace
import config
import classes.solve_flasks as sf
from keyboards.all_my_keyboards import error_image, colors, feedback, upload_new, no_result

import asyncio
import logging
import os


rtr = Router()


@rtr.message(
    sf.SolveFlasks.send_photo,
    F.photo
)
async def get_photo(message: Message, bot: Bot, state: FSMContext):
    '''Функция получения и обработки фотографий'''
    config.image_for_load = f'./images/{message.photo[-1].file_id}.jpg'   # Сохраняем на всякий случай путь к картинке
    in_file, out_file = f"./tmp/start_level_{message.from_user.id}.json", f"./tmp/result_level_{message.from_user.id}.txt"
    level_file = f'./tmp/level_for_{message.from_user.id}.jpg'
    await bot.download(
        message.photo[-1],
        destination=config.image_for_load
    )
    await message.answer("I'll try to recognize colors in the photo")
    
    try:
        # Распознаем цвета и добавляем их в список с последующей сериализации в json
        config.undefined_colors = found_colors_in_flasks(image_for_search=config.image_for_load, id=message.from_user.id, reload_image=False)
    except:
        await message.answer(
            'Something went wrong...🤷‍♂️ Please upload another picture',
            reply_markup=error_image()
        )
        await state.set_state(sf.SolveFlasks.start_solving)

    if len(config.undefined_colors) != 0:
        # Подготавливаем картинку, в которой подсвечиваем неопределенные области
        create_image_for_replace(json_name=in_file, id_client=message.from_user.id)

        # Изображение, где подсвечивается первый неопределенный цвет
        with open(level_file, 'rb') as open_image:
            await message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption="Please check if I recognized everything correctly? If I misrecognized some colors or you noticed some other error, then feel free to let me know about the problem\nTo do this, click the button below the message (send a photo with which the error occurred and describe the problem)🙂",
                reply_markup=feedback()
            )
        await message.answer(
            'Please select from the options provided the color that should be in place of the green circle',
            reply_markup=colors()
        )
        await state.set_state(sf.SolveFlasks.set_color)
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

        if os.stat(out_file).st_size == 0 or os.path.isfile(out_file) == False:
            await message.answer(
                f"😖😖😖Unfortunately, I was unable to find a solution for this arrangement.\nIf you want to change the order of undefined colors, click '🔄️🖼️Reload image'.\nIf you know all the colors, but the solution still hasn't been found, then I can add another empty flask, to do this, click '➕🧪Add an empty flask'\nOr you can upload a new image, to do this, click '📩🖼️Upload new image'",
                reply_markup=no_result()
            )
        else:
            with open(out_file, "r") as result:
                await message.answer(
                    f'Yay!🥳🥳🥳I found a solution for you!!!🥳🥳🥳\nPlease note that the flasks are numbered starting from 0, not 1!\n{result.read()}\nLet me know if you want a solution for another screenshot🙂',
                    reply_markup=upload_new()
                )
        # Удаление временных файлов
        os.remove(out_file)
        os.remove(in_file)
        os.remove(level_file)
        await state.clear()


@rtr.message(sf.SolveFlasks.send_photo)
async def sending_photo_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме отправки фото'''
    msg = await message.answer('Send a photo please')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()