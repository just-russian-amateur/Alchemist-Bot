from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import classes.all_my_classes as amc
from config import color_variations
from texts.all_my_texts import KeyboardTexts
from callbacks.all_my_callbacks import CallbacksData


logger = amc.ConfigLogger(__name__)
MY_URL = "t.me/alchemist_bot_support"


def create_undef_buttons(color_buttons_list: list) -> list:
    '''Функция для расстановки кнопок с цветами'''

    color_buttons = []

    # "Красивая" расстановка кнопок
    for i in range(0, len(color_buttons_list), 3):
        color_buttons.append(color_buttons_list[i:i + 3])

    logger.log_info('Расстановка кнопок в правильном порядке')
    
    return color_buttons


def start_keyboard() -> list:

    logger.log_info('Вывод приветствия')

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.START_SOLVING, callback_data=CallbacksData.START_SOLVING),
                InlineKeyboardButton(text=KeyboardTexts.RULES, callback_data=CallbacksData.RULES)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.ACCOUNT, callback_data=CallbacksData.ACCOUNT)
            ]
        ]
    )


def account(free_mode: bool) -> list:

    logger.log_info('Вывод личного аккаунта пользователя')
    
    if free_mode:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=KeyboardTexts.TERMS, callback_data=CallbacksData.TERMS)
                ],
                [
                    InlineKeyboardButton(text=KeyboardTexts.SUPPORT, url=MY_URL),
                ],
                [
                    InlineKeyboardButton(text=KeyboardTexts.CONTINUE, callback_data=CallbacksData.CONTINUE)
                ]
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.TERMS, callback_data=CallbacksData.TERMS)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.SUPPORT, url=MY_URL),
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.BUY_ATTEMPTS, callback_data=CallbacksData.BUY_ATTEMPTS),
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.CONTINUE, callback_data=CallbacksData.CONTINUE)
            ]
        ]
    )


def error_image() -> list:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.UPLOAD_IMAGE, callback_data=CallbacksData.START_SOLVING)
            ]
        ]
    )


def colors(undef_colors: dict) -> list:

    color_buttons_list = []

    # Создание списка кнопок с цветмаи, которыми можно будет заменить неопределенные значения
    for color_id in undef_colors.keys():
        for _ in range(undef_colors[color_id]):
            color_buttons_list.append(InlineKeyboardButton(text=color_variations[int(color_id)], callback_data=color_id))

    color_buttons = create_undef_buttons(color_buttons_list)
    kb = InlineKeyboardMarkup(inline_keyboard=color_buttons)

    logger.log_info('Составлен список неопределенных кнопок')

    return kb


def feedback() -> list:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.FEEDBACK, url=MY_URL),
                InlineKeyboardButton(text=KeyboardTexts.UPLOAD_IMAGE, callback_data=CallbacksData.START_SOLVING)
            ]
        ]
    )
    

def upload_new(mode: str) -> list:

    logger.log_info('Результат успешно найден')
    
    if mode == 'upload_new_or_reload':
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=KeyboardTexts.RELOAD_IMAGE, callback_data=CallbacksData.RELOAD_IMAGE),
                    InlineKeyboardButton(text=KeyboardTexts.UPLOAD_IMAGE, callback_data=CallbacksData.UPLOAD_IMAGE)
                ]
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.UPLOAD_IMAGE, callback_data=CallbacksData.UPLOAD_IMAGE)
            ]
        ]
    )
    

def no_result() -> list:

    logger.log_info('Результат не найден')
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.RELOAD_IMAGE, callback_data=CallbacksData.RELOAD_IMAGE),
                InlineKeyboardButton(text=KeyboardTexts.ADD_SEGMENT, callback_data=CallbacksData.EMPTY_FLASK)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.UPLOAD_IMAGE, callback_data=CallbacksData.UPLOAD_IMAGE)
            ]
        ]
    )


