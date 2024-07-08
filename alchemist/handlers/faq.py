from aiogram import Router  # Подключение библиотек
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import continue_solving


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.message(Command('faq'))  # Команда для вызова справки по решению часто возникающих проблем
async def faq_message(message: Message, state: FSMContext):
    '''Функция для описания решения всех наиболее распространенных проблем при работе с ботом'''
    logger.log_info(f'Пользователем {message.from_user.id} была вызвана справка по решению проблем')
    current_state = await state.get_state()
    await message.delete()
    await message.answer(
        "Here is a list of the most common problems when working with me and ways to solve them🙂:\n\n❔<b>Problem: I don't respond to clicking buttons or sending screenshots.</b>\n✅<b>Solution:</b> I may not have enough memory to remember the actions of all users and then I reboot my mind. Give me 10 seconds to breathe and try again, I'll be ready🙂\n\n❔<b>Problem: You receive a message: Something went wrong...🤷‍♂️ Please upload another picture.</b>\n✅<b>Solution:</b> Sometimes I may be mistaken in recognizing the contents of your picture and I will inform you about this. Just retake a screenshot of the level and send me the updated screenshot🙂\n\n❔<b>Problem: You receive a response image in which not all the colors are in the right place.</b>\n✅<b>Solution:</b> As I said, sometimes my eyesight fails me and I may not see some colors in your picture, so I show you what I could see. To help me see everything correctly, you can also just take a screenshot again and send it to me, giving me a second chance. Also, before sending the screenshot, make sure that you have not edited it in any way (you have not changed the contrast, sharpness or other parameters of the original image) and the screenshot meets all the requirements that are described in the welcome message from me🙂\n\nIf your problem has not been resolved after these steps, then you can write to my developer using the /support command",
        parse_mode='HTML',
        reply_markup=continue_solving()
    )
    if current_state == amc.SolveFlasks.send_photo:
        await state.set_state(amc.SolveFlasks.start_solving)
