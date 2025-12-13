from aiogram import Bot, Router, F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender

from found_colors import found_colors_in_flasks, create_image_for_replace, replace_in_list
import classes.all_my_classes as amc
from keyboards.all_my_keyboards import error_image, recognition_check

import asyncio


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.message(
    amc.SolveFlasks.send_photo,
    F.photo
)
async def get_photo(message: Message, bot: Bot, state: FSMContext):
    '''Функция получения и обработки фотографий'''
    async with ChatActionSender.upload_photo(bot=bot, chat_id=message.chat.id):
        image_for_load = f'./tmp/{message.from_user.id}.jpg'   # Сохраняем на всякий случай путь к картинке
        lvl_file = f'./tmp/level_for_{message.from_user.id}.jpg'
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
            # Распознаем цвета и добавляем их в список
            undef_colors, flasks_id_list = await found_colors_in_flasks(image_for_search=image_for_load)
            await state.update_data(undefined_colors=undef_colors)
            await state.update_data(flasks_id_list=flasks_id_list)
            await state.update_data(edit_undefined_colors=undef_colors)
            await state.update_data(edit_flasks_id_list=flasks_id_list)
        except:
            # Если есть любое прерывание во время распознавания, то просим пользователя загрузить новое фото
            # (генерация прерывания говорит о том, что фото не является скриншотом колб или не соответствует условиям)
            await message.answer(
                'Something went wrong...🤷‍♂️ Please take a new screenshot of the current level and upload it again or send another screenshot',
                reply_markup=error_image()
            )
            logger.log_error('Изображение не подходит для распознавания')
            await state.set_state(amc.SolveFlasks.start_solving)
            return
        
        # Автозаполнение цвета, если остался только один неопределенный
        if len(undef_colors) == 1:
            while undef_colors[list(undef_colors.keys())[0]] != 0:
                undef_colors[list(undef_colors.keys())[0]] -= 1
                flasks_id_list = await replace_in_list(flasks_id_list=flasks_id_list, color_id=list(undef_colors.keys())[0])
            undef_colors.pop(list(undef_colors.keys())[0])
            await state.update_data(undefined_colors=undef_colors)
            await state.update_data(flasks_id_list=flasks_id_list)

        # Подготавливаем картинку, в которой подсвечиваем неопределенные области
        await create_image_for_replace(flasks_id_list=flasks_id_list, id_client=message.from_user.id)

        # Изображение, где подсвечивается первый неопределенный цвет
        with open(lvl_file, 'rb') as open_image:
            await message.answer_photo(
                BufferedInputFile(
                    open_image.read(),
                    filename='solve_flasks'
                ),
                caption="This is what I saw in your screenshot. Compare the colors here with the original image and please tell me if I succeeded so I can continue with the solution. You can also add an empty segment right away if you think it is necessary (the image is considered correctly recognized in this case)! If something is wrong, I can try again, or you can send this screenshot for feedback using the /support command🙂\nYou can also read about how to solve the most common recognition problems yourself using the /faq command🙂",
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
