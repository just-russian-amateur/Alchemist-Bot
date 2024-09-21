from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender

from found_colors import replace_in_list, create_image_for_replace
import config
import classes.all_my_classes as amc
from keyboards.all_my_keyboards import colors
from handlers.send_welcome import check_user
from handlers.autofill import reply

import asyncio
import os


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.callback_query(
    amc.SolveFlasks.set_color,
    F.data.in_(
        [
            "LIGHT BLUE", "ORANGE", "YELLOW", "RED", "LIGHT GREEN", "BLUE", "BURGUNDY", "LIME", "MOSS",
            "GREEN", "PINK", "CRIMSON", "CREAM", "PURPLE", "GRAY", "LILAC", "PEACH", "BROWN", "COCOA",
            'upload_new_image', 'manually', 'no'
        ]
    )
)
async def fill_undef_values(callback: CallbackQuery, bot: Bot, state: FSMContext):
    '''Функция дозаполнения неопределенных цветов вручную'''
    await check_user(callback.message.from_user.id, state)
    # Получаем данные с путями к файлам
    props = await state.get_data()
    image_for_load, lvl_file = props['original_image'], props['level_file']

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
            undef_colors, flasks_list = props['undefined_colors'], props['flasks_list']
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
    
    edit_undef_colors, edit_flasks_list = props['edit_undefined_colors'], props['edit_flasks_list']
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
        await reply(callback, bot, state, edit_flasks_list, 'upload_new_or_reload', False)


@rtr.message(amc.SolveFlasks.set_color)
async def filling_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме заполнения цветом'''
    logger.log_info(f'Пользователь {message.from_user.id} проигнорировал кнопки')
    msg = await message.answer('Please select a color from above or choose what to do with the image')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()
