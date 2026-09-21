from aiogram.types import (
    BufferedInputFile,
    RichMessageButton,
    InputRichBlockButtons,
    InputRichBlockPhoto,
    InputMediaPhoto,
    InputRichBlockCollage
)
from pydantic import BaseModel
from _io import BufferedReader

from config import color_variations
from texts.all_my_texts import KeyboardTexts
from callbacks.all_my_callbacks import CallbacksData

MY_URL = "t.me/alchemist_bot_support"
REPO_URL = "https://github.com/just-russian-amateur/Alchemist-Bot.git"


def fill_format(node: list, **kwargs) -> list:
    '''
    Заполнение именованных аргументов в текстах сообщений
    
    Рекурсивно применяет str.format(**kwargs) ко всем строковым листьям
    внутри произвольной структуры, не трогая саму структуру (типы, 
    вложенность, стили и т.п.).

    Работает для:
      - обычных строк
      - списков (list[RichTextUnion] и т.п.)
      - любых pydantic-моделей aiogram (InputRichBlockParagraph,
        RichTextBold, RichTextUrl, InputRichBlockButtons, RichMessageButton
        и т.д.) — рекурсивно проходит по всем их полям.
    '''

    if isinstance(node, str):
        return node.format(**kwargs)

    if isinstance(node, list):
        return [fill_format(item, **kwargs) for item in node]

    if isinstance(node, BaseModel):
        update = {}

        for field_name, value in node:
            new_value = fill_format(value, **kwargs)

            if new_value is not value:
                update[field_name] = new_value

        return node.model_copy(update=update) if update else node

    # числа, Enum, None и т.п. — возвращаем как есть
    return node


def create_rich_msg(msg: list, buttons: list) -> list:
    '''Формирование единого текстового сообщения'''
    return msg + buttons


def create_media_msg(media: list, caption: list, buttons=None) -> list:
    '''Формирование сообщения с медиафайлом(и)'''
    media += caption

    if buttons:
        return media + buttons

    return media


def build_image_msg(image: BufferedReader, name: str) -> list:
    '''Формирование блока с одиной картинкой'''
    return [
        InputRichBlockPhoto(
            photo=InputMediaPhoto(
                media=BufferedInputFile(
                    image.read(),
                    filename=name
                )
            )
        )
    ]


def build_collage_msg(images: list) -> list:
    '''Формирование сообщения с несколькими экземплярами медиконтента'''
    img_blocks = []

    for data_image in images:
        image, name = data_image
        img_blocks.append(
            InputRichBlockPhoto(
                photo=InputMediaPhoto(
                    media=BufferedInputFile(
                        image.read(),
                        filename=name
                    )
                )
            )
        )

    return [
        InputRichBlockCollage(
            blocks=img_blocks
        )
    ]


def build_rules_msg() -> list:
    '''Стартовое сообщение (часть про чтение правил)'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.RULES, callback_data=CallbacksData.RULES)
            ]
        )
    ]


def build_start_msg() -> list:
    '''Стартовое сообщение'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.START_SOLVING, callback_data=CallbacksData.START_SOLVING),
                RichMessageButton(text=KeyboardTexts.ACCOUNT, callback_data=CallbacksData.ACCOUNT)
            ]
        )
    ]


def build_excuse_msg() -> list:
    '''Сообщение с извинением'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.OPEN_REPOSITORY, url=REPO_URL)
            ]
        )
    ]


def build_pay_attempts_msg() -> list:
    '''Предложение окупки попыток'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.BUY_5_ATTEMPTS, callback_data=CallbacksData.ATTEMPTS_5)
            ]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.BUY_12_ATTEMPTS, callback_data=CallbacksData.ATTEMPTS_12)
            ]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.BUY_20_ATTEMPTS, callback_data=CallbacksData.ATTEMPTS_20)
            ]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.BUY_UNLIM_ATTEMPTS, callback_data=CallbacksData.ATTEMPTS_UNLIM)
            ]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.CANCEL, callback_data=CallbacksData.ACCOUNT)
            ]
        )
    ]


def build_continue_msg() -> list:
    '''Подготовка сообщения с продолжением работы бота'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.CONTINUE, callback_data=CallbacksData.CONTINUE)
            ]
        )
    ]


def build_feedback_msg() -> list:
    '''Обратная связь с разработчиком'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.FEEDBACK, url=MY_URL)
            ]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.UPLOAD_IMAGE, callback_data=CallbacksData.START_SOLVING)
            ]
        )
    ]


def build_terms_msg() -> list:
    '''Пользовательское соглашение'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.ACCEPT, callback_data=CallbacksData.OK)
            ]
        )
    ]


def build_account_msg(free: bool) -> list:
    '''Инфомация о пользователе'''
    blocks = [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.TERMS, callback_data=CallbacksData.TERMS)
            ]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.SUPPORT, url=MY_URL)
            ]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.CONTINUE, callback_data=CallbacksData.CONTINUE)
            ]
        )
    ]
    
    if not free:
        blocks.insert(
            0,
            InputRichBlockButtons(
                buttons=[
                    RichMessageButton(text=KeyboardTexts.BUY_ATTEMPTS, callback_data=CallbacksData.BUY_ATTEMPTS)
                ]
            )
        )

    return blocks


def build_recognition_img_msg() -> list:
    '''Распознавание цветов на изображении'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.CONFIRM, callback_data=CallbacksData.YES),
                RichMessageButton(text=KeyboardTexts.CHANGE_COLOR, callback_data=CallbacksData.NO)
            ]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.ADD_SEGMENT, callback_data=CallbacksData.EMPTY_FLASK)
            ]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.REMOVE_FLASK, callback_data=CallbacksData.REMOVE_FLASK)
            ]
        )
    ]


