from aiogram import Router, F  # Подключение библиотек
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from transfusion_of_liquids import transfusion_manage
from found_colors import found_colors_in_flasks, replace_in_json, create_image_for_replace, add_empty_flask
import config
import classes.all_my_classes as amc
from keyboards.all_my_keyboards import error_image, colors, feedback, upload_new, no_result

import asyncio
import os


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.callback_query(
    amc.SolveFlasks.set_color,
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
    await callback.message.delete()
    if callback.data == 'upload_new_image':
        await callback.message.answer('Upload a new screenshot as an image, please')
        await callback.answer()
        await state.set_state(amc.SolveFlasks.send_photo)
        return

    # Получаем данные с путями к папкам
    paths = await state.get_data()
    image_for_load = paths['original_image']
    in_file, out_file = paths['input_file'], paths['output_file']
    lvl_file = paths['level_file']

    if callback.data == 'reload_image' or callback.data == 'add_an_empty_flask':
        logger.log_info(f'Изображение от пользователя {callback.from_user.id} отправлено на перезагрузку с/без добавления пустой колбы')
        # Распознаем цвета и добавляем их в список с последующей сериализации в json
        undef_colors = found_colors_in_flasks(image_for_search=image_for_load, id_client=callback.from_user.id, reload_image=True)
        await state.update_data(undefined_colors=undef_colors)
    else:
        undef_colors = paths['undefined_colors']

    if callback.data != 'reload_image' and callback.data != 'add_an_empty_flask':
        # Удаление цвета нажатой кнопки из словаря и замена неопределенного цвета цветом кнопки
        if undef_colors:
            for variation in config.color_variations:
                if callback.data == variation:
                    undef_colors[variation] -= 1
                    if undef_colors[variation] == 0:
                        undef_colors.pop(variation)
                    replace_in_json(json_name=in_file, color_name=variation)
                    break
            await state.update_data(undefined_colors=undef_colors)

    # Автозаполнение цвета, если остался только один неопределенный
    if len(undef_colors) == 1:
        for variation in undef_colors:
            while undef_colors[variation] != 0:
                undef_colors[variation] -= 1
                replace_in_json(json_name=in_file, color_name=variation)
        undef_colors.pop(variation)
        await state.update_data(undefined_colors=undef_colors)

    if undef_colors:
        if callback.data == 'add_an_empty_flask':
            # Добавляем пустую колбу
            add_empty_flask(json_name=in_file)
            logger.log_info(f'В изображение пользователя {callback.from_user.id} была добавлена пустая колба')

        # Подготавливаем картинку, в которой подсвечиваем неопределенные области
        create_image_for_replace(json_name=in_file, id_client=callback.from_user.id)

        if callback.data == 'reload_image' or callback.data == 'add_an_empty_flask':
            # Изображение, где подсвечивается первый неопределенный цвет
            with open(lvl_file, 'rb') as open_image:
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
                reply_markup=colors(undef_colors)
            )
            await callback.answer()
            logger.log_info(f'Изображение для пользователя {callback.from_user.id} перезагружено для дальнейшего редактирования')
        else:
            # Изображение, где подсвечивается первый неопределенный цвет
            with open(lvl_file, 'rb') as open_image:
                await callback.message.answer_photo(
                    BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption="Please select from the options provided the color that should be in place of the green circle",
                    reply_markup=colors(undef_colors)
                )
            await callback.answer()
            logger.log_info(f'Изображение для пользователя {callback.from_user.id} дополнено и отправлено для дальнейшего редактирования')
    else:
        # Формируем итоговый json
        create_image_for_replace(json_name=in_file, id_client=callback.from_user.id)
        # Итоговое изображение
        with open(lvl_file, 'rb') as open_image:
            await callback.message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption="I'll look for a solution from this position. Wait, this may take a while"
            )
        await callback.answer()

        logger.log_info(f'Пользователь {callback.from_user.id} заполнил все пустоты')
        try:
            # Вызываем функцию перебора переливаний
            is_solved = transfusion_manage(task=in_file, result=out_file)
        except TelegramBadRequest:
            logger.log_error('Превышено время ожидания ответа на начало поиска решения')

        # В случае, если файл пустой или не был создан сообщаем, что решение не найдено, иначе выводим решение
        if not is_solved:
            await callback.message.answer(
                f'😖😖😖Unfortunately, I was unable to find a solution for this arrangement.\nIf you want to change the order of undefined colors, click "🔄️🖼️Reload image".\nIf you know all the colors, but the solution still hasn’t been found, then I can add another empty flask, to do this, click “➕🧪Add an empty flask”\nOr you can upload a new image, to do this, click "📩🖼️Upload new image"',
                reply_markup=no_result()
            )
            await state.set_state(amc.SolveFlasks.set_color)
        else:
            with open(out_file, "r") as result:
                await callback.message.answer(
                    f'Yay!🥳🥳🥳I found a solution for you!!!🥳🥳🥳\n{result.read()}\nLet me know if you want a solution for another screenshot :)',
                    reply_markup=upload_new()
                )
            await state.set_state(amc.SolveFlasks.start_solving)
        # Удаление временных файлов
        if os.path.isfile(out_file):
            os.remove(out_file)
        os.remove(in_file)
        os.remove(lvl_file)


@rtr.message(amc.SolveFlasks.set_color)
async def filling_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме заполнения цветом'''
    logger.log_info(f'Пользователь {message.from_user.id} проигнорировал кнопки')
    msg = await message.answer('Please select a color from above or choose what to do with the image')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()