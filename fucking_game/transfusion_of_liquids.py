import json
import multiprocessing as mp
import threading as th
import os


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
        mono_color_height = 0
        solve_upper_color = (
            (idx_solve_flask, 0),
            ('EMPTY', mono_color_height)
        )  # Пустая колба
        for idx_color in range(count_colors - 1, -1, -1):
            # Получаем необходимую информацию о самом верхнем цвете
            if position[idx_solve_flask][idx_color] != 'EMPTY':
                mono_color_height += 1
                solve_upper_color = (
                    (idx_solve_flask, idx_color),
                    (position[idx_solve_flask][idx_color], mono_color_height)
                )
                break
        # Из пустой колбы ничего перелить нельзя
        if solve_upper_color[1][0] == 'EMPTY':
            continue
        # Проверка того, что следующие плоки такого же цвета (переливаться будет сразу весь цвет и это влияет на решение)
        for idx_color in range(solve_upper_color[0][1] - 1, -1, -1):
            if position[idx_solve_flask][idx_color] == solve_upper_color[1][0]:
                mono_color_height += 1
            else:
                break
        # Нельзя переливать полностью заполненную колбу
        if mono_color_height == count_colors:
            continue
        solve_upper_color = (
            (solve_upper_color[0][0], solve_upper_color[0][1]),
            (solve_upper_color[1][0], mono_color_height)
        )

        # Перебираем все колбы в которые можно перелить
        for idx_target_flask in range(count_flasks):
            # Переливать колбу саму в себя нельзя
            if idx_solve_flask != idx_target_flask:
                # Перебираем все цвета, начиная с верхнего (последний в списке)
                count_empty_slots = 0
                target_upper_color = (
                    (idx_target_flask, 0),
                    ('EMPTY', count_empty_slots)
                )
                for idx_color in range(count_colors - 1, -1, -1):
                    if position[idx_target_flask][idx_color] != 'EMPTY':
                        target_upper_color = (
                            (idx_target_flask, idx_color),
                            (position[idx_target_flask][idx_color], count_empty_slots)
                        )
                        break
                    else:
                        count_empty_slots += 1
                if count_empty_slots > 0:
                    target_upper_color = (
                        (target_upper_color[0][0], target_upper_color[0][1]),
                        (target_upper_color[1][0], count_empty_slots)
                    )
                # В полную колбу ничего перелить нельзя
                if target_upper_color[0][1] == count_colors - 1:
                    continue
                # Исключение переливания одного цвета в пустую колбу (бесполезное действие)
                if not (target_upper_color[1][0] == 'EMPTY' and
                        len(set(position[idx_solve_flask])) == 2 and
                        'EMPTY' in position[idx_solve_flask]):
                    # Переливание возможно только если верхние цвета совпадают или если переливаем в пустую колбу и места в целевой колбе достаточно
                    if solve_upper_color[1][0] == target_upper_color[1][0] and target_upper_color[1][1] >= solve_upper_color[1][1]:
                        target_upper_color = (
                            (target_upper_color[0][0], target_upper_color[0][1] + 1),
                            ('EMPTY', target_upper_color[1][1])
                        )
                        moves.append((solve_upper_color, target_upper_color))
                    elif target_upper_color[1][0] == 'EMPTY':
                        moves.append((solve_upper_color, target_upper_color))

    return moves


def apply_move(position, move):
    '''Функция для применения перемещения к текущему положению для получения нового'''
    # Получение данных о колбах, которые задействуются
    solve_flask, target_flask = move
    
    # Замена цвета в решающей колбе на пустое и заполнение места в целевой колбе 
    for cnt in range(solve_flask[1][1]):
        position[target_flask[0][0]][target_flask[0][1] + cnt] = solve_flask[1][0]
        position[solve_flask[0][0]][solve_flask[0][1] - cnt] = 'EMPTY'
    step = f'{solve_flask[0][0] + 1} -> {target_flask[0][0] + 1}'

    return position, step


def go_back_move(position, move):
    '''Функция отмены перемещения'''
    # Получение данных о колбах, которые задействуются
    solve_flask, target_flask = move

    # Замена цвета в целевой колбе на пустое и заполнение места в решающей колбе
    for cnt in range(solve_flask[1][1]):
        position[solve_flask[0][0]][solve_flask[0][1] - cnt] = solve_flask[1][0]
        position[target_flask[0][0]][target_flask[0][1] + cnt] = target_flask[1][0]

    return position


