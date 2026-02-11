from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

import classes.all_my_classes as amc
from keyboards.all_my_keyboards import ok


rtr = Router()
logger = amc.ConfigLogger(__name__)


@rtr.message(Command('terms'))  # Команда для показа пользовательского соглашения
async def terms(message: Message):
    '''Функция для показа пользовательского соглашения'''
    logger.log_info(f'Пользователем {message.from_user.id} был вызван показ пользовательского соглашения')
    await message.delete()
    await message.answer(
        'By starting to work with me you agree to the <a href="https://just-russian-amateur.github.io/terms_for_alchemist_bot/Terms_of_Service.html">User Agreement</a> and <a href="https://just-russian-amateur.github.io/terms_for_alchemist_bot/Privacy_Policy.html">Privacy Policy</a>\n\nYou can ask my developer any questions you have regarding the operation of the bot or the payment system through the feedback system using the command /support🙂\n\nAfter clicking the button below you can continue from where you left off',
        parse_mode='HTML',
        reply_markup=ok()
    )


@rtr.callback_query(
    amc.SolveFlasks.start_solving,
    F.data == 'terms'
)
async def terms(callback: CallbackQuery):
    '''Функция для показа пользовательского соглашения'''
    logger.log_info(f'Пользователем {callback.from_user.id} был вызван показ пользовательского соглашения')
    await callback.message.edit_text(
        'By starting to work with me you agree to the <a href="https://just-russian-amateur.github.io/terms_for_alchemist_bot/Terms_of_Service.html">User Agreement</a> and <a href="https://just-russian-amateur.github.io/terms_for_alchemist_bot/Privacy_Policy.html">Privacy Policy</a>\n\nYou can ask my developer any questions you have regarding the operation of the bot or the payment system through the feedback system using the command /support🙂',
        parse_mode='HTML',
        reply_markup=ok()
    )
