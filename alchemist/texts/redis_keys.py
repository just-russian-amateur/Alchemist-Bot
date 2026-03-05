'''Файл с enum ключами полльзователей для бота'''
from enum import Enum


class RedisKeys(str, Enum):
    FRIENDS_IDS = "id_my_friends"

    FREE_ATTEMPTS = "count_free_attempts"

    PAID_ATTEMPTS = "count_paid_attempts"

    END_UNLIM = "end_unlimited"

    FAIL_ATTEMPTS = "count_fail_attempts"

    FLASKS_LIST = "flasks_id_list"

    UNDEF_COLORS = "undefined_colors"

    LVL_FILE = "level_file"

    NEW_SEGMENTS = "new_segment"

    AUTOFILL_FLASKS_LIST = "autofill_flasks_id_list"

    PERMUTATIONS = "permutations"

    SERIAL_NUMBER = "serial_number"

    IMAGE = "original_image"

    EDITED_UNDEF_COLORS = "edit_undefined_colors"

    EDITED_FLASKS_LIST = "edit_flasks_id_list"

    CHOOSEN_FLASK = "choosen_flask"

    CHOOSEN_SEGMENT = "choosen_segment"

    ADD_ATTEMPTS = "add_attempts"
