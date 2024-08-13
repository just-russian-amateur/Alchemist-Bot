from aiogram import Bot, Router, F  # Подключение библиотек
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender

from found_colors import found_colors_in_flasks, create_image_for_replace, replace_in_list
import classes.all_my_classes as amc
from keyboards.all_my_keyboards import error_image, recognition_check

import asyncio
import os


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.message(
    amc.SolveFlasks.send_photo,
    F.photo
)
async def get_photo(message: Message, bot: Bot, state: FSMContext):
    '''Функция получения и обработки фотографий'''
    async with ChatActionSender.upload_photo(bot=bot, chat_id=message.chat.id):
        # Создание папки со скриншотами и папки для временных изображений в папке с id пользователя
        this_path = f'./{message.from_user.id}'
        if not os.path.isdir(f'{this_path}/images'):
            os.mkdir(f'{this_path}/images')
        if not os.path.isdir(f'{this_path}/tmp'):
            os.mkdir(f'{this_path}/tmp')

        image_for_load = f'{this_path}/images/{message.photo[-1].file_id}.jpg'   # Сохраняем на всякий случай путь к картинке
        lvl_file = f'{this_path}/tmp/level_for_{message.from_user.id}.jpg'
        # Сохраняем пути в машину состояний
        await state.update_data(original_image=image_for_load)
        await state.update_data(level_file=lvl_file)
        # Загрузка фото в буфер для последующей обработки
        await bot.download(
            message.photo[-1],
            destination=image_for_load
        )
        logger.log_info(f'Пользователь {message.from_user.id} отправил фото')
    
        try:
            # Распознаем цвета и добавляем их в список с последующей сериализации в json
            undef_colors, flasks_list = await found_colors_in_flasks(image_for_search=image_for_load, id_client=message.from_user.id)
            await state.update_data(undefined_colors=undef_colors)
            await state.update_data(flasks_list=flasks_list)
        except:
            # Если есть любое прерывание во время распознавания, то просим пользователя загрузить новое фото
            # (генерация прерывания говорит о том, что фото не является скриншотом колб или не соответствует условиям)
            await message.answer(
                'Something went wrong...🤷‍♂️ Please upload another picture',
                reply_markup=error_image()
            )
            logger.log_error('Изображение не подходит для распознавания')
            await state.set_state(amc.SolveFlasks.start_solving)
            return
        
        # Автозаполнение цвета, если остался только один неопределенный
        if len(undef_colors) == 1:
            for variation in undef_colors:
                while undef_colors[variation] != 0:
                    undef_colors[variation] -= 1
                    flasks_list = await replace_in_list(flasks_list=flasks_list, color_name=variation)
            undef_colors.pop(variation)
            await state.update_data(undefined_colors=undef_colors)
            await state.update_data(flasks_list=flasks_list)

        # Подготавливаем картинку, в которой подсвечиваем неопределенные области
        await create_image_for_replace(flasks_list=flasks_list, id_client=message.from_user.id)

        # Изображение, где подсвечивается первый неопределенный цвет
        with open(lvl_file, 'rb') as open_image:
            await message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption="This is what I saw in your screenshot. Compare the colors here with the original image and please tell me if I succeeded so I can continue with the solution. If something is wrong, I can try again, or you can send this screenshot for feedback using the /support command🙂",
                reply_markup=recognition_check()
            )
        await state.set_state(amc.SolveFlasks.set_color)


@rtr.message(amc.SolveFlasks.send_photo)
async def sending_photo_incorrectly(message: Message):
    '''Функция для отслеживания любых действий кроме отправки фото'''
    logger.log_info(f'Пользователь {message.from_user.id} отправил что-то кроме фото')
    msg = await message.answer('Send a photo please')
    await asyncio.sleep(10)
    await message.delete()
    await msg.delete()
