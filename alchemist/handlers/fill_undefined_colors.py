from aiogram import Bot, Router, F
from aiogram.types import Message, CallbackQuery, InputRichMessage
from aiogram.fsm.context import FSMContext

from io import BytesIO

from found_colors import (
    replace_in_list,
    create_image_for_replace,
    replace_selected_color,
    replace_undefined,
    remove_selected_flask
)
import classes.all_my_classes as amc
from richmessages.all_my_rich_messages import (
    create_media_msg,
    build_image_msg,
    build_collage_msg,
    build_colors_msg,
    build_change_flask_msg,
    build_change_segment_msg,
    build_change_color_msg,
    build_recognition_img_msg
)
from handlers.autofill import reply
from handlers.start_solving import check_attempts
from texts.all_my_texts import FillUndefinedColorsTexts
from texts.redis_keys import RedisKeys
from callbacks.all_my_callbacks import CallbacksData

import asyncio
import os


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def edit_image(
        callback: CallbackQuery,
        state: FSMContext,
        new_caption: list,
        keyboard=None,
        new_state=None,
        fill_color=False
):
    '''Функция для изменения надписей под изображением'''

    # Получаем данные с путями к файлам
    user_data = await state.get_data()
    lvl_file = user_data.get(RedisKeys.LVL_FILE)

    if fill_color:
        collage = []

        # Создаем коллаж из изображения и примеров цветов для заполнения
        with open(lvl_file, 'rb') as lvl_image:
            collage.append((BytesIO(lvl_image.read()), 'solve_flasks'))

        with open('color_examples.jpg', 'rb') as colors_image:
            collage.append((BytesIO(colors_image.read()), 'color_examples'))

        await callback.message.edit_text(
            rich_message=InputRichMessage(
                blocks=create_media_msg(
                    build_collage_msg(collage),
                    new_caption,
                    keyboard
                )
            )
        )
    else:
        with open(lvl_file, 'rb') as open_image:
            await callback.message.edit_text(
                rich_message=InputRichMessage(
                    blocks=create_media_msg(
                        build_image_msg(open_image, 'solve_flasks'),
                        new_caption,
                        keyboard
                    )
                )
            )

    if new_state:
        await state.set_state(new_state)

    await callback.answer()


