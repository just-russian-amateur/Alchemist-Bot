from aiogram import Router, F  # Подключение библиотек
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from flasks import flasks_solver
from found_colors import found_colors_in_flasks, replace_in_json, create_image_for_replace, add_empty_flask
import config
import classes.solve_flasks as sf
from keyboards.all_my_keyboards import error_image, colors, feedback, upload_new, no_result

import asyncio
import logging
import os


rtr = Router()


@rtr.callback_query(
    sf.SolveFlasks.set_color,
    F.data.in_(
        [
            "LIGHT BLUE", "ORANGE", "YELLOW", "RED", "LIGHT GREEN", "BLUE", "BURGUNDY",
            "GREEN", "PINK", "CRIMSON", "CREAM", "PURPLE", "GRAY","LILAC",
            'reload_image', 'add_an_empty_flask', 'upload_new_image'
        ]
    )
)
async def fill_undef_values(callback: CallbackQuery, state: FSMContext):
    '''Функция дозаполнения неопределенных цветов вручную'''
    if callback.data == 'upload_new_image':
        await callback.message.answer('Upload a new screenshot as an image, please')
        await callback.answer()
        await state.set_state(sf.SolveFlasks.send_photo)
        return

    this_path = f'./{callback.from_user.id}'
    in_file, out_file = f"{this_path}/tmp/start_level_{callback.from_user.id}.json", f"{this_path}/tmp/result_level_{callback.from_user.id}.txt"
    level_file = f'{this_path}/tmp/level_for_{callback.from_user.id}.jpg'

    if callback.data == 'reload_image' or callback.data == 'add_an_empty_flask':
        try:
            # Распознаем цвета и добавляем их в список с последующей сериализации в json
            config.undefined_colors = found_colors_in_flasks(image_for_search=config.image_for_load, id_client=callback.from_user.id, reload_image=True)
        except:
            await callback.message.answer(
                'Something went wrong...🤷‍♂️ Please upload another picture',
                reply_markup=error_image()
            )
            await callback.answer()
            await state.set_state(sf.SolveFlasks.start_solving)

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
        if callback.data == 'add_an_empty_flask':
            # Добавляем пустую колбу
            add_empty_flask(json_name=in_file)

        # Подготавливаем картинку, в которой подсвечиваем неопределенные области
        create_image_for_replace(json_name=in_file, id_client=callback.from_user.id)

        if callback.data == 'reload_image' or callback.data == 'add_an_empty_flask':
            # Изображение, где подсвечивается первый неопределенный цвет
            with open(level_file, 'rb') as open_image:
                await callback.message.answer_photo(
                    BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption="Please check if I recognized everything correctly? If I misrecognized some colors or you noticed some other error, then feel free to let me know about the problem\nTo do this, click the button below the message (send a photo with which the error occurred and describe the problem)🙂",
                    reply_markup=feedback()
                )
            await callback.message.answer(
                'Please select from the options provided the color that should be in place of the green circle',
                reply_markup=colors()
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
                    reply_markup=colors()
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

        if os.stat(out_file).st_size == 0 or os.path.isfile(out_file) == False:
            await callback.message.answer(
                f'😖😖😖Unfortunately, I was unable to find a solution for this arrangement.\nIf you want to change the order of undefined colors, click "🔄️🖼️Reload image".\nIf you know all the colors, but the solution still hasn’t been found, then I can add another empty flask, to do this, click “➕🧪Add an empty flask”\nOr you can upload a new image, to do this, click "📩🖼️Upload new image"',
                reply_markup=no_result()
            )
            await state.set_state(sf.SolveFlasks.set_color)
        else:
            with open(out_file, "r") as result:
                await callback.message.answer(
                    f'Yay!🥳🥳🥳I found a solution for you!!!🥳🥳🥳\nPlease note that the flasks are numbered starting from 0, not 1!\n{result.read()}\nLet me know if you want a solution for another screenshot :)',
                    reply_markup=upload_new()
                )
            await state.set_state(sf.SolveFlasks.start_solving)
        # Удаление временных файлов
        os.remove(out_file)
        os.remove(in_file)
        os.remove(level_file)


@rtr.message(sf.SolveFlasks.send_photo)
async def filling_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме заполнения цветом'''
    msg = await message.answer('Please select a color from above')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()