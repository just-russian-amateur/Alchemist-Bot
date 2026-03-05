from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.chat_action import ChatActionSender

from math import isnan
from random import shuffle

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import autofill_buttons, autofill_options, no_result, upload_new, pay_attempts
from found_colors import replace_in_list, create_image_for_replace, add_empty_flask, create_colors_dict, EMPTY, UNDEFINED
from transfusion_of_liquids import transfusion_manage
from texts.all_my_texts import AutofillTexts
from texts.redis_keys import RedisKeys
from callbacks.all_my_callbacks import CallbacksData

from itertools import permutations


rtr = Router()
logger = amc.ConfigLogger(__name__)

class BreakAction(Exception):
    pass


async def reply(callback: CallbackQuery, bot: Bot, state: FSMContext, flasks_id_list: list, keyboard_name: str, new_message: bool):
    '''Функция для вызова поиска решения'''

    user_data = await state.get_data()

    if not RedisKeys.FAIL_ATTEMPTS in user_data:
        await state.update_data(count_fail_attempts=0)
        user_data = await state.get_data()

    lvl_file = user_data[RedisKeys.LVL_FILE]

    # Подставляем нужную клавиатуру в зависимости от начальной картинки
    if keyboard_name == 'upload_new':
        keyboard = upload_new('upload_new')
        
    else:
        keyboard = upload_new('upload_new_or_reload')
        
    async with ChatActionSender.typing(bot=bot, chat_id=callback.from_user.id):
        
        '''
        Запускаем процесс поиска решения
        '''

        # Итоговое изображение
        caption = AutofillTexts.START_FIND_SOLUTION

        if new_message == False:

            with open(lvl_file, 'rb') as open_image:
                await callback.message.edit_media(
                    InputMediaPhoto(
                        media=BufferedInputFile(
                            open_image.read(),
                            filename='solve_flasks'
                        ),
                        caption=caption
                    )
                )

        else:

            with open(lvl_file, 'rb') as open_image:
                await callback.message.answer_photo(
                    BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption=caption
                )

        await callback.answer()

        logger.log_info(f'Пользователь {callback.from_user.id} заполнил все пустоты')

        colors_dict = await create_colors_dict(flasks_id_list)

        if UNDEFINED not in colors_dict and all(key == EMPTY or colors_dict[key] == 4 for key in colors_dict.keys()):

            try:
                # Вызываем функцию перебора переливаний (только если количество сегментов каждого цвета соответствует вместимости колбы)
                is_solved, steps, count_states = await transfusion_manage(flasks_id_list)

            except TelegramBadRequest:
                logger.log_error('Превышено время ожидания ответа на начало поиска решения')

            # В случае, если флаг выставлен в False сообщаем, что решение не найдено, иначе выводим решение
            if not is_solved:
                await state.update_data(count_fail_attempts=user_data[RedisKeys.FAIL_ATTEMPTS] + 1)

                user_data = await state.get_data()

                await callback.message.answer(
                    AutofillTexts.NOT_SOLVED.format(count_states=count_states),
                    parse_mode='HTML',
                    reply_markup=no_result()
                )

            else:
                await callback.message.answer(
                    AutofillTexts.SUCCESSFUL_SOLVED.format(steps=steps),
                    reply_markup=keyboard
                )

        else:
            # Выводим сообщение о том, что изображение не подходит для поиска решения
            await callback.message.answer(
                AutofillTexts.BAD_IMAGE,
                reply_markup=upload_new('upload_new')
            )

        await state.set_state(amc.SolveFlasks.set_color)
    
        # Отнимаем попытку у пользователя только после того, как он получил решение или получил в ответ, что решения нет
        if not isnan(user_data[RedisKeys.PAID_ATTEMPTS]) and not isnan(user_data[RedisKeys.FREE_ATTEMPTS]):

            if user_data[RedisKeys.FAIL_ATTEMPTS] == 3:
                await state.update_data(count_fail_attempts=0)
                await state.update_data(count_free_attempts=user_data[RedisKeys.FREE_ATTEMPTS] + 1)
            if user_data[RedisKeys.FREE_ATTEMPTS] > 0:
                await state.update_data(count_free_attempts=user_data[RedisKeys.FREE_ATTEMPTS] - 1)
            else:
                await state.update_data(count_paid_attempts=user_data[RedisKeys.PAID_ATTEMPTS] - 1)


