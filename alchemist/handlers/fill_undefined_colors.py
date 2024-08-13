from aiogram import Bot, Router, F  # Подключение библиотек
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.chat_action import ChatActionSender

from transfusion_of_liquids import transfusion_manage
from found_colors import found_colors_in_flasks, replace_in_list, create_image_for_replace, add_empty_flask
import config
import classes.all_my_classes as amc
from keyboards.all_my_keyboards import colors, recognition_check, upload_new, no_result

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
            'reload_image', 'add_an_empty_flask', 'upload_new_image',
            'ok', 'manually', 'no'
        ]
    )
)
async def fill_undef_values(callback: CallbackQuery, bot: Bot, state: FSMContext):
    '''Функция дозаполнения неопределенных цветов вручную'''
    # Получаем данные с путями к папкам
    props = await state.get_data()
    image_for_load = props['original_image']
    lvl_file = props['level_file']

    if callback.data == 'manually':
        async with ChatActionSender.upload_photo(bot=bot, chat_id=callback.from_user.id):
            await callback.message.delete()

    if callback.data == 'upload_new_image':
        await callback.message.edit_text('Upload a new screenshot as an image, please')
        await callback.answer()
        await state.set_state(amc.SolveFlasks.send_photo)
        return

    if callback.data == 'reload_image' or callback.data == 'add_an_empty_flask':
        logger.log_info(f'Изображение от пользователя {callback.from_user.id} отправлено на перезагрузку с/без добавления пустой колбы')
        # Распознаем цвета и добавляем их в список с последующей сериализации в json
        undef_colors, flasks_list = await found_colors_in_flasks(image_for_search=image_for_load, id_client=callback.from_user.id, reload_image=True)
        await state.update_data(undefined_colors=undef_colors)
        await state.update_data(flasks_list=flasks_list)
    elif callback.data == 'no':
        async with ChatActionSender.typing(bot=bot, chat_id=callback.from_user.id):
            '''Распознавание завершилось с ошибкой'''
            await callback.message.delete()
            await callback.message.answer(
                "Please upload your screenshot again so I can try to recognize it🙂\nI recommend that you take a new screenshot of the same level and send me the updated version, for details use the /faq command"
            )
            await callback.answer()
            logger.log_info('Изображение было распознано неверно')
            await state.set_state(amc.SolveFlasks.send_photo)
            return
    else:
        undef_colors = props['undefined_colors']
        flasks_list = props['flasks_list']

    if callback.data != 'reload_image' and callback.data != 'add_an_empty_flask':
        # Удаление цвета нажатой кнопки из словаря и замена неопределенного цвета цветом кнопки
        if undef_colors:
            for variation in config.color_variations:
                if callback.data == variation:
                    undef_colors[variation] -= 1
                    if undef_colors[variation] == 0:
                        undef_colors.pop(variation)
                    flasks_list = await replace_in_list(flasks_list=flasks_list, color_name=variation)
                    break
            await state.update_data(undefined_colors=undef_colors)
            await state.update_data(flasks_list=flasks_list)

    # Автозаполнение цвета, если остался только один неопределенный
    if len(undef_colors) == 1:
        for variation in undef_colors:
            while undef_colors[variation] != 0:
                undef_colors[variation] -= 1
                flasks_list = await replace_in_list(flasks_list=flasks_list, color_name=variation)
        undef_colors.pop(variation)
        await state.update_data(undefined_colors=undef_colors)
        await state.update_data(flasks_list=flasks_list)

    if callback.data == 'add_an_empty_flask':
        # Добавляем пустую ччетверть колбы
        if props['new_segment'] == 0 or props['new_segment'] == 3:
            idx_segment = 1
            await state.update_data(new_segment=idx_segment)
        elif props['new_segment'] < 3:
            idx_segment = props['new_segment'] + 1
            await state.update_data(new_segment=idx_segment)
        flasks_list = await add_empty_flask(flasks_list=flasks_list, idx_segment=idx_segment)
        await state.update_data(flasks_list=flasks_list)
        logger.log_info(f'В изображение пользователя {callback.from_user.id} была добавлена пустая четверть колбы')

    # Подготавливаем картинку, в которой подсвечиваем неопределенные области
    await create_image_for_replace(flasks_list=flasks_list, id_client=callback.from_user.id)

    if callback.data == 'add_an_empty_flask' or callback.data == 'reload_image':
        await callback.message.delete()
        async with ChatActionSender.upload_photo(bot=bot, chat_id=callback.from_user.id):
            # Изображение, где подсвечивается первый неопределенный цвет
            with open(lvl_file, 'rb') as open_image:
                await callback.message.answer_photo(
                    BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption="This is what I saw in your screenshot. Compare the colors here with the original image and please tell me if I succeeded so I can continue with the solution. If something is wrong, I can try again, or you can send this screenshot for feedback using the /support command🙂",
                    reply_markup=recognition_check()
                )
            await callback.answer()
            logger.log_info(f'Изображение для пользователя {callback.from_user.id} перезагружено для дальнейшего редактирования')
            return

    if undef_colors:
        if callback.data == 'reload_image':
            async with ChatActionSender.upload_photo(bot=bot, chat_id=callback.from_user.id):
                # Изображение, где подсвечивается первый неопределенный цвет
                with open(lvl_file, 'rb') as open_image:
                    await callback.message.answer_photo(
                        BufferedInputFile(
                            open_image.read(),
                            filename='solve_flasks'
                        ),
                        caption="This is what I saw in your screenshot. Compare the colors here with the original image and please tell me if I succeeded so I can continue with the solution. If something is wrong, I can try again, or you can send this screenshot for feedback using the /support command🙂",
                        reply_markup=recognition_check()
                    )
                await callback.answer()
                logger.log_info(f'Изображение для пользователя {callback.from_user.id} перезагружено для дальнейшего редактирования')
                return
        
        if callback.data == 'manually':
            async with ChatActionSender.upload_photo(bot=bot, chat_id=callback.from_user.id):
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
        else:
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
                    reply_markup=colors(undef_colors)
                )
        await callback.answer()
        logger.log_info(f'Изображение для пользователя {callback.from_user.id} дополнено и отправлено для дальнейшего редактирования')
    else:
        async with ChatActionSender.typing(bot=bot, chat_id=callback.from_user.id):
            '''Запускаем процесс поиска решения'''
            if callback.data == 'manually':
                # Итоговое изображение
                with open(lvl_file, 'rb') as open_image:
                    await callback.message.answer_photo(
                        BufferedInputFile(
                            open_image.read(),
                            filename='solve_flasks'
                        ),
                        caption="I'll look for a solution from this position. Wait, this may take a while"
                    )
            else:
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
                is_solved, steps = await transfusion_manage(bot=bot, chat_id=callback.from_user.id, task=flasks_list)
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
                await callback.message.answer(
                    f'Yay!🥳🥳🥳I found a solution for you!!!🥳🥳🥳\n{steps}\nLet me know if you want a solution for another screenshot :)',
                    reply_markup=upload_new()
                )
                os.remove(image_for_load)
                await state.set_state(amc.SolveFlasks.start_solving)

        # Удаление временных файлов
        os.remove(lvl_file)


@rtr.message(amc.SolveFlasks.set_color)
async def filling_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме заполнения цветом'''
    logger.log_info(f'Пользователь {message.from_user.id} проигнорировал кнопки')
    msg = await message.answer('Please select a color from above or choose what to do with the image')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()