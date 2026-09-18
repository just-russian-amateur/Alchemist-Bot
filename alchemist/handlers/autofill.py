from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InputRichMessage, InputRichBlockParagraph
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.chat_action import ChatActionSender

from math import isnan
from random import shuffle

import classes.all_my_classes as amc
from richmessages.all_my_rich_messages import (
    create_rich_msg,
    create_media_msg,
    build_image_msg,
    build_no_result_msg,
    build_upload_file_msg,
    build_pay_attempts_msg,
    build_autofill_options_msg,
    build_select_mode_msg,
    fill_format
)
from found_colors import (
    replace_in_list,
    create_image_for_replace,
    add_empty_flask,
    create_colors_dict,
    EMPTY,
    UNDEFINED
)
from transfusion_of_liquids import transfusion_manage
from texts.all_my_texts import AutofillTexts
from texts.redis_keys import RedisKeys
from callbacks.all_my_callbacks import CallbacksData

from itertools import permutations


rtr = Router()
logger = amc.ConfigLogger(__name__)

class BreakAction(Exception):
    pass


async def reply(
        callback: CallbackQuery,
        bot: Bot,
        state: FSMContext,
        flasks_id_list: list,
        keyboard_name: str
):
    '''Функция для вызова поиска решения'''

    user_data = await state.get_data()

    if RedisKeys.FAIL_ATTEMPTS not in user_data:
        await state.update_data(**{RedisKeys.FAIL_ATTEMPTS: 0})
        user_data = await state.get_data()

    lvl_file = user_data.get(RedisKeys.LVL_FILE)

    # Подставляем нужную клавиатуру в зависимости от начальной картинки
    if keyboard_name == 'upload_new':
        keyboard = build_upload_file_msg('upload_new')
    else:
        keyboard = build_upload_file_msg('upload_new_or_reload')
        
    async with ChatActionSender.typing(bot=bot, chat_id=callback.from_user.id):
        '''
        Запускаем процесс поиска решения
        '''

        # Итоговое изображение
        caption = AutofillTexts.START_FIND_SOLUTION

        with open(lvl_file, 'rb') as open_image:
            await callback.message.edit_text(
                rich_message=InputRichMessage(
                    blocks=create_media_msg(
                        build_image_msg(open_image, 'solve_flasks'),
                        caption
                    )
                )
            )

        await callback.answer()

        logger.log_info(f'Пользователь {callback.from_user.id} заполнил все пустоты')

        colors_dict = create_colors_dict(flasks_id_list)

        if UNDEFINED not in colors_dict and all(key == EMPTY or colors_dict[key] == 4 for key in colors_dict.keys()):
            try:
                # Вызываем функцию перебора переливаний (только если количество сегментов каждого цвета соответствует вместимости колбы)
                is_solved, steps, count_states = await transfusion_manage(flasks_id_list)
            except TelegramBadRequest:
                logger.log_error('Превышено время ожидания ответа на начало поиска решения')

            # В случае, если флаг выставлен в False сообщаем, что решение не найдено, иначе выводим решение
            if not is_solved:
                await state.update_data(**{RedisKeys.FAIL_ATTEMPTS: user_data.get(RedisKeys.FAIL_ATTEMPTS) + 1})

                user_data = await state.get_data()

                await callback.message.edit_text(
                    rich_message=InputRichMessage(
                        blocks=create_rich_msg(
                            fill_format(
                                AutofillTexts.NOT_SOLVED,
                                count_states=count_states
                            ),
                            build_no_result_msg()
                        )
                    )
                )
            else:
                msg_text = [AutofillTexts.SUCCESSFUL_SOLVED[0]] + steps + [AutofillTexts.SUCCESSFUL_SOLVED[1]]

                await callback.message.edit_text(
                    rich_message=InputRichMessage(
                        blocks=create_rich_msg(
                            msg_text,
                            keyboard
                        )
                    )
                )
        else:
            # Выводим сообщение о том, что изображение не подходит для поиска решения
            await callback.message.edit_text(
                rich_message=InputRichMessage(
                    blocks=create_rich_msg(
                        AutofillTexts.BAD_IMAGE,
                        build_upload_file_msg('upload_new')
                    )
                )
            )

        await state.set_state(amc.SolveFlasks.set_color)
    
        # Отнимаем попытку у пользователя только после того, как он получил решение или получил в ответ, что решения нет
        if not isnan(user_data.get(RedisKeys.PAID_ATTEMPTS)) and not isnan(user_data.get(RedisKeys.FREE_ATTEMPTS)):
            if user_data.get(RedisKeys.FAIL_ATTEMPTS) == 3:
                await state.update_data(**{
                    RedisKeys.FAIL_ATTEMPTS: 0,
                    RedisKeys.FREE_ATTEMPTS: user_data.get(RedisKeys.FREE_ATTEMPTS) + 1,
                })
            if user_data.get(RedisKeys.FREE_ATTEMPTS) > 0:
                await state.update_data(**{RedisKeys.FREE_ATTEMPTS: user_data.get(RedisKeys.FREE_ATTEMPTS) - 1})
            else:
                await state.update_data(**{RedisKeys.PAID_ATTEMPTS: user_data.get(RedisKeys.PAID_ATTEMPTS) - 1})


