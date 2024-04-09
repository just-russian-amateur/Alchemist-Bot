from aiogram.fsm.state import StatesGroup, State


class SolveFlasks(StatesGroup):
    '''Класс для машины состояний'''
    start_solving = State()
    reload_image = State()
    add_an_empty_flask = State()
    send_photo = State()
    set_color = State()