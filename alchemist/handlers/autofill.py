from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
from aiogram.utils.chat_action import ChatActionSender

from random import shuffle

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import autofill_buttons, autofill_options, no_result, upload_new
from found_colors import replace_in_list, create_image_for_replace, add_empty_flask, BreakAction
from transfusion_of_liquids import transfusion_manage
from handlers.send_welcome import check_user

from itertools import permutations


rtr = Router()
logger = amc.ConfigLogger(__name__)


async def reply(callback: CallbackQuery, bot: Bot, state: FSMContext, flasks_id_list: list, keyboard_name: str, new_message: bool):
    '''Функция для вызова поиска решения'''
    data = await state.get_data()
    lvl_file = data['level_file']

    # Подставляем нужную клавиатуру в зависимости от начальной картинки
    if keyboard_name == 'upload_new':
        keyboard = upload_new('upload_new')
    else:
        keyboard = upload_new('upload_new_or_reload')

    async with ChatActionSender.typing(bot=bot, chat_id=callback.from_user.id):
        '''Запускаем процесс поиска решения'''
        # Итоговое изображение
        caption = "I'll look for a solution from this position. Wait, this may take a while"
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

        try:
            # Вызываем функцию перебора переливаний
            is_solved, steps = await transfusion_manage(bot=bot, chat_id=callback.from_user.id, task=flasks_id_list)
        except TelegramBadRequest:
            logger.log_error('Превышено время ожидания ответа на начало поиска решения')

        # В случае, если флаг выставлен в False сообщаем, что решение не найдено, иначе выводим решение
        if not is_solved:
            await callback.message.answer(
                f'😖😖😖I have looked through all possible variants of pouring liquids and unfortunately, it is impossible to find a solution for this arrangement.\nIf you want to change the order of undefined colors, click "🔄️🖼️Update image".\nIf you know all the colors, but the solution is still not found, then I can add another empty flask, for this click "➕🧪Add empty flask"\nOr you can upload a new image, for this click "📩🖼️Upload new image"',
                reply_markup=no_result()
            )
        else:
            await callback.message.answer(
                f'Yay!🥳🥳🥳I found a solution for you!!!🥳🥳🥳\n{steps}\nLet me know if you want a solution for another screenshot :)',
                reply_markup=keyboard
            )
        await state.set_state(amc.SolveFlasks.set_color)


@rtr.callback_query(
    amc.SolveFlasks.set_color,
    F.data.in_(
        [
            'yes', 'autofill', 'previous', 'next', 'confirm', 'reload_image', 'add_an_empty_flask'
        ]
    )
)
async def autofill(callback: CallbackQuery, bot: Bot, state: FSMContext):
    '''Функция выбора режима работы и реализации логики втозаполнения'''
    logger.log_info(f'Пользователь {callback.from_user.id} выбрал режим автозаполнения')
    await check_user(callback.message.from_user.id, state)
    if callback.data in ['yes', 'reload_image', 'add_an_empty_flask']:
        '''Если пользователь подтвердил, что изображение было распознано правильно'''
        # Получаем доступ к сохраненному набору неопределенных цветов
        data = await state.get_data()
        undef_colors, flasks_id_list = data['undefined_colors'], data['flasks_id_list']
        lvl_file = data['level_file']
        new_message = False

        async with ChatActionSender.typing(bot=bot, chat_id=callback.from_user.id):
            if callback.data in ['reload_image', 'add_an_empty_flask']:
                await callback.message.delete()
                new_message = True
                if callback.data == 'add_an_empty_flask':
                    # Добавляем пустую четверть колбы
                    if data['new_segment'] == 0 or data['new_segment'] == 3:
                        idx_segment = 1
                        await state.update_data(new_segment=idx_segment)
                    elif data['new_segment'] < 3:
                        idx_segment = data['new_segment'] + 1
                        await state.update_data(new_segment=idx_segment)
                    flasks_id_list = await add_empty_flask(flasks_id_list=flasks_id_list, idx_segment=idx_segment)
                    await state.update_data(flasks_id_list=flasks_id_list)
                    logger.log_info(f'В изображение пользователя {callback.from_user.id} была добавлена пустая четверть колбы')

                    # Подготавливаем картинку, в которой подсвечиваем неопределенные области
                    await create_image_for_replace(flasks_id_list=flasks_id_list, id_client=callback.from_user.id)

            if not undef_colors:
                await reply(callback, bot, state, flasks_id_list, 'upload_new', new_message)
                return

            if callback.data == 'yes':
                await callback.message.delete()
                await state.update_data(serial_number=0)
            await callback.message.answer(
                "Tell me if you want to fill in the undefined colors manually or should I do it automatically?🙂",
                reply_markup=autofill_buttons()
            )
            await callback.answer()
            return
    
    '''Начало перебора всех решений, генерация картинки и сообщения'''
    # Получаем доступ к сохраненному набору неопределенных цветов
    data = await state.get_data()
    undef_colors = data['undefined_colors']
    lvl_file = data['level_file']

    if callback.data == 'autofill':
        async with ChatActionSender.typing(bot=bot, chat_id=callback.from_user.id):
            await callback.message.edit_text("Now I'll show you my options for filling undefined colors\nYou can switch between all the options until you find the one that suits you")
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

    if callback.data == 'confirm':
        logger.log_info(f'Пользователь {callback.from_user.id} выбрал вариант для поиска решения')
        autofill_flasks_id_list = data['autofill_flasks_id_list']
        await reply(callback, bot, state, autofill_flasks_id_list, 'upload_new_or_reload', False)
        return
    
    autofill_flasks_id_list = data['flasks_id_list']
    data = await state.get_data()
    all_permutations = data['permutations']

    if callback.data in ['previous', 'next']:
        # Отоброжаем промежуточный вариант
        with open(lvl_file, 'rb') as open_image:
            await callback.message.edit_media(
                InputMediaPhoto(
                    media=BufferedInputFile(
                        open_image.read(),
                        filename='solve_flasks'
                    ),
                    caption='Click on one of the buttons below to get another option or select the current option'
                )
            )

    if callback.data == 'previous':
        number = data['serial_number']
        number -= 1
        await state.update_data(serial_number=number)

    if callback.data == 'next':
        if len(all_permutations) == 1:
            shuffle(all_permutations[0])
            await state.update_data(permutations=all_permutations)
        else:
            number = data['serial_number']
            if number < len(all_permutations) - 1:
                number += 1
            await state.update_data(serial_number=number)

    data = await state.get_data()
    all_permutations = data['permutations']
    if len(all_permutations) == 1:
        autofill_variation = all_permutations[0]
    else:
        number = data['serial_number']
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
                        if flask[color] == flask[color + 1] and flask[color] != 20:
                            raise BreakAction
                unique_sequence = True
            except BreakAction:
                pass

        if unique_sequence == False:
            shuffle(autofill_variation)
            data = await state.get_data()
            autofill_flasks_id_list = data['flasks_id_list']
    await state.update_data(autofill_flasks_id_list=autofill_flasks_id_list)

    # Подготавливаем картинку
    await create_image_for_replace(flasks_id_list=autofill_flasks_id_list, id_client=callback.from_user.id)

    if len(all_permutations) == 1:
        mode = 'first'
        caption = 'Click on one of the buttons below to get another option or select the current option'
    else:
        if number == 0:
            mode = 'first'
        elif number == len(all_permutations) - 1:
            mode = 'last'
        else:
            mode = None
        caption = f"Option {number + 1} of {len(all_permutations)}"

    if callback.data in ['previous', 'next']:
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
