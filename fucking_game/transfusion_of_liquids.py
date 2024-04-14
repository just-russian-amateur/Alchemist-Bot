import json


def get_level_from_json(level):
    '''Функция для считывания данных из json и преобразования их в список'''
    with open(level, 'r') as this_level:
        file = json.load(this_level)
    
    return list(file['bottles'])


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
            break

    if full_color == len(position):
        # Количество одноцветных колб совпадает с количеством колб
        return True
    
    return False


def possible_moves(position):
    '''Функция для определения всех возможных перемещений для конкретной ситуации'''
    moves = []  # Список перемещений
    count_flasks = len(position)    # Количество колб
    count_colors = len(position[0]) # Максимальное количество цветов в колбе (во всех колбах одинаковое количество элементов)
    
    # Перебираем все колбы из которых можно перелить
    for idx_solve_flask in range(count_flasks):
        # Перебираем все цвета, начиная с верхнего (последний в списке)
        solve_upper_color = ((idx_solve_flask, 0), 'EMPTY')  # Пустая колба
        for idx_color in range(count_colors - 1, -1, -1):
            # Получаем необходимую информацию о самом верхнем цвете
            if position[idx_solve_flask][idx_color] != 'EMPTY':
                solve_upper_color = ((idx_solve_flask, idx_color), position[idx_solve_flask][idx_color])
                break
        # Из пустой колбы ничего перелить нельзя
        if solve_upper_color[1] == 'EMPTY':
            continue

        # Перебираем все колбы в которые можно перелить
        for idx_target_flask in range(count_flasks):
            # Переливать колбу саму в себя нельзя
            if idx_solve_flask != idx_target_flask:
                # Перебираем все цвета, начиная с верхнего (последний в списке)
                target_upper_color = ((idx_target_flask, 0), 'EMPTY')
                for idx_color in range(count_colors - 1, -1, -1):
                    if position[idx_target_flask][idx_color] != 'EMPTY':
                        target_upper_color = ((idx_target_flask, idx_color), position[idx_target_flask][idx_color])
                        break
                # В полную колбу ничего перелить нельзя
                if target_upper_color[0][1] == count_colors - 1:
                    continue
                # Переливание возможно только если верхние цвета совпадают или если переливаем в пустую колбу
                if solve_upper_color[1] == target_upper_color[1] or target_upper_color[1] == 'EMPTY':
                    moves.append((solve_upper_color, target_upper_color))

    return moves


def apply_move(position, move):
    '''Функция для применения перемещения к текущему положению для получения нового'''
    # Получение данных о колбах, которые задействуются
    solve_flask, target_flask = move
    
    # Замена цвета в решающей колбе на пустое и заполнение места в целевой колбе 
    if target_flask[1] == 'EMPTY':
        position[target_flask[0][0]][target_flask[0][1]] = solve_flask[1]
    else:
        position[target_flask[0][0]][target_flask[0][1] + 1] = solve_flask[1]
    position[solve_flask[0][0]][solve_flask[0][1]] = 'EMPTY'
    step = f'{solve_flask[0][0]} -> {target_flask[0][0]}'

    return position, step


def go_back_move(position, move):
    '''Функция отмены перемещения'''
    # Получение данных о колбах, которые задействуются
    solve_flask, target_flask = move

    # Замена цвета в целевой колбе на пустое и заполнение места в решающей колбе
    position[solve_flask[0][0]][solve_flask[0][1]] = solve_flask[1]
    position[target_flask[0][0]][target_flask[0][1]] = target_flask[1]

    return position


def transfusion_of_liquids(position, visited_states, steps_list):
    '''Функция перемещения цвета в текущей позиции и записи последовательности шагов'''
    # Проверяем решена ли задача
    if check_solving(position):
        return True
    
    # Обходим массив возможных перемещений, рекурсивно погружаясь в глубину
    for move in possible_moves(position):
        # Применяем действие
        next_position, step = apply_move(position, move)
        # Преобразуем новую текущую позицию в неизменяемый объект (кортеж)
        steps_list.append(step)
        next_position_tuple = tuple(tuple(flask) for flask in next_position)

        # Если текущая позиция уже была посещена ранее, то возвращаем движение назад
        if next_position_tuple in visited_states:
            go_back_move(next_position, move)
            steps_list.pop()
            continue

        # Добавляем текущую позицию в список посещенных
        visited_states.add(next_position_tuple)

        is_solved = transfusion_of_liquids(next_position, visited_states, steps_list)  # Делаем перемещение
        # Если решение найдено, то завершаем перемещения
        if is_solved:
            return True
        go_back_move(next_position, move)
        steps_list.pop()

    return False


def transfusion_manage(task, result):
    '''Основная функция модуля, регулирующая процесс переливания'''
    # Вызываем функцию для считывания файлов из json
    start_position = get_level_from_json(task)
    
    visited_states = set()
    steps_list = []

    # Возвращаем флаг решения и список шагов, если решение есть
    is_solved = transfusion_of_liquids(start_position, visited_states, steps_list)  # Делаем первое перемещение
    if is_solved:
        send_result_to_txt(result, steps_list)
        return True
    
    return False


if __name__ == "__main__":
    transfusion_manage('./fucking_game/config_files/myLevel2.json', 'result.txt')
