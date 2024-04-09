from aiogram.fsm.state import StatesGroup, State


class SolveFlasks(StatesGroup):
    '''Класс для машины состояний'''
    start_solving = State()
    send_photo = State()
    set_color = State()