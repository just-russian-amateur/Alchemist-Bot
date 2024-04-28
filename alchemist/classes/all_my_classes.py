from aiogram.fsm.state import StatesGroup, State
import logging
from logging.handlers import RotatingFileHandler
import os


class ConfigLogger:
    '''Класс логгирования'''
    def __init__(self, filename) -> None:
        # Создание папки для логов
        if not os.path.isdir('./logs'):
            os.mkdir('./logs')
        self.logger = logging.getLogger(filename)
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(f'./logs/{filename}.log', 'a')
        handler = RotatingFileHandler(f'./logs/{filename}.log', maxBytes=1e6, backupCount=6)
        formatter = logging.Formatter('%(name)s\t%(asctime)s\t%(levelname)s\t%(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)


    def log_message(self, level, message):
        if level == 'info':
            self.logger.info(message)
        elif level == 'warning':
            self.logger.warning(message, exc_info=True)
        elif level == 'error':
            self.logger.error(message, exc_info=True)


    def log_info(self, message):
        self.log_message('info', message)


    def log_warning(self, message):
        self.log_message('warning', message)


    def log_error(self, message):
        self.log_message('error', message)


class SolveFlasks(StatesGroup):
    '''Класс для машины состояний'''
    start_solving = State()
    send_photo = State()
    set_color = State()