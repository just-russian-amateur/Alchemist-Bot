import json


def get_level_from_json(level):
    '''Функция для считывания данных из json и преобразования их в список'''
    with open(level, 'r') as this_level:
        file = json.load(this_level)
    
    return list(file)


def send_result_to_txt(result, steps):
    '''Функция для записи результата решения в текстовый файл'''
    if len(steps) == 0:
        return False
    else:
        with open(result, 'w') as result_level:
            for step in steps:
                result_level.write(f'{step}\n')
        return True


def check_solving(position):
    '''Функция проверки получения решения'''
    full_color = 0
    for flask in position:
        # После очередного перемещения проходим по списку колб
        if flask[0] == flask[1] == flask[2] == flask[3]:
            full_color += 1
        else:
            return

    if full_color == len(position):
        # Количество одноцветных колб совпадает с количеством колб
        return True
    
    return False


def possible_moves(position):
    '''Функция для определения всех возможных перемещений для конкретной ситуации'''
    moves = []
    
    # Перебираем все комбинации колб, исключая случай совпадения первой и второй колбы
    for flask_1 in range(len(position)):
        for flask_2 in range(len(position)):
            if flask_1 != flask_2:
                moves.append(flask_1, flask_2)

    return moves


def apply_move(position, move):
    '''Функция для применения перемещения к текущему положению для получения нового'''
    pass
    # return next_position


def transfusion_of_liquids(position, visited_states, steps_list):
    '''Функция перемещения цвета в текущей позиции и записи последовательности шагов'''
    if position in visited_states:
        return False, []
    
    visited_states.append(position)
    if check_solving(position):
        return True, steps_list
    
    for move in possible_moves(position):
        next_position = apply_move(position, move)
        is_solved, steps_list = transfusion_of_liquids(next_position, visited_states, steps_list)  # Делаем первое перемещение
        if is_solved == True:
            # steps_list.append(next_position)
            return True, steps_list

    visited_states.pop()
    return False, []


def transfusion_manage(task, result):
    '''Основная функция модуля, регулирующая процесс переливания'''
    # Вызываем функцию для считывания файлов из json
    start_position = get_level_from_json(task)
    
    visited_states = []
    steps_list = []

    is_solved, steps_list = transfusion_of_liquids(start_position, visited_states, steps_list, result)  # Делаем первое перемещение
    if is_solved == True:
        send_result_to_txt(result, steps_list)
        return True
    
    return False
