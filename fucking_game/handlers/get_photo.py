from aiogram import Bot, Router, F  # Подключение библиотек
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from transfusion_of_liquids import transfusion_manage
from found_colors import found_colors_in_flasks, create_image_for_replace
import classes.all_my_classes as amc
from keyboards.all_my_keyboards import error_image, colors, feedback, upload_new, no_result

import asyncio
import os


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.message(
    amc.SolveFlasks.send_photo,
    F.photo
)
async def get_photo(message: Message, bot: Bot, state: FSMContext):
    '''Функция получения и обработки фотографий'''
    # Создание папки со скриншотами и папки для временных изображений в папке с id пользователя
    this_path = f'./{message.from_user.id}'
    if not os.path.isdir(f'{this_path}/images'):
        os.mkdir(f'{this_path}/images')
    if not os.path.isdir(f'{this_path}/tmp'):
        os.mkdir(f'{this_path}/tmp')

    image_for_load = f'{this_path}/images/{message.photo[-1].file_id}.jpg'   # Сохраняем на всякий случай путь к картинке
    in_file, out_file = f"{this_path}/tmp/start_level_{message.from_user.id}.json", f"{this_path}/tmp/result_level_{message.from_user.id}.txt"
    lvl_file = f'{this_path}/tmp/level_for_{message.from_user.id}.jpg'
    # Сохраняем пути в машину состояний
    await state.update_data(original_image=image_for_load)
    await state.update_data(input_file=in_file)
    await state.update_data(output_file=out_file)
    await state.update_data(level_file=lvl_file)
    # Загрузка фото в буфер для последующей обработки
    await bot.download(
        message.photo[-1],
        destination=image_for_load
    )
    await message.answer("I'll try to recognize colors in the photo")
    logger.log_info(f'Пользователь {message.from_user.id} отправил фото')
    
    try:
        # Распознаем цвета и добавляем их в список с последующей сериализации в json
        undef_colors = found_colors_in_flasks(image_for_search=image_for_load, id_client=message.from_user.id, reload_image=False)
        await state.update_data(undefined_colors=undef_colors)
    except:
        # Если есть любое прерывание во время распознавания, то просим пользователя загрузить новое фото
        # (генерация прерывания говорит о том, что фото не является скриншотом колб или не соответствует условиям)
        await message.answer(
            'Something went wrong...🤷‍♂️ Please upload another picture',
            reply_markup=error_image()
        )
        logger.log_error('Изображение не подходит для распознавания')
        await state.set_state(amc.SolveFlasks.start_solving)

    if undef_colors:
        # Подготавливаем картинку, в которой подсвечиваем неопределенные области
        create_image_for_replace(json_name=in_file, id_client=message.from_user.id)

        # Изображение, где подсвечивается первый неопределенный цвет
        with open(lvl_file, 'rb') as open_image:
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
            reply_markup=colors(undef_colors)
        )
        logger.log_info(f'Изображение для пользователя {message.from_user.id} успешно создано и готово для редактирования')
        await state.set_state(amc.SolveFlasks.set_color)
    else:
        # Формируем итоговый json
        create_image_for_replace(json_name=in_file, id_client=message.from_user.id)
        # Итоговое изображение
        with open(lvl_file, 'rb') as open_image:
            await message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption="I'll look for a solution from this position. Wait, this may take a while"
            )
        logger.log_info(f'Пользователь {message.from_user.id} заполнил все пустоты')
        try:
            # Вызываем функцию перебора переливаний
            is_solved = transfusion_manage(task=in_file, result=out_file)
        except TelegramBadRequest:
            logger.log_error('Превышено время ожидания ответа на начало поиска решения')

        # В случае, если файл пустой или не был создан сообщаем, что решение не найдено, иначе выводим решение
        if not is_solved:
            await message.answer(
                f"😖😖😖Unfortunately, I was unable to find a solution for this arrangement.\nIf you want to change the order of undefined colors, click '🔄️🖼️Reload image'.\nIf you know all the colors, but the solution still hasn't been found, then I can add another empty flask, to do this, click '➕🧪Add an empty flask'\nOr you can upload a new image, to do this, click '📩🖼️Upload new image'",
                reply_markup=no_result()
            )
            await state.set_state(amc.SolveFlasks.set_color)
        else:
            with open(out_file, "r") as result:
                await message.answer(
                    f'Yay!🥳🥳🥳I found a solution for you!!!🥳🥳🥳\n{result.read()}\nLet me know if you want a solution for another screenshot🙂',
                    reply_markup=upload_new()
                )
            await state.set_state(amc.SolveFlasks.start_solving)
        # Удаление временных файлов
        if os.path.isfile(out_file):
            os.remove(out_file)
        os.remove(in_file)
        os.remove(lvl_file)


@rtr.message(amc.SolveFlasks.send_photo)
async def sending_photo_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме отправки фото'''
    logger.log_info(f'Пользователь {message.from_user.id} отправил что-то кроме фото')
    msg = await message.answer('Send a photo please')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()