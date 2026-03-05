from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender

from found_colors import replace_in_list, create_image_for_replace, replace_selected_color, replace_undefined, remove_selected_flask
import classes.all_my_classes as amc
from keyboards.all_my_keyboards import colors, change_flask, change_segment, change_color, recognition_check
from handlers.autofill import reply
from handlers.start_solving import check_attempts
from texts.all_my_texts import FillUndefinedColorsTexts
from texts.redis_keys import RedisKeys
from callbacks.all_my_callbacks import CallbacksData

import asyncio
import os


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def edit_image(callback: CallbackQuery, state: FSMContext, new_caption: str, keyboard=None, new_state=None, edit_media=True, fill_color=False):
    '''Функция для изменения надписей под изображением'''

    # Получаем данные с путями к файлам
    user_data = await state.get_data()
    lvl_file = user_data[RedisKeys.LVL_FILE]

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
        # Изображение с примерами цветов, которые поддерживает бот и их названиями
        with open('color_examples.jpg', 'rb') as open_image:
            msg = await callback.message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='color_examples'
                ),
                caption=FillUndefinedColorsTexts.COLORS_EXAMPLE_CAPTION
            )
            await asyncio.sleep(30)
            await msg.delete()


@rtr.callback_query(
    amc.SolveFlasks.set_color,
    F.data.in_(
        [
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
            "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24",
            CallbacksData.UPLOAD_IMAGE, CallbacksData.MANUALLY, CallbacksData.NO,
            CallbacksData.REMOVE_FLASK
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
    user_data = await state.get_data()
    image_for_load, lvl_file = user_data[RedisKeys.IMAGE], user_data[RedisKeys.LVL_FILE]

    if current_state == amc.SolveFlasks.set_color:

        if callback.data == CallbacksData.UPLOAD_IMAGE:
            
            # Удаление временных файлов
            if os.path.isfile(image_for_load):
                os.remove(image_for_load)
            if os.path.isfile(lvl_file):
                os.remove(lvl_file)

            # Проверяем, что пользователь может использовать бота
            await check_attempts(
                data=user_data,
                callback=callback,
                state=state
            )
            await callback.answer()
            return

        elif callback.data in [CallbacksData.NO, CallbacksData.REMOVE_FLASK]:

            '''
            Распознавание завершилось с ошибкой, выбираем колбу для замены цвета
            '''

            flasks_id_list = user_data[RedisKeys.FLASKS_LIST]
            new_caption = FillUndefinedColorsTexts.CHOOSE_FLASK
            kb = change_flask(len(flasks_id_list))

            if callback.data == CallbacksData.NO:
                new_state = amc.SolveFlasks.choose_segment
            else:
                new_state = amc.SolveFlasks.remove_flask

            await edit_image(callback, state, new_caption, kb, new_state)

            logger.log_info(f'Изображение от пользователя {callback.from_user.id} было распознано неверно. Пользователь выбрал изменение проблемных цветов')
            
            return

        elif callback.data == CallbacksData.MANUALLY:

            '''
            Выбрано заполнение неизвестных цветов вручную
            '''

            async with ChatActionSender.upload_photo(bot=bot, chat_id=callback.from_user.id):

                await callback.message.delete()

                undef_colors, flasks_id_list = user_data[RedisKeys.UNDEF_COLORS], user_data[RedisKeys.FLASKS_LIST]

                await state.update_data(edit_undefined_colors=undef_colors)
                await state.update_data(edit_flasks_id_list=flasks_id_list)

                # Подготавливаем картинку, в которой подсвечиваем неопределенные области
                await create_image_for_replace(flasks_id_list=flasks_id_list, id_client=callback.from_user.id)

                new_caption = FillUndefinedColorsTexts.MANUALLY_FILLING
                kb = colors(undef_colors)

                await edit_image(callback=callback, state=state, new_caption=new_caption, keyboard=kb, edit_media=False, fill_color=True)

            return
        
        # Промежуточный кадр без кнопок
        new_caption = FillUndefinedColorsTexts.MANUALLY_FILLING
        await edit_image(callback, state, new_caption)
            
        edit_undef_colors, edit_flasks_id_list = user_data[RedisKeys.EDITED_UNDEF_COLORS], user_data[RedisKeys.EDITED_FLASKS_LIST]

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
            new_caption = FillUndefinedColorsTexts.MANUALLY_FILLING
            kb = colors(edit_undef_colors)

            await edit_image(callback, state, new_caption, kb)

            logger.log_info(f'Изображение для пользователя {callback.from_user.id} дополнено и отправлено для дальнейшего редактирования')

        else:
            await reply(callback, bot, state, edit_flasks_id_list, 'upload_new_or_reload', False)

    else:

        if current_state == amc.SolveFlasks.choose_segment:
            # Выбираем сегмент внутри выбранной колбы для замены
            await state.update_data(choosen_flask=int(callback.data))

            new_caption=FillUndefinedColorsTexts.CHOOSE_SEGMENT
            kb = change_segment()
            new_state = amc.SolveFlasks.choose_color

            await edit_image(callback, state, new_caption, kb, new_state)

            logger.log_info(f'Изображение от пользователя {callback.from_user.id} было распознано неверно. Пользователь выбирает сегмент для изменения')
        
        elif current_state == amc.SolveFlasks.remove_flask or current_state == amc.SolveFlasks.confirm_changing:
            
            flasks_id_list = user_data[RedisKeys.FLASKS_LIST]
            
            if current_state == amc.SolveFlasks.remove_flask:
                # Удаляем выбранную колбу целиком
                logger.log_info(f'Пользователь {callback.from_user.id} удаляет колбу')

                await state.update_data(removed_flask=int(callback.data))

                flasks_id_list = await remove_selected_flask(flasks_id_list, int(callback.data))

            else:
                # Заменяем сегмент на выбранный цвет
                new_caption = FillUndefinedColorsTexts.CHOOSE_COLOR

                await edit_image(callback, state, new_caption)

                logger.log_info(f'Пользователь {callback.from_user.id} заменяет цвет')

                await state.update_data(choosen_color=int(callback.data))

                choosen_flask, choosen_segment = user_data[RedisKeys.CHOOSEN_FLASK], user_data[RedisKeys.CHOOSEN_SEGMENT]
                flasks_id_list = await replace_selected_color(flasks_id_list, int(callback.data), choosen_flask, choosen_segment)

            undef_colors = await replace_undefined(flasks_id_list)
    
            await state.update_data(undefined_colors=undef_colors)
            await state.update_data(flasks_id_list=flasks_id_list)
            await state.update_data(edit_undefined_colors=undef_colors)
            await state.update_data(edit_flasks_id_list=flasks_id_list)
    
            await create_image_for_replace(flasks_id_list=flasks_id_list, id_client=callback.from_user.id)

            # Подготавливаем сообщения для сделанных выше действий
            if current_state == amc.SolveFlasks.remove_flask:
                new_caption = FillUndefinedColorsTexts.SUCCESSFUL_REMOVAL_FLASK
                kb = recognition_check()
                new_state = amc.SolveFlasks.set_color    

            else:
                new_caption = FillUndefinedColorsTexts.SUCESSFUL_REPLACEMENT_COLOR
                kb = recognition_check()
                new_state = amc.SolveFlasks.set_color

            await edit_image(callback, state, new_caption, kb, new_state)

        elif current_state == amc.SolveFlasks.choose_color:

            # Выбираем цвет на который будет изменен выбранный сегмент из списка
            new_caption = FillUndefinedColorsTexts.CHOOSE_COLOR
            kb = change_color()
            new_state = amc.SolveFlasks.confirm_changing

            await state.update_data(choosen_segment=int(callback.data))
            await edit_image(callback, state, new_caption, kb, new_state, fill_color=True)

            logger.log_info(f'Изображение от пользователя {callback.from_user.id} было распознано неверно. Пользователь выбирает новый цвет')


@rtr.message(amc.SolveFlasks.set_color)
async def filling_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме заполнения цветом'''

    logger.log_info(f'Пользователь {message.from_user.id} проигнорировал кнопки')

    msg = await message.answer(FillUndefinedColorsTexts.ERROR_ACTION)
    
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()