async def current_image_edit(
        callback: CallbackQuery,
        state: FSMContext,
        flasks_id_list: list
):
    '''Функция для обработки случаев с перезагрузкой изображения уровня или добавления к нему пустой колбы'''

    user_data = await state.get_data()

    # Предлагаем купить попытки, если они закончились 
    free_attempts = user_data.get(RedisKeys.FREE_ATTEMPTS)
    paid_attempts = user_data.get(RedisKeys.PAID_ATTEMPTS)

    if free_attempts == 0 and paid_attempts == 0:
        logger.log_info(f'У пользователя {callback.from_user.id} закончились попытки')

        await callback.message.edit_text(
            rich_message=InputRichMessage(
                blocks=create_rich_msg(
                    AutofillTexts.OUT_ATTEMPTS,
                    build_pay_attempts_msg()
                )
            )
        )
        await callback.answer()
        await state.set_state(amc.SolveFlasks.pay_attempts)

        return False

    logger.log_info(f'Изображение от пользователя {callback.from_user.id} отправлено на перезагрузку с/без добавления пустой колбы')

    if callback.data == CallbacksData.EMPTY_FLASK:
        # Добавляем пустую четверть колбы
        if user_data.get(RedisKeys.NEW_SEGMENTS) == 0 or user_data.get(RedisKeys.NEW_SEGMENTS) == 3:
            index_segment = 1
            await state.update_data(**{RedisKeys.NEW_SEGMENTS: index_segment})
        elif user_data.get(RedisKeys.NEW_SEGMENTS) < 3:
            index_segment = user_data.get(RedisKeys.NEW_SEGMENTS) + 1
            await state.update_data(**{RedisKeys.NEW_SEGMENTS: index_segment})

        flasks_id_list = add_empty_flask(
            flasks_id_list,
            idx_segment=index_segment
        )
        await state.update_data(**{RedisKeys.FLASKS_LIST: flasks_id_list})

        logger.log_info(f'В изображение пользователя {callback.from_user.id} была добавлена пустая четверть колбы')

        # Подготавливаем картинку, в которой подсвечиваем неопределенные области
        await create_image_for_replace(
            flasks_id_list,
            id_client=callback.from_user.id
        )


async def get_permutations(state: FSMContext, undef_colors: dict):
    '''Функция для получения списка возможных расположений неопределенных цветов'''

    # Создание списка цветов
    variations = []

    for key in undef_colors.keys():
        for _ in range(undef_colors[key]):
            variations.append(int(key))

    if len(variations) < 5:
        # Получение всевозможных уникальных перестановок
        all_permutations = list(list(permutation) for permutation in set(permutations(variations)))
        await state.update_data(**{RedisKeys.PERMUTATIONS: all_permutations})
    else:
        shuffle(variations)
        await state.update_data(**{RedisKeys.PERMUTATIONS: [variations]})


async def change_permutation(
        callback: CallbackQuery,
        state: FSMContext
) -> tuple[list, list, int | None]:
    '''Функция для обработки логики по переключению текущей расстановки неопределенных цветов, которую выбирает пользователь'''

    number = None
    user_data = await state.get_data()
    autofill_flasks_id_list = user_data.get(RedisKeys.FLASKS_LIST)
    all_permutations = user_data.get(RedisKeys.PERMUTATIONS)

    # Обработка логики переключения между вариациями автоматической расстановки неизвестных цветов
    if callback.data == CallbacksData.PREVIOUS:
        number = user_data.get(RedisKeys.SERIAL_NUMBER)
        number -= 1
        await state.update_data(**{RedisKeys.SERIAL_NUMBER: number})

    if callback.data == CallbacksData.NEXT:
        if len(all_permutations) == 1:
            shuffle(all_permutations[0])
            await state.update_data(**{RedisKeys.PERMUTATIONS: all_permutations})
        else:
            number = user_data.get(RedisKeys.SERIAL_NUMBER)
            if number < len(all_permutations) - 1:
                number += 1   
            await state.update_data(**{RedisKeys.SERIAL_NUMBER: number})

    user_data = await state.get_data()
    all_permutations = user_data.get(RedisKeys.PERMUTATIONS)

    if len(all_permutations) == 1:
        autofill_variation = all_permutations[0]
    else:
        number = user_data.get(RedisKeys.SERIAL_NUMBER)
        autofill_variation = all_permutations[number]

    unique_sequence = False # Флаг для отслеживания перемешки без повторений последовательных цветов

    while not unique_sequence:
        if len(all_permutations) != 1:
            unique_sequence = True

        # Дозаполняем неопределенные места
        for color in autofill_variation:
            replace_in_list(autofill_flasks_id_list, color_id=color)

        if len(all_permutations) == 1:
            try:
                for flask in autofill_flasks_id_list:
                    for color in range(len(flask) - 1):
                        if flask[color] == flask[color + 1] and flask[color] != EMPTY:
                            raise BreakAction
                unique_sequence = True
            except BreakAction:
                pass

        if unique_sequence == False:
            shuffle(autofill_variation)
            user_data = await state.get_data()
            autofill_flasks_id_list = user_data.get(RedisKeys.FLASKS_LIST)

    await state.update_data(**{RedisKeys.AUTOFILL_FLASKS_LIST: autofill_flasks_id_list})

    return autofill_flasks_id_list, all_permutations, number


