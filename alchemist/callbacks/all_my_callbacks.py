'''Файл с enum callback'ами для бота'''
from enum import Enum


class CallbacksData(str, Enum):
    CLUE_START = "/start"

    CLUE_ACCOUNT = "/account"

    CLUE_TERMS = "/terms"

    CLUE_SUPPORT = "/support"

    START_SOLVING = "start_solving"

    RULES = "rules"
    
    ACCOUNT = "account"
    
    TERMS = "terms"
    
    CONTINUE = "continue"
    
    BUY_ATTEMPTS = "buy_attempts"

    SUPPORT = "support"
    
    RELOAD_IMAGE = "reload_image"
    
    UPLOAD_IMAGE = "upload_new_image"
    
    EMPTY_FLASK = "add_an_empty_flask"
    
    ATTEMPTS_5 = "5_attempts"
    
    ATTEMPTS_12 = "12_attempts"
    
    ATTEMPTS_20 = "20_attempts"
    
    ATTEMPTS_UNLIM = "unlimited_attempts"
    
    CANCEL = "cancel"
    
    OK = "ok"
    
    YES = "yes"
    
    NO = "no"
    
    REMOVE_FLASK = "remove_flask"
    
    MANUALLY = "manually"
    
    AUTOFILL = "autofill"
    
    NEXT = "next"
    
    PREVIOUS = "previous"
    
    CONFIRM = "confirm"