def pay_attempts() -> list:

    logger.log_info('Кончились попытки')

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.BUY_5_ATTEMPTS, callback_data=CallbacksData.ATTEMPTS_5)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.BUY_12_ATTEMPTS, callback_data=CallbacksData.ATTEMPTS_12)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.BUY_20_ATTEMPTS, callback_data=CallbacksData.ATTEMPTS_20)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.BUY_UNLIM_ATTEMPTS, callback_data=CallbacksData.ATTEMPTS_UNLIM)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.CANCEL, callback_data=CallbacksData.ACCOUNT)
            ]
        ]
    )
    

def payment_kb(btn_text: str) -> list:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=btn_text, pay=True)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.CANCEL, callback_data=CallbacksData.CANCEL)
            ]
        ]
    )


def continue_solving() -> list:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.CONTINUE, callback_data=CallbacksData.CONTINUE)
            ]
        ]
    )
    

def ok() -> list:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.ACCEPT, callback_data=CallbacksData.OK)
            ]
        ]
    )
    

def recognition_check() -> list:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.CONFIRM, callback_data=CallbacksData.YES),
                InlineKeyboardButton(text=KeyboardTexts.CHANGE_COLOR, callback_data=CallbacksData.NO)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.ADD_SEGMENT, callback_data=CallbacksData.EMPTY_FLASK)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.REMOVE_FLASK, callback_data=CallbacksData.REMOVE_FLASK)
            ]
        ]
    )


def change_flask(num_of_lasks: int) -> list:

    cnt = 0
    button_list, button_line = [], []

    for i in range(num_of_lasks - 2):

        cnt += 1
        button_line.append(InlineKeyboardButton(text=f'{i + 1}', callback_data=f'{i}'))

        if cnt == 4:
            cnt = 0
            button_list.append(button_line)
            button_line = []

        elif i == num_of_lasks - 3:
            button_list.append(button_line)

    kb = InlineKeyboardMarkup(inline_keyboard=button_list)

    return kb


def change_segment() -> list:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='1', callback_data='0'),
                InlineKeyboardButton(text='2', callback_data='1'),
                InlineKeyboardButton(text='3', callback_data='2'),
                InlineKeyboardButton(text='4', callback_data='3')
            ]
        ]
    )


def change_color() -> list:

    buttons_list, buttons_line = [], []
    cnt = 0
    
    for id in color_variations.keys():
    
        cnt += 1
        buttons_line.append(InlineKeyboardButton(text=color_variations[id], callback_data=str(id)))
    
        if cnt == 3:
            buttons_list.append(buttons_line)
            buttons_line = []
            cnt = 0
    
    if buttons_line:
        buttons_list.append(buttons_line)

    kb = InlineKeyboardMarkup(inline_keyboard=buttons_list)

    return kb


def autofill_buttons() -> list:

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.MANUALLY, callback_data=CallbacksData.MANUALLY),
                InlineKeyboardButton(text=KeyboardTexts.AUTOFILL, callback_data=CallbacksData.AUTOFILL)
            ]
        ]
    )


def autofill_options(mode=None) -> list:
    
    if mode == 'first':
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=KeyboardTexts.NEXT_OPTION, callback_data=CallbacksData.NEXT)
                ],
                [
                    InlineKeyboardButton(text=KeyboardTexts.SELECT, callback_data=CallbacksData.CONFIRM)
                ]
            ]
        )
    elif mode == 'last':
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=KeyboardTexts.PREVIOUS_OPTION, callback_data=CallbacksData.PREVIOUS)
                ],
                [
                    InlineKeyboardButton(text=KeyboardTexts.SELECT, callback_data=CallbacksData.CONFIRM)
                ]
            ]
        )
    
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=KeyboardTexts.PREVIOUS_OPTION, callback_data=CallbacksData.PREVIOUS),
                InlineKeyboardButton(text=KeyboardTexts.NEXT_OPTION, callback_data=CallbacksData.NEXT)
            ],
            [
                InlineKeyboardButton(text=KeyboardTexts.SELECT, callback_data=CallbacksData.CONFIRM)
            ]
        ]
    )