@rtr.callback_query(
    amc.SolveFlasks.set_color,
    F.data.in_(
        [
            CallbacksData.YES, CallbacksData.AUTOFILL, CallbacksData.PREVIOUS, CallbacksData.NEXT,
            CallbacksData.CONFIRM, CallbacksData.RELOAD_IMAGE, CallbacksData.EMPTY_FLASK
        ]
    )
)
async def autofill(callback: CallbackQuery, bot: Bot, state: FSMContext):
    '''Функция выбора режима работы и реализации логики втозаполнения'''

    logger.log_info(f'Пользователь {callback.from_user.id} выбрал режим автозаполнения')

    if callback.data in [CallbacksData.YES, CallbacksData.RELOAD_IMAGE, CallbacksData.EMPTY_FLASK]:

        '''
        Если пользователь подтвердил, что изображение было распознано правильно
        '''

        # Получаем доступ к сохраненному набору неопределенных цветов
        user_data = await state.get_data()
        undef_colors, flasks_id_list = user_data[RedisKeys.UNDEF_COLORS], user_data[RedisKeys.FLASKS_LIST]
        lvl_file = user_data[RedisKeys.LVL_FILE]
        new_message = False

        async with ChatActionSender.typing(bot=bot, chat_id=callback.from_user.id):
            if callback.data in [CallbacksData.RELOAD_IMAGE, CallbacksData.EMPTY_FLASK]:

                # Предлагаем купить попытки, если они закончились 
                await callback.message.delete()

                new_message = True
                free_attempts = user_data[RedisKeys.FREE_ATTEMPTS]
                paid_attempts = user_data[RedisKeys.PAID_ATTEMPTS]

                if free_attempts == 0 and paid_attempts == 0:

                    logger.log_info(f'У пользователя {callback.from_user.id} закончились попытки')

                    await callback.message.answer(
                        AutofillTexts.OUT_ATTEMPTS,
                        reply_markup=pay_attempts()
                    )

                    await callback.answer()
                    await state.set_state(amc.SolveFlasks.pay_attempts)
                    return

                else:

                    if not isnan(free_attempts) and not isnan(paid_attempts):
                        if paid_attempts > 0 and free_attempts > 0:
                            msg_text = AutofillTexts.RELOAD_FREE_PAID.format(free_attempts=free_attempts, paid_attempts=paid_attempts)
                        elif paid_attempts == 0 and free_attempts > 0:
                            msg_text = AutofillTexts.RELOAD_FREE.format(free_attempts=free_attempts)
                        elif paid_attempts > 0 and free_attempts == 0:
                            msg_text = AutofillTexts.RELOAD_PAID.format(paid_attempts=paid_attempts)
                        await callback.message.answer(msg_text)

                    await callback.answer()

                logger.log_info(f'Изображение от пользователя {callback.from_user.id} отправлено на перезагрузку с/без добавления пустой колбы')
            
                if callback.data == CallbacksData.EMPTY_FLASK:
                    
                    # Добавляем пустую четверть колбы
                    if user_data[RedisKeys.NEW_SEGMENTS] == 0 or user_data[RedisKeys.NEW_SEGMENTS] == 3:
                        idx_segment = 1
                        await state.update_data(new_segment=idx_segment)
                    elif user_data[RedisKeys.NEW_SEGMENTS] < 3:
                        idx_segment = user_data[RedisKeys.NEW_SEGMENTS] + 1
                        await state.update_data(new_segment=idx_segment)

                    flasks_id_list = await add_empty_flask(flasks_id_list=flasks_id_list, idx_segment=idx_segment)
                    await state.update_data(flasks_id_list=flasks_id_list)

                    logger.log_info(f'В изображение пользователя {callback.from_user.id} была добавлена пустая четверть колбы')

                    # Подготавливаем картинку, в которой подсвечиваем неопределенные области
                    await create_image_for_replace(flasks_id_list=flasks_id_list, id_client=callback.from_user.id)

            if not undef_colors:
                await reply(callback, bot, state, flasks_id_list, 'upload_new', new_message)
                return

            if callback.data == CallbacksData.YES:
                await callback.message.delete()
                await state.update_data(serial_number=0)
            
            await callback.message.answer(
                AutofillTexts.SELECT_MODE,
                reply_markup=autofill_buttons()
            )

            await callback.answer()
            return
    
    '''Начало перебора всех решений, генерация картинки и сообщения'''
    # Получаем доступ к сохраненному набору неопределенных цветов
    user_data = await state.get_data()
    undef_colors = user_data[RedisKeys.UNDEF_COLORS]
    lvl_file = user_data[RedisKeys.LVL_FILE]

    if callback.data == CallbacksData.AUTOFILL:
        async with ChatActionSender.typing(bot=bot, chat_id=callback.from_user.id):

            await callback.message.edit_text(AutofillTexts.PREPARING_START_POSITION)

            # Создание списка цветов
            variations = []

            for key in undef_colors.keys():
                for _ in range(undef_colors[key]):
                    variations.append(int(key))

            if len(variations) < 5:
                # Получение всевозможных уникальных перестановок
                all_permutations = list(list(permutation) for permutation in set(permutations(variations)))
                await state.update_data(permutations=all_permutations)
            else:
                shuffle(variations)
                await state.update_data(permutations=[variations])

            await callback.answer()

    if callback.data == CallbacksData.CONFIRM:
        logger.log_info(f'Пользователь {callback.from_user.id} выбрал вариант для поиска решения')

        autofill_flasks_id_list = user_data[RedisKeys.AUTOFILL_FLASKS_LIST]

        await reply(callback, bot, state, autofill_flasks_id_list, 'upload_new_or_reload', False)
        return
    
    autofill_flasks_id_list = user_data[RedisKeys.FLASKS_LIST]
    user_data = await state.get_data()
    all_permutations = user_data[RedisKeys.PERMUTATIONS]

    if callback.data in [CallbacksData.PREVIOUS, CallbacksData.NEXT]:

        # Отоброжаем промежуточный вариант
        with open(lvl_file, 'rb') as open_image:
            await callback.message.edit_media(
                InputMediaPhoto(
                    media=BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption=AutofillTexts.SELECT_START_POSITION
                )
            )

    # Обработка логики переключения между вариациями автоматической расстановки неизвестных цветов
    if callback.data == CallbacksData.PREVIOUS:

        number = user_data[RedisKeys.SERIAL_NUMBER]
        number -= 1
        await state.update_data(serial_number=number)

    if callback.data == CallbacksData.NEXT:

        if len(all_permutations) == 1:
            shuffle(all_permutations[0])
            await state.update_data(permutations=all_permutations)

        else:
            number = user_data[RedisKeys.SERIAL_NUMBER]
            if number < len(all_permutations) - 1:
                number += 1   
            await state.update_data(serial_number=number)

    user_data = await state.get_data()
    all_permutations = user_data[RedisKeys.PERMUTATIONS]

    if len(all_permutations) == 1:
        autofill_variation = all_permutations[0]

    else:
        number = user_data[RedisKeys.SERIAL_NUMBER]
        autofill_variation = all_permutations[number]

    unique_sequence = False # Флаг для отслеживания перемешки без повторений последовательных цветов

    while not unique_sequence:

        if len(all_permutations) != 1:
            unique_sequence = True

        # Дозаполняем неопределенные места
        for color in autofill_variation:
            await replace_in_list(autofill_flasks_id_list, color)

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
            autofill_flasks_id_list = user_data[RedisKeys.FLASKS_LIST]

    await state.update_data(autofill_flasks_id_list=autofill_flasks_id_list)

    # Подготавливаем картинку
    await create_image_for_replace(flasks_id_list=autofill_flasks_id_list, id_client=callback.from_user.id)

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
        caption = f"Option {number + 1} of {len(all_permutations)}"
        
    if callback.data in [CallbacksData.PREVIOUS, CallbacksData.NEXT]:

        # Рисуем картинки с вариантами автозаполнений
        with open(lvl_file, 'rb') as open_image:
            await callback.message.edit_media(
                InputMediaPhoto(
                    media=BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption=caption
                ),
                reply_markup=autofill_options(mode)
            )
            
    else:
        async with ChatActionSender.upload_photo(bot=bot, chat_id=callback.from_user.id):

            # Рисуем картинку после первого автозаполнения
            with open(lvl_file, 'rb') as open_image:
                await callback.message.answer_photo(
                    BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption=caption,
                    reply_markup=autofill_options(mode)
                )

    await callback.answer()
