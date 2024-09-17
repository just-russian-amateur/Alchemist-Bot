from aiogram import Bot, Router, F  # Подключение библиотек
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.chat_action import ChatActionSender

from transfusion_of_liquids import transfusion_manage
from found_colors import replace_in_list, create_image_for_replace
import config
import classes.all_my_classes as amc
from keyboards.all_my_keyboards import colors, upload_new, no_result

import asyncio
import os


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.callback_query(
    amc.SolveFlasks.set_color,
    F.data.in_(
        [
            "LIGHT BLUE", "ORANGE", "YELLOW", "RED", "LIGHT GREEN", "BLUE", "BURGUNDY", "LIME", "MOSS",
            "GREEN", "PINK", "CRIMSON", "CREAM", "PURPLE", "GRAY", "LILAC", "PEACH", "BROWN"
            'upload_new_image', 'manually', 'no'
        ]
    )
)
async def fill_undef_values(callback: CallbackQuery, bot: Bot, state: FSMContext):
    '''Функция дозаполнения неопределенных цветов вручную'''
    # Получаем данные с путями к файлам
    props = await state.get_data()
    image_for_load, lvl_file = props['original_image'], props['level_file']
    undef_colors, flasks_list = props['undefined_colors'], props['flasks_list']
    edit_undef_colors, edit_flasks_list = props['edit_undefined_colors'], props['edit_flasks_list']

    if callback.data == 'upload_new_image':
        # Удаление временных файлов
        if os.path.isfile(image_for_load):
            os.remove(image_for_load)
        if os.path.isfile(lvl_file):
            os.remove(lvl_file)
        await state.update_data(new_segment=0)
        # Предлагаем купить попытки, если они закончились
        await callback.message.edit_text('Upload a new screenshot as an image, please')
        await state.set_state(amc.SolveFlasks.send_photo)
        await callback.answer()
        return
    elif callback.data == 'no':
        async with ChatActionSender.typing(bot=bot, chat_id=callback.from_user.id):
            '''Распознавание завершилось с ошибкой'''
            await callback.message.delete()
            await callback.message.answer(
                "Please upload your screenshot again so I can try to recognize it🙂\nI recommend that you take a new screenshot of the same level and send me the updated version, for details use the /faq command"
            )
            await callback.answer()
            logger.log_info(f'Изображение от пользователя {callback.message.from_user.id} было распознано неверно')
            await state.set_state(amc.SolveFlasks.send_photo)
            return
    elif callback.data == 'manually':
        async with ChatActionSender.upload_photo(bot=bot, chat_id=callback.from_user.id):
            await callback.message.delete()
            # Подготавливаем картинку, в которой подсвечиваем неопределенные области
            await create_image_for_replace(flasks_list=flasks_list, id_client=callback.from_user.id)
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
        return
    elif not callback.data in ['upload_new_image', 'manually', 'no']:
        # Удаление цвета нажатой кнопки из словаря и замена неопределенного цвета цветом кнопки
        if edit_undef_colors:
            for variation in config.color_variations:
                if callback.data == variation:
                    edit_undef_colors[variation] -= 1
                    if edit_undef_colors[variation] == 0:
                        edit_undef_colors.pop(variation)
                    edit_flasks_list = await replace_in_list(flasks_list=edit_flasks_list, color_name=variation)
                    break
            await state.update_data(edit_undefined_colors=edit_undef_colors)
            await state.update_data(edit_flasks_list=edit_flasks_list)

    # Автозаполнение цвета, если остался только один неопределенный
    if len(edit_undef_colors) == 1:
        for variation in edit_undef_colors:
            while edit_undef_colors[variation] != 0:
                edit_undef_colors[variation] -= 1
                edit_flasks_list = await replace_in_list(flasks_list=edit_flasks_list, color_name=variation)
        edit_undef_colors.pop(variation)
        await state.update_data(edit_undefined_colors=edit_undef_colors)
        await state.update_data(edit_flasks_list=edit_flasks_list)

    # Подготавливаем картинку, в которой подсвечиваем неопределенные области
    await create_image_for_replace(flasks_list=edit_flasks_list, id_client=callback.from_user.id)

    if edit_undef_colors:
        # Изображение, где подсвечивается первый неопределенный цвет
        with open(lvl_file, 'rb') as open_image:
            await callback.message.edit_media(
                InputMediaPhoto(
                    media=BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption="Please select from the options provided the color that should be in place of the green circle",
                ),
                reply_markup=colors(edit_undef_colors)
            )
        await callback.answer()
        logger.log_info(f'Изображение для пользователя {callback.from_user.id} дополнено и отправлено для дальнейшего редактирования')
    else:
        async with ChatActionSender.typing(bot=bot, chat_id=callback.from_user.id):
            '''Запускаем процесс поиска решения'''
            # Итоговое изображение
            with open(lvl_file, 'rb') as open_image:
                await callback.message.edit_media(
                    InputMediaPhoto(
                        media=BufferedInputFile(
                            open_image.read(),
                            filename='solve_flasks'
                        ),
                        caption="I'll look for a solution from this position. Wait, this may take a while"
                    )
                )
            await callback.answer()
            logger.log_info(f'Пользователь {callback.from_user.id} заполнил все пустоты')

            try:
                # Вызываем функцию перебора переливаний
                is_solved, steps = await transfusion_manage(bot=bot, chat_id=callback.from_user.id, task=edit_flasks_list)
            except TelegramBadRequest:
                logger.log_error('Превышено время ожидания ответа на начало поиска решения')

            # В случае, если файл пустой или не был создан сообщаем, что решение не найдено, иначе выводим решение
            if not is_solved:
                await callback.message.answer(
                    f'😖😖😖Unfortunately, I was unable to find a solution for this arrangement.\nIf you want to change the order of undefined colors, click "🔄️🖼️Reload image".\nIf you know all the colors, but the solution still hasn’t been found, then I can add another empty flask, to do this, click “➕🧪Add an empty flask”\nOr you can upload a new image, to do this, click "📩🖼️Upload new image"',
                    reply_markup=no_result()
                )
            else:
                await callback.message.answer(
                    f'Yay!🥳🥳🥳I found a solution for you!!!🥳🥳🥳\n{steps}\nLet me know if you want a solution for another screenshot🙂',
                    reply_markup=upload_new()
                )
            await state.set_state(amc.SolveFlasks.set_color)


@rtr.message(amc.SolveFlasks.set_color)
async def filling_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме заполнения цветом'''
    logger.log_info(f'Пользователь {message.from_user.id} проигнорировал кнопки')
    msg = await message.answer('Please select a color from above or choose what to do with the image')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()
