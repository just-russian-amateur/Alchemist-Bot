from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from config_logger import ConfigLogger


logger = ConfigLogger(__name__)


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
            InlineKeyboardButton(text='🚀Start solving', callback_data='start_solving')
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=start_button)

    logger.log_info('Вывод приветствия')

    return kb


def error_image():
    reload_img = [
        [
            InlineKeyboardButton(text='📩🖼️Upload new image', callback_data='upload_new_image')
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=reload_img)

    logger.log_warning('Изображение не подходит для распознавания')

    return kb


def colors(undef_colors):
    color_buttons_list = []
    # Создание списка кнопок с цветмаи, которыми можно будет заменить неопределенные значения
    for color in undef_colors.keys():
        for _ in range(undef_colors[color]):
            if color == 'LIGHTGREEN':
                color_buttons_list.append(InlineKeyboardButton(text='LIGHT GREEN', callback_data='LIGHT GREEN'))
            elif color == 'LIGHTBLUE':
                color_buttons_list.append(InlineKeyboardButton(text='LIGHT BLUE', callback_data='LIGHT BLUE'))
            else:
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
            InlineKeyboardButton(text='➕🧪Add an empty flask', callback_data='add_an_empty_flask')
        ],
        [
            InlineKeyboardButton(text='📩🖼️Upload new image', callback_data='upload_new_image')
        ]
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=no_result_button)

    logger.log_info('Результат не найден')

    return kb
