from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender

from math import isnan

from found_colors import replace_in_list, create_image_for_replace, replace_selected_color, replace_undefined, remove_selected_flask
import classes.all_my_classes as amc
from keyboards.all_my_keyboards import colors, pay_attempts, change_flask, change_segment, change_color, recognition_check
from handlers.autofill import reply

import asyncio
import os


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def edit_image(callback: CallbackQuery, state: FSMContext, new_caption: str, keyboard=None, new_state=None, edit_media=True, fill_color=False):
    '''Функция для изменения надписей под изображением'''
    # Получаем данные с путями к файлам
    props = await state.get_data()
    lvl_file = props['level_file']
    if edit_media:
        with open(lvl_file, 'rb') as open_image:
            await callback.message.edit_media(
                InputMediaPhoto(
                    media=BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption=new_caption
                ),
                reply_markup=keyboard
            )
        if new_state:
            await state.set_state(new_state)
        await callback.answer()
    else:
        # Изображение, где подсвечивается первый неопределенный цвет
        with open(lvl_file, 'rb') as open_image:
            await callback.message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption=new_caption,
                reply_markup=keyboard
            )

    if fill_color:
        with open('../color_examples.jpg', 'rb') as open_image:
            msg = await callback.message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='color_examples'
                ),
                caption="Here are examples of all the colors I know (this message will be automatically deleted after 30 seconds)"
            )
            await asyncio.sleep(30)
            await msg.delete()


@rtr.callback_query(
    amc.SolveFlasks.set_color,
    F.data.in_(
        [
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
            "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24",
            'upload_new_image', 'manually', 'no', 'remove_flask'
        ]
    )
)
@rtr.callback_query(amc.SolveFlasks.choose_segment)
@rtr.callback_query(amc.SolveFlasks.remove_flask)
@rtr.callback_query(
    amc.SolveFlasks.choose_color,
    F.data.in_(
        [
            "0", "1", "2", "3"
        ]
    )
)
@rtr.callback_query(
    amc.SolveFlasks.confirm_changing,
    F.data.in_(
        [
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
            "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24"
        ]
    )
)
async def fill_undef_values(callback: CallbackQuery, bot: Bot, state: FSMContext):
    '''Функция дозаполнения неопределенных цветов вручную'''
    # Получаем данные с путями к файлам
    current_state = await state.get_state()
    props = await state.get_data()
    image_for_load, lvl_file = props['original_image'], props['level_file']

    if current_state == amc.SolveFlasks.set_color:
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
        elif callback.data in ['no', 'remove_flask']:
            '''Распознавание завершилось с ошибкой, выбираем колбу для замены цвета'''
            flasks_id_list = props['flasks_id_list']
            new_caption = 'Select the number of the flask you want to manipulate (count the flask numbers from left to right, starting from the top row, i.e. top row 1-6, middle row 7-12, bottom row 13-18)'
            kb = change_flask(len(flasks_id_list))
            if callback.data == 'no':
                new_state = amc.SolveFlasks.choose_segment
            else:
                new_state = amc.SolveFlasks.remove_flask
            await edit_image(callback, state, new_caption, kb, new_state)
            logger.log_info(f'Изображение от пользователя {callback.from_user.id} было распознано неверно. Пользователь выбрал изменение проблемных цветов')
            return
        elif callback.data == 'manually':
            async with ChatActionSender.upload_photo(bot=bot, chat_id=callback.from_user.id):
                await callback.message.delete()
                undef_colors, flasks_id_list = props['undefined_colors'], props['flasks_id_list']
                await state.update_data(edit_undefined_colors=undef_colors)
                await state.update_data(edit_flasks_id_list=flasks_id_list)
                # Подготавливаем картинку, в которой подсвечиваем неопределенные области
                await create_image_for_replace(flasks_id_list=flasks_id_list, id_client=callback.from_user.id)
                new_caption = "Please select from the options provided the color that should be in place of the green circle"
                kb = colors(undef_colors)
                await edit_image(callback=callback, state=state, new_caption=new_caption, keyboard=kb, edit_media=False, fill_color=True)
            return
        
        # Промежуточный кадр без кнопок
        new_caption= "Please select from the options provided the color that should be in place of the green circle"
        await edit_image(callback, state, new_caption)
            
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
            new_caption = "Please select from the options provided the color that should be in place of the green circle"
            kb = colors(edit_undef_colors)
            await edit_image(callback, state, new_caption, kb)
            logger.log_info(f'Изображение для пользователя {callback.from_user.id} дополнено и отправлено для дальнейшего редактирования')
        else:
            await reply(callback, bot, state, edit_flasks_id_list, 'upload_new_or_reload', False)
    else:
        if current_state == amc.SolveFlasks.choose_segment:
            await state.update_data(choosen_flask=int(callback.data))
            new_caption="Select the segment number in the flask to change the color (segments are numbered from bottom to top, i.e. the bottom segment of the flask is 1, and the top segment is 4)"
            kb = change_segment()
            new_state = amc.SolveFlasks.choose_color
            await edit_image(callback, state, new_caption, kb, new_state)
            logger.log_info(f'Изображение от пользователя {callback.from_user.id} было распознано неверно. Пользователь выбирает сегмент для изменения')
        elif current_state == amc.SolveFlasks.remove_flask or current_state == amc.SolveFlasks.confirm_changing:
            flasks_id_list = props['flasks_id_list']
            if current_state == amc.SolveFlasks.remove_flask:
                logger.log_info(f'Пользователь {callback.from_user.id} удаляет колбу')
                await state.update_data(removed_flask=int(callback.data))
                flasks_id_list = await remove_selected_flask(flasks_id_list, int(callback.data))
            else:
                new_caption = "Select a new color for the segment"
                await edit_image(callback, state, new_caption)
                logger.log_info(f'Пользователь {callback.from_user.id} заменяет цвет')
                await state.update_data(choosen_color=int(callback.data))
                choosen_flask, choosen_segment = props["choosen_flask"], props["choosen_segment"]
                flasks_id_list = await replace_selected_color(flasks_id_list, int(callback.data), choosen_flask, choosen_segment)
            undef_colors = await replace_undefined(flasks_id_list)
    
            await state.update_data(undefined_colors=undef_colors)
            await state.update_data(flasks_id_list=flasks_id_list)
            await state.update_data(edit_undefined_colors=undef_colors)
            await state.update_data(edit_flasks_id_list=flasks_id_list)
    
            await create_image_for_replace(flasks_id_list=flasks_id_list, id_client=callback.from_user.id)
            if current_state == amc.SolveFlasks.remove_flask:
                new_caption = "The flask removal was successful! Please choose your next action"
                kb = recognition_check()
                new_state = amc.SolveFlasks.set_color    
            else:
                new_caption = "Replacement successful! Please choose your next action"
                kb = recognition_check()
                new_state = amc.SolveFlasks.set_color
            await edit_image(callback, state, new_caption, kb, new_state)
        elif current_state == amc.SolveFlasks.choose_color:
            new_caption = "Select a new color for the segment"
            kb = change_color()
            new_state = amc.SolveFlasks.confirm_changing
            await state.update_data(choosen_segment=int(callback.data))
            await edit_image(callback, state, new_caption, kb, new_state, fill_color=True)
            logger.log_info(f'Изображение от пользователя {callback.from_user.id} было распознано неверно. Пользователь выбирает новый цвет')


@rtr.message(amc.SolveFlasks.set_color)
async def filling_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме заполнения цветом'''
    logger.log_info(f'Пользователь {message.from_user.id} проигнорировал кнопки')
    msg = await message.answer('Please select a color from above or choose what to do with the image')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()