async def show_permutation(
        callback: CallbackQuery,
        all_permutations: list,
        number: int,
        lvl_file: str
):
    '''Функция для отображения пользователю изображения для выбранного им расположения неопределенных цветов'''

    if len(all_permutations) == 1:
        mode = 'first'
        caption = AutofillTexts.SELECT_START_POSITION
    else:
        if number == 0:
            mode = 'first'
        elif number == len(all_permutations) - 1:
            mode = 'last'
        else:
            mode = None
        caption = [InputRichBlockParagraph(text=f"Option {number + 1} of {len(all_permutations)}")]
        
    # Рисуем картинки с вариантами автозаполнений
    with open(lvl_file, 'rb') as open_image:
        await callback.message.edit_text(
            rich_message=InputRichMessage(
                blocks=create_media_msg(
                    build_image_msg(open_image, 'solve_flasks'),
                    caption,
                    build_autofill_options_msg(mode)
                )
            )
        )

    await callback.answer()


@rtr.callback_query(
    amc.SolveFlasks.set_color,
    F.data.in_(
        [
            CallbacksData.YES, CallbacksData.AUTOFILL, CallbacksData.PREVIOUS, CallbacksData.NEXT,
            CallbacksData.CONFIRM, CallbacksData.RELOAD_IMAGE, CallbacksData.EMPTY_FLASK
        ]
    )
)
async def autofill(
        callback: CallbackQuery,
        bot: Bot,
        state: FSMContext
):
    '''Функция выбора режима работы и реализации логики втозаполнения'''

    logger.log_info(f'Пользователь {callback.from_user.id} выбрал режим автозаполнения')

    if callback.data in [CallbacksData.YES, CallbacksData.RELOAD_IMAGE, CallbacksData.EMPTY_FLASK]:
        '''Если пользователь подтвердил, что изображение было распознано правильно'''

        # Получаем доступ к сохраненному набору неопределенных цветов
        user_data = await state.get_data()
        undef_colors = user_data.get(RedisKeys.UNDEF_COLORS)
        flasks_id_list = user_data.get(RedisKeys.FLASKS_LIST)

        if callback.data in [CallbacksData.RELOAD_IMAGE, CallbacksData.EMPTY_FLASK]:
            await current_image_edit(
                callback,
                state,
                flasks_id_list
            )

        if not undef_colors:
            await reply(
                callback,
                bot,
                state,
                flasks_id_list,
                keyboard_name='upload_new'
            )

            return

        if callback.data == CallbacksData.YES:
            await state.update_data(**{RedisKeys.SERIAL_NUMBER: 0})

        await callback.message.edit_text(
            rich_message=InputRichMessage(
                blocks=create_rich_msg(
                    AutofillTexts.SELECT_MODE,
                    build_select_mode_msg()
                )
            )
        )
        await callback.answer()

        return
    
    '''Начало перебора всех решений, генерация картинки и сообщения'''

    # Получаем доступ к сохраненному набору неопределенных цветов
    user_data = await state.get_data()
    undef_colors = user_data.get(RedisKeys.UNDEF_COLORS)
    current_level = user_data.get(RedisKeys.LVL_FILE)

    if callback.data == CallbacksData.AUTOFILL:
        await get_permutations(state, undef_colors)

    if callback.data == CallbacksData.CONFIRM:
        logger.log_info(f'Пользователь {callback.from_user.id} выбрал вариант для поиска решения')

        autofill_flasks_id_list = user_data.get(RedisKeys.AUTOFILL_FLASKS_LIST)

        await reply(
            callback,
            bot,
            state,
            autofill_flasks_id_list,
            keyboard_name='upload_new_or_reload'
        )

        return

    autofill_flasks_id_list, permutations, permutation_number = await change_permutation(callback, state)

    # Подготавливаем и отображаем картинку пользователю
    await create_image_for_replace(
        autofill_flasks_id_list,
        id_client=callback.from_user.id
    )

    await show_permutation(
        callback,
        all_permutations=permutations,
        number=permutation_number,
        lvl_file=current_level
    )