def transfusion_of_liquids(position, steps_list=None):
    '''Функция перемещения цвета в текущей позиции и записи последовательности шагов'''
    visited_states = set()
    stack = [(position, [])]
    # stack = [(position, [steps_list])]
    # print(stack)
    while stack:
        now_position, steps = stack[0]
        now_position = list(list(flask) for flask in now_position)
        steps = list(steps)
        # Проверяем решена ли задача
        if check_solving(now_position):
            return True, steps
        
        if len(possible_moves(now_position)) == 0:
            # Поскольку мы сначала заполняем стек вершинами, то для корректных позиций нужен откат действия
            go_back_move(now_position, move)
            stack.pop(0)
        else:
            # Обходим массив возможных перемещений, рекурсивно погружаясь в глубину
            moves = possible_moves(now_position)
            for move in moves:
                # Применяем действие
                now_position, step = apply_move(now_position, move)
                # Преобразуем новую текущую позицию в неизменяемый объект (кортеж)
                now_position_tuple = tuple(tuple(flask) for flask in now_position)

                # Если текущая позиция уже была посещена ранее, то возвращаем движение назад
                if now_position_tuple in visited_states:
                    if move == moves[len(moves) - 1]:
                        stack.pop(0)
                    go_back_move(now_position, move)
                    continue

                # Добавляем текущую позицию в список посещенных
                visited_states.add(now_position_tuple)
                steps.append(step)
                steps = tuple(steps)
                stack.insert(0, (now_position_tuple, steps))
                break

    return False, None


def find_all_first_moves(position):
    '''Функция для поиска всех возможных перемещений для начальной позиции для последующей параллелизации'''
    visited_states = set()
    pair = set()
    moves = possible_moves(position)
    for move in moves:
        # Применяем действие
        position, step = apply_move(position, move)
        # Преобразуем новую текущую позицию в неизменяемый объект (кортеж)
        position_tuple = tuple(tuple(flask) for flask in position)

        # Добавляем текущую позицию в список посещенных
        visited_states.add(position_tuple)
        # Возвращаемся к стартовой позиции
        go_back_move(position, move)
        # Создаем пару агрументов для следующей функции
        pair.add((position_tuple, step))

    return pair


# def create_threads_pack(pair_args, count_threads_pack):
#     '''Функция для упаковки в пакеты потоков для обраюотки на отдельных ядрах'''
#     threads_pack = []

#     for i in range(count_threads_pack):
#         if not pair_args:
#             break
#         thread = th.Thread(target=transfusion_of_liquids, )
#         threads_pack.append(thread)
#         pair_args.pop(0)
    
#     return thread


def transfusion_manage(task, result):
    '''Основная функция модуля, регулирующая процесс переливания'''
    # Вызываем функцию для считывания файлов из json
    start_position = get_level_from_json(task)
    # Возвращаем флаг решения и список шагов, если решение есть
    is_solved, steps_list = transfusion_of_liquids(start_position)
    if is_solved:
        send_result_to_txt(result, steps_list)
        return True
    # Получаем все возможные начальные перемещения
    # pair_args = find_all_first_moves(start_position)

    # # count_processes = len(os.sched_getaffinity(0))
    # # count_threads_pack = int(round(len(pair_args) / count_processes))

    # # if count_threads_pack > 1:
    # #     create_threads_pack(pair_args, count_threads_pack)
    # #     with mp.Pool(processes=count_processes) as process:
    # #         is_solved = process.starmap(transfusion_of_liquids, pair_args)

    # with mp.Pool(processes=len(pair_args)) as process:
    #     is_solved = process.starmap(transfusion_of_liquids, pair_args)
    
    # # Возвращаем флаг решения и список шагов, если решение есть
    # for _ in range(len(is_solved)):
    #     if is_solved[0]:
    #         send_result_to_txt(result, is_solved[1])
    #         return True
    
    return False


# if __name__ == '__main__':
#     transfusion_manage('./fucking_game/config_files/myLevel.json', 'result.txt')