async def replace_undefined_color(
        callback: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        user_data: dict
):
    '''Функция для обработки изменений цветов на изображении'''
        
    edit_undef_colors = user_data.get(RedisKeys.EDITED_UNDEF_COLORS)
    edit_flasks_id_list = user_data.get(RedisKeys.EDITED_FLASKS_LIST)

    # Удаление цвета нажатой кнопки из словаря и замена неопределенного цвета цветом кнопки
    if edit_undef_colors:
        edit_undef_colors[callback.data] -= 1

        if edit_undef_colors[callback.data] == 0:
            edit_undef_colors.pop(callback.data)

        edit_flasks_id_list = replace_in_list(
            edit_flasks_id_list,
            color_id=int(callback.data)
        )
        
        await state.update_data(**{
            RedisKeys.EDITED_UNDEF_COLORS: edit_undef_colors,
            RedisKeys.EDITED_FLASKS_LIST: edit_flasks_id_list,
        })
        
    # Автозаполнение цвета, если остался только один неопределенный
    if len(edit_undef_colors) == 1:
        while edit_undef_colors[list(edit_undef_colors.keys())[0]] > 0:
            edit_undef_colors[list(edit_undef_colors.keys())[0]] -= 1
            edit_flasks_id_list = replace_in_list(
                edit_flasks_id_list,
                color_id=int(list(edit_undef_colors.keys())[0])
            )

        edit_undef_colors.pop(list(edit_undef_colors.keys())[0])

        await state.update_data(**{
            RedisKeys.EDITED_UNDEF_COLORS: edit_undef_colors,
            RedisKeys.EDITED_FLASKS_LIST: edit_flasks_id_list,
        })

    # Подготавливаем картинку, в которой подсвечиваем неопределенные области
    await create_image_for_replace(
        edit_flasks_id_list,
        id_client=callback.from_user.id
    )

    if edit_undef_colors:
        # Изображение, где подсвечивается первый неопределенный цвет
        new_caption = FillUndefinedColorsTexts.MANUALLY_FILLING
        kb = build_colors_msg(edit_undef_colors)

        await edit_image(callback, state, new_caption, kb)

        logger.log_info(f'Изображение для пользователя {callback.from_user.id} дополнено и отправлено для дальнейшего редактирования')
    else:
        await reply(
            callback,
            bot,
            state,
            edit_flasks_id_list,
            keyboard_name='upload_new_or_reload'
        )


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
async def fill_undefined_values(
        callback: CallbackQuery,
        bot: Bot,
        state: FSMContext
):
    '''Функция дозаполнения неопределенных цветов вручную'''

    # Получаем данные с путями к файлам
    current_state = await state.get_state()
    user_data = await state.get_data()
    image_for_load = user_data.get(RedisKeys.IMAGE)
    lvl_file = user_data.get(RedisKeys.LVL_FILE)

    if current_state == amc.SolveFlasks.set_color:
        if callback.data == CallbacksData.UPLOAD_IMAGE:
            # Удаление временных файлов
            if os.path.isfile(image_for_load):
                os.remove(image_for_load)
            if os.path.isfile(lvl_file):
                os.remove(lvl_file)

            # Проверяем, что пользователь может использовать бота
            await check_attempts(user_data, callback, state)
            await callback.answer()

            return
        elif callback.data in [CallbacksData.NO, CallbacksData.REMOVE_FLASK]:
            '''
            Распознавание завершилось с ошибкой, выбираем колбу для замены цвета
            '''

            flasks_id_list = user_data.get(RedisKeys.FLASKS_LIST)
            caption = FillUndefinedColorsTexts.CHOOSE_FLASK
            kb = build_change_flask_msg(len(flasks_id_list))

            if callback.data == CallbacksData.NO:
                new_state = amc.SolveFlasks.choose_segment
            else:
                new_state = amc.SolveFlasks.remove_flask

            await edit_image(
                callback,
                state,
                new_caption=caption,
                keyboard=kb,
                new_state=new_state
            )

            logger.log_info(f'Изображение от пользователя {callback.from_user.id} было распознано неверно. Пользователь выбрал изменение проблемных цветов')
            
            return
        elif callback.data == CallbacksData.MANUALLY:
            '''
            Выбрано заполнение неизвестных цветов вручную
            '''

            undef_colors = user_data.get(RedisKeys.UNDEF_COLORS)
            flasks_id_list = user_data.get(RedisKeys.FLASKS_LIST)

            await state.update_data(**{
                RedisKeys.EDITED_UNDEF_COLORS: undef_colors,
                RedisKeys.EDITED_FLASKS_LIST: flasks_id_list,
            })

            # Подготавливаем картинку, в которой подсвечиваем неопределенные области
            await create_image_for_replace(
                flasks_id_list,
                id_client=callback.from_user.id
            )

            caption = FillUndefinedColorsTexts.MANUALLY_FILLING
            kb = build_colors_msg(undef_colors)

            await edit_image(
                callback,
                state,
                new_caption=caption,
                keyboard=kb,
                fill_color=True
            )

            return
        
        await replace_undefined_color(
            callback,
            bot,
            state,
            user_data
        )
    else:
        if current_state == amc.SolveFlasks.choose_segment:
            # Выбираем сегмент внутри выбранной колбы для замены
            await state.update_data(**{RedisKeys.CHOOSEN_FLASK: int(callback.data)})

            caption = FillUndefinedColorsTexts.CHOOSE_SEGMENT
            kb = build_change_segment_msg()
            new_state = amc.SolveFlasks.choose_color

            await edit_image(
                callback,
                state,
                new_caption=caption,
                keyboard=kb,
                new_state=new_state
            )

            logger.log_info(f'Изображение от пользователя {callback.from_user.id} было распознано неверно. Пользователь выбирает сегмент для изменения')
        elif current_state == amc.SolveFlasks.remove_flask or current_state == amc.SolveFlasks.confirm_changing:
            flasks_id_list = user_data.get(RedisKeys.FLASKS_LIST)
            
            if current_state == amc.SolveFlasks.remove_flask:
                # Удаляем выбранную колбу целиком
                logger.log_info(f'Пользователь {callback.from_user.id} удаляет колбу')

                await state.update_data(**{RedisKeys.REMOVED_FLASK: int(callback.data)})

                flasks_id_list = remove_selected_flask(
                    flasks_id_list,
                    choosen_flask=int(callback.data)
                )
            else:
                # Заменяем сегмент на выбранный цвет
                caption = FillUndefinedColorsTexts.CHOOSE_COLOR

                await edit_image(
                    callback,
                    state,
                    new_caption=caption
                )

                logger.log_info(f'Пользователь {callback.from_user.id} заменяет цвет')

                await state.update_data(**{RedisKeys.CHOOSEN_COLOR: int(callback.data)})

                target_flask = user_data.get(RedisKeys.CHOOSEN_FLASK)
                target_segment = user_data.get(RedisKeys.CHOOSEN_SEGMENT)
                flasks_id_list = replace_selected_color(
                    flasks_id_list,
                    color_id=int(callback.data),
                    choosen_flask=target_flask,
                    choosen_segment=target_segment
                )

            undef_colors = replace_undefined(flasks_id_list)
    
            await state.update_data(**{
                RedisKeys.UNDEF_COLORS: undef_colors,
                RedisKeys.FLASKS_LIST: flasks_id_list,
                RedisKeys.EDITED_UNDEF_COLORS: undef_colors,
                RedisKeys.EDITED_FLASKS_LIST: flasks_id_list,
            })
    
            await create_image_for_replace(
                flasks_id_list,
                id_client=callback.from_user.id
            )

            # Подготавливаем сообщения для сделанных выше действий
            if current_state == amc.SolveFlasks.remove_flask:
                caption = FillUndefinedColorsTexts.SUCCESSFUL_REMOVAL_FLASK
            else:
                caption = FillUndefinedColorsTexts.SUCESSFUL_REPLACEMENT_COLOR

            kb = build_recognition_img_msg()
            new_state = amc.SolveFlasks.set_color

            await edit_image(
                callback,
                state,
                new_caption=caption,
                keyboard=kb,
                new_state=new_state
            )
        elif current_state == amc.SolveFlasks.choose_color:
            # Выбираем цвет на который будет изменен выбранный сегмент из списка
            caption = FillUndefinedColorsTexts.CHOOSE_COLOR
            kb = build_change_color_msg()
            new_state = amc.SolveFlasks.confirm_changing

            await state.update_data(**{RedisKeys.CHOOSEN_SEGMENT: int(callback.data)})
            await edit_image(
                callback,
                state,
                new_caption=caption,
                keyboard=kb,
                new_state=new_state,
                fill_color=True
            )

            logger.log_info(f'Изображение от пользователя {callback.from_user.id} было распознано неверно. Пользователь выбирает новый цвет')


@rtr.message(amc.SolveFlasks.set_color)
async def filling_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме заполнения цветом'''

    logger.log_info(f'Пользователь {message.from_user.id} проигнорировал кнопки')

    msg = await message.answer(FillUndefinedColorsTexts.ERROR_ACTION)
    
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()
