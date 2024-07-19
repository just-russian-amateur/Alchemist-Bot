def check_solving(position: list) -> bool:
    '''Функция проверки получения решения'''
    full_color = 0
    for flask in position:
        # После очередного перемещения проходим по списку колб
        full_flask = 0
        for idx_colors in range(len(flask)):
            if flask[idx_colors] == flask[0]:
                full_flask += 1
            else:
                break
        if full_flask == len(flask):
            full_color += 1
        else:
            break

    if full_color == len(position):
        # Количество одноцветных колб совпадает с количеством колб
        return True
    
    return False


def possible_moves(position: list) -> list:
    '''Функция для определения всех возможных перемещений для конкретной ситуации'''
    moves = []  # Список перемещений
    count_flasks = len(position)    # Количество колб

    # Перебираем все колбы из которых можно перелить
    for idx_solve_flask in range(count_flasks):
        count_colors = len(position[idx_solve_flask])
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
        # Проверка того, что следующие блоки такого же цвета (переливаться будет сразу весь цвет и это влияет на решение)
        for idx_color in range(solve_upper_color[0][1] - 1, -1, -1):
            if position[idx_solve_flask][idx_color] == solve_upper_color[1][0]:
                mono_color_height += 1
            else:
                break
        # Нельзя переливать полностью заполненную колбу
        if mono_color_height == count_colors and count_colors == 4:
            continue
        solve_upper_color = (
            (solve_upper_color[0][0], solve_upper_color[0][1]),
            (solve_upper_color[1][0], mono_color_height)
        )

        # Перебираем все колбы в которые можно перелить
        for idx_target_flask in range(count_flasks):
            count_colors = len(position[idx_target_flask])
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
                if target_upper_color[0][1] == count_colors - 1 and count_colors != 1:
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


def apply_move(position: list, move: tuple) -> tuple[list, str]:
    '''Функция для применения перемещения к текущему положению для получения нового'''
    # Получение данных о колбах, которые задействуются
    solve_flask, target_flask = move
    
    # Замена цвета в решающей колбе на пустое и заполнение места в целевой колбе 
    for cnt in range(solve_flask[1][1]):
        position[target_flask[0][0]][target_flask[0][1] + cnt] = solve_flask[1][0]
        position[solve_flask[0][0]][solve_flask[0][1] - cnt] = 'EMPTY'
    step = f'{solve_flask[0][0] + 1} ➡️ {target_flask[0][0] + 1}'

    return position, step


def go_back_move(position: list, move: tuple) -> list:
    '''Функция отмены перемещения'''
    # Получение данных о колбах, которые задействуются
    solve_flask, target_flask = move

    # Замена цвета в целевой колбе на пустое и заполнение места в решающей колбе
    for cnt in range(solve_flask[1][1]):
        position[solve_flask[0][0]][solve_flask[0][1] - cnt] = solve_flask[1][0]
        position[target_flask[0][0]][target_flask[0][1] + cnt] = target_flask[1][0]

    return position


def transfusion_of_liquids(position: list) -> tuple[bool, any]:
    '''Функция перемещения цвета в текущей позиции и записи последовательности шагов'''
    visited_states = set()
    stack = [(position, [])]

    while stack:
        now_position, steps = stack[0]
        now_position = list(list(flask) for flask in now_position)
        steps = list(steps)
        # Проверяем решена ли задача
        if check_solving(now_position):
            return True, steps
        
        if not possible_moves(now_position):
            # Поскольку мы сначала заполняем стек вершинами, то для корректных позиций нужен откат действия
            go_back_move(now_position, move)
            stack.pop(0)
        else:
            # Обходим массив возможных перемещений, рекурсивно погружаясь в глубину
            moves = possible_moves(now_position)
            for move in moves:
                if move == moves[len(moves) - 1] and len(stack) == 1:
                    # Прекращаем решение если пройдены все ветви от корня
                    return False, None
                # Применяем действие
                now_position, step = apply_move(now_position, move)
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


def transfusion_manage(task: list) -> tuple[bool, any]:
    '''Основная функция модуля, регулирующая процесс переливания'''
    # Возвращаем флаг решения и список шагов, если решение есть
    is_solved, steps_list = transfusion_of_liquids(task)
    if is_solved:
        # Убираем "глупые" ходы бота
        idx_step = 1
        while idx_step < len(steps_list):
            current_step = steps_list[idx_step].split('➡️')
            previous_step = steps_list[idx_step - 1].split('➡️')
            if current_step[0] == previous_step[1] and current_step[1] == previous_step[0]:
                steps_list.pop(idx_step - 1)
                idx_step -= 1
            idx_step += 1
        result = ''
        for step in steps_list:
            result += step + '\n'
        return True, result

    return False, None