def build_recognition_error_msg() -> list:
    '''Ошибка распознавания изображения'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.UPLOAD_IMAGE, callback_data=CallbacksData.START_SOLVING)
            ]
        )
    ]


def create_undef_buttons(color_buttons_list: list) -> list:
    '''Расстановки кнопок с цветами'''

    color_buttons = []

    # "Красивая" расстановка кнопок
    for i in range(0, len(color_buttons_list), 3):
        color_buttons.append(
            InputRichBlockButtons(
                buttons=color_buttons_list[i:i + 3]
            )
        )
    
    return color_buttons


def build_colors_msg(undef_colors: dict) -> list:
    '''Сообщение с кнопками - названями цветов'''

    color_buttons_list = []

    # Создание списка кнопок с цветмаи, которыми можно будет заменить неопределенные значения
    for color_id in undef_colors.keys():
        for _ in range(undef_colors[color_id]):
            color_buttons_list.append(RichMessageButton(text=color_variations[int(color_id)], callback_data=color_id))

    return create_undef_buttons(color_buttons_list)


def build_change_flask_msg(num_of_lasks: int) -> list:
    '''Сообщение с выбором колбы для замены цвета внутри нее или ее удаления'''

    cnt = 0
    button_list, button_line = [], []

    for i in range(num_of_lasks - 2):

        cnt += 1
        button_line.append(RichMessageButton(text=f'{i + 1}', callback_data=f'{i}'))

        if cnt == 4:
            cnt = 0
            button_list.append(InputRichBlockButtons(buttons=button_line))
            button_line = []

        elif i == num_of_lasks - 3:
            button_list.append(InputRichBlockButtons(buttons=button_line))

    return button_list


def build_change_segment_msg() -> list:
    '''Сообщение с выбором сегмента колбы для замены цвета внутри него'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text='1', callback_data='0'),
                RichMessageButton(text='2', callback_data='1'),
                RichMessageButton(text='3', callback_data='2'),
                RichMessageButton(text='4', callback_data='3')
            ]
        )
    ]


def build_change_color_msg() -> list:
    '''Сообщение с выбором цветов для заполнения выбранного места'''

    buttons_list, buttons_line = [], []
    cnt = 0
    
    for id in color_variations.keys():
    
        cnt += 1
        buttons_line.append(RichMessageButton(text=color_variations[id], callback_data=str(id)))
    
        if cnt == 3:
            buttons_list.append(InputRichBlockButtons(buttons=buttons_line))
            buttons_line = []
            cnt = 0
    
    if buttons_line:
        buttons_list.append(InputRichBlockButtons(buttons=buttons_line))

    return buttons_list


def build_no_result_msg() -> list:
    '''Сообщение о отсутствием решения уровня'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.RELOAD_IMAGE, callback_data=CallbacksData.RELOAD_IMAGE),
                RichMessageButton(text=KeyboardTexts.ADD_SEGMENT, callback_data=CallbacksData.EMPTY_FLASK)
            ]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.UPLOAD_IMAGE, callback_data=CallbacksData.UPLOAD_IMAGE)
            ]
        )
    ]


def build_upload_file_msg(mode: str) -> list:
    '''Сообщение для подготовки к загрузке изображения'''

    if mode == 'upload_new_or_reload':
        return [
            InputRichBlockButtons(
                buttons=[
                    RichMessageButton(text=KeyboardTexts.RELOAD_IMAGE, callback_data=CallbacksData.RELOAD_IMAGE),
                    RichMessageButton(text=KeyboardTexts.UPLOAD_IMAGE, callback_data=CallbacksData.UPLOAD_IMAGE)
                ]
            )
        ]

    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.UPLOAD_IMAGE, callback_data=CallbacksData.UPLOAD_IMAGE)
            ]
        )
    ]


def build_autofill_options_msg(mode: str | None) -> list:
    '''Сообщение с выбором варианта для автозаполнения'''
    
    if mode == 'first':
        return [
            InputRichBlockButtons(
                buttons=[
                    RichMessageButton(text=KeyboardTexts.NEXT_OPTION, callback_data=CallbacksData.NEXT)
                ]
            ),
            InputRichBlockButtons(
                buttons=[
                    RichMessageButton(text=KeyboardTexts.SELECT, callback_data=CallbacksData.CONFIRM)
                ]
            )
        ]
    elif mode == 'last':
        return [
            InputRichBlockButtons(
                buttons=[
                    RichMessageButton(text=KeyboardTexts.PREVIOUS_OPTION, callback_data=CallbacksData.PREVIOUS)
                ]
            ),
            InputRichBlockButtons(
                buttons=[
                    RichMessageButton(text=KeyboardTexts.SELECT, callback_data=CallbacksData.CONFIRM)
                ]
            )
        ]
    
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.PREVIOUS_OPTION, callback_data=CallbacksData.PREVIOUS),
                RichMessageButton(text=KeyboardTexts.NEXT_OPTION, callback_data=CallbacksData.NEXT)
            ]
        ),
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.SELECT, callback_data=CallbacksData.CONFIRM)
            ]
        )
    ]


def build_select_mode_msg() -> list:
    '''Сообщение с выбором режима заполнения пустот'''
    return [
        InputRichBlockButtons(
            buttons=[
                RichMessageButton(text=KeyboardTexts.MANUALLY, callback_data=CallbacksData.MANUALLY),
                RichMessageButton(text=KeyboardTexts.AUTOFILL, callback_data=CallbacksData.AUTOFILL)
            ]
        )
    ]
