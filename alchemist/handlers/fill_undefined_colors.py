from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender

from math import isnan

from found_colors import replace_in_list, create_image_for_replace
import classes.all_my_classes as amc
from keyboards.all_my_keyboards import colors, pay_attempts
from handlers.autofill import reply

import asyncio
import os


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.callback_query(
    amc.SolveFlasks.set_color,
    F.data.in_(
        [
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
            "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24",
            'upload_new_image', 'manually', 'no'
        ]
    )
)
async def fill_undef_values(callback: CallbackQuery, bot: Bot, state: FSMContext):
    '''Функция дозаполнения неопределенных цветов вручную'''
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
        free_attempts = props['count_free_attempts']
        paid_attempts = props['count_paid_attempts']
        if free_attempts == 0 and paid_attempts == 0:
            logger.log_info(f'У пользователя {callback.from_user.id} закончились попытки')
            msg_text = "Sorry, you've run out of attempts😞\nIf you want to continue now, you can buy multiple attempts for a small fee"
            msg_kb = pay_attempts()
            set_state = amc.SolveFlasks.pay_attempts
        else:
            msg_kb = None
            set_state = amc.SolveFlasks.send_photo
            if isnan(free_attempts):
                msg_text = f'Upload a new screenshot as an image, please'
            elif isnan(paid_attempts):
                msg_text = f'Upload a new screenshot as an image, please\nNow you have an unlimited 🎟️\n*Unlimited is available within 30 days from the date of payment'
            elif paid_attempts > 0 and free_attempts > 0:
                msg_text = f'Upload a new screenshot as an image, please\nNow you have:\nFree 🎟️: {free_attempts}\nPaid 🎟️: {paid_attempts}'
            elif paid_attempts == 0 and free_attempts > 0:
                msg_text = f'Upload a new screenshot as an image, please\nNow you have:\nFree 🎟️: {free_attempts}'
            elif paid_attempts > 0 and free_attempts == 0:
                msg_text = f'Upload a new screenshot as an image, please\nNow you have:\nPaid 🎟️: {paid_attempts}'
                
        await callback.message.edit_text(
            msg_text,
            reply_markup=msg_kb
        )
        await state.set_state(set_state)
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
            logger.log_info(f'Изображение от пользователя {callback.from_user.id} было распознано неверно')
            await state.set_state(amc.SolveFlasks.send_photo)
            return
    elif callback.data == 'manually':
        async with ChatActionSender.upload_photo(bot=bot, chat_id=callback.from_user.id):
            await callback.message.delete()
            undef_colors, flasks_id_list = props['undefined_colors'], props['flasks_id_list']
            await state.update_data(edit_undefined_colors=undef_colors)
            await state.update_data(edit_flasks_id_list=flasks_id_list)
            # Подготавливаем картинку, в которой подсвечиваем неопределенные области
            await create_image_for_replace(flasks_id_list=flasks_id_list, id_client=callback.from_user.id)
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
    
    # Промежуточный кадр без кнопок
    with open(lvl_file, 'rb') as open_image:
        await callback.message.edit_media(
            InputMediaPhoto(
                media=BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption="Please select from the options provided the color that should be in place of the green circle",
            )
        )
        
    edit_undef_colors, edit_flasks_id_list = props['edit_undefined_colors'], props['edit_flasks_id_list']
    # Удаление цвета нажатой кнопки из словаря и замена неопределенного цвета цветом кнопки
    if edit_undef_colors:
        edit_undef_colors[callback.data] -= 1
        if edit_undef_colors[callback.data] == 0:
            edit_undef_colors.pop(callback.data)
        edit_flasks_id_list = await replace_in_list(flasks_id_list=edit_flasks_id_list, color_id=int(callback.data))
        await state.update_data(edit_undefined_colors=edit_undef_colors)
        await state.update_data(edit_flasks_id_list=edit_flasks_id_list)

    # Автозаполнение цвета, если остался только один неопределенный
    if len(edit_undef_colors) == 1:
        while edit_undef_colors[list(edit_undef_colors.keys())[0]] != 0:
            edit_undef_colors[list(edit_undef_colors.keys())[0]] -= 1
            edit_flasks_id_list = await replace_in_list(flasks_id_list=edit_flasks_id_list, color_id=int(list(edit_undef_colors.keys())[0]))
        edit_undef_colors.pop(list(edit_undef_colors.keys())[0])
        await state.update_data(edit_undefined_colors=edit_undef_colors)
        await state.update_data(edit_flasks_id_list=edit_flasks_id_list)

    # Подготавливаем картинку, в которой подсвечиваем неопределенные области
    await create_image_for_replace(flasks_id_list=edit_flasks_id_list, id_client=callback.from_user.id)

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
        await reply(callback, bot, state, edit_flasks_id_list, 'upload_new_or_reload', False)


@rtr.message(amc.SolveFlasks.set_color)
async def filling_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме заполнения цветом'''
    logger.log_info(f'Пользователь {message.from_user.id} проигнорировал кнопки')
    msg = await message.answer('Please select a color from above or choose what to do with the image')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()
