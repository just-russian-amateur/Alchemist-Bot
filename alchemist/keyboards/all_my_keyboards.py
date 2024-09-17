from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import classes.all_my_classes as amc


logger = amc.ConfigLogger(__name__)


def create_undef_buttons(color_buttons_list):
    '''Функция для расстановки кнопок с цветами'''
    color_buttons, button_line = [], []
    # "Красивая" расстановка кнопок
    for i in range(len(color_buttons_list)):
        if i % 3 == 0 and i == len(color_buttons_list) - 1:
            color_buttons.append(button_line)
            button_line = []
            button_line.append(color_buttons_list[i])
            color_buttons.append(button_line)
        elif i % 3 == 0 and i != 0:
            color_buttons.append(button_line)
            button_line = []
            button_line.append(color_buttons_list[i])
        elif i == len(color_buttons_list) - 1:
            button_line.append(color_buttons_list[i])
            color_buttons.append(button_line)
        else:
            button_line.append(color_buttons_list[i])

    logger.log_info('Расстановка кнопок в правильном порядке')
    
    return color_buttons


def start_keyboard():
    start_button = [
        [
            InlineKeyboardButton(text='🚀Start solving', callback_data='start_solving'),
            InlineKeyboardButton(text='📝Rules of use', callback_data='rules')
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=start_button)

    logger.log_info('Вывод приветствия')

    return kb


def error_image():
    reload_img = [
        [
            InlineKeyboardButton(text='📩🖼️Upload new image', callback_data='start_solving')
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=reload_img)

    return kb


def colors(undef_colors):
    color_buttons_list = []
    # Создание списка кнопок с цветмаи, которыми можно будет заменить неопределенные значения
    for color in undef_colors.keys():
        for _ in range(undef_colors[color]):
            color_buttons_list.append(InlineKeyboardButton(text=color, callback_data=color))
    color_buttons = create_undef_buttons(color_buttons_list)
    kb = InlineKeyboardMarkup(inline_keyboard=color_buttons)

    logger.log_info('Составлен список неопределенных кнопок')

    return kb


def feedback():
    feedback_button = [
        [
            InlineKeyboardButton(text='Feedback to me🙃', url=f"tg://user?id={984089348}")
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=feedback_button)

    return kb


def upload_new():
    upload_new_button = [
        [
            InlineKeyboardButton(text='🔄️🖼️Reload image', callback_data='reload_image'),
            InlineKeyboardButton(text='📩🖼️Upload new image', callback_data='upload_new_image')
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=upload_new_button)

    logger.log_info('Результат успешно найден')

    return kb


def no_result():
    no_result_button = [
        [
            InlineKeyboardButton(text='🔄️🖼️Reload image', callback_data='reload_image'),
            InlineKeyboardButton(text='➕🧪Add 1/4 flask', callback_data='add_an_empty_flask')
        ],
        [
            InlineKeyboardButton(text='📩🖼️Upload new image', callback_data='upload_new_image')
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=no_result_button)

    logger.log_info('Результат не найден')

    return kb


def continue_solving():
    continue_button = [
        [
            InlineKeyboardButton(text='⏭️Continue solving', callback_data='continue')
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=continue_button)

    return kb


def ok():
    ok_button = [
        [
            InlineKeyboardButton(text='✅I understand', callback_data='ok')
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=ok_button)

    return kb


def recognition_check():
    check_button = [
        [
            InlineKeyboardButton(text='Yes👍', callback_data='yes'),
            InlineKeyboardButton(text='No, try again👎', callback_data='no')
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=check_button)

    return kb


def autofill_buttons():
    autofill = [
        [
            InlineKeyboardButton(text='🙍‍♂️Manually', callback_data='manually'),
            InlineKeyboardButton(text='🤖Autofill', callback_data='autofill')
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=autofill)

    return kb


def autofill_options(mode=None):
    all_options = [
        [
            InlineKeyboardButton(text='⬅️Previous option', callback_data='previous'),
            InlineKeyboardButton(text='➡️Next option', callback_data='next')
        ],
        [
            InlineKeyboardButton(text='☑️Confirm selection', callback_data='confirm')
        ]
    ]
    first_options = [
        [
            InlineKeyboardButton(text='➡️Next option', callback_data='next')
        ],
        [
            InlineKeyboardButton(text='☑️Confirm selection', callback_data='confirm')
        ]
    ]
    last_options = [
        [
            InlineKeyboardButton(text='⬅️Previous option', callback_data='previous')
        ],
        [
            InlineKeyboardButton(text='☑️Confirm selection', callback_data='confirm')
        ]
    ]
    if mode == 'first':
        kb = InlineKeyboardMarkup(inline_keyboard=first_options)
    elif mode == 'last':
        kb = InlineKeyboardMarkup(inline_keyboard=last_options)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=all_options)

    return kb
