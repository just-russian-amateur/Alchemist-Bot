from random import shuffle

from found_colors import EMPTY


async def check_solving(position: tuple) -> bool:
    '''Функция проверки получения решения'''

    for flask in position:

        first = flask[0]

        if any(color != first for color in flask):
            return False

    return True


async def possible_moves(position: tuple, last_move=None) -> list:
    '''
    Функция для определения всех возможных перемещений для конкретной ситуации

    Отсекаются следующие ходы:
    1. Переливание колбы самой в себя +
    2. Переливание одноцветной колбы (в том числе не из 4 сегментов) в пустую колбу +
    3. Переливание в заполненную колбу +
    4. Переливание из пустой колбы +
    5. Переливание несовпадающих цветов в колбах +
    6. "Глупые" ходы - переливание между двумя колбами последовательно +

    Кортеж с описанием цвета включает в себя следующие составляющие:
    [
        [индекс текущей колбы, индекс текущего сегмента внутри колбы],
        [порядковый номер цвета сегмента, толщина цвета в сегментах]
    ]

    Порядковые номера цветов можно увидеть в файле "found_colors.py"
    '''

    moves = []  # Список перемещений

    # Перебираем все колбы из которых можно перелить
    for idx_solve_flask, solve_flask in enumerate(position):

        count_segments = len(solve_flask)
        solve_colors_count = len(set(solve_flask))
        
        # Из пустой колбы ничего перелить нельзя
        if solve_flask[0] == EMPTY:
            continue

        # Нельзя переливать полностью заполненную колбу
        if solve_colors_count == 1 and count_segments == 4:
            continue

        # Избавляемся от "глупых" ходов с переливанием из той колбы, в которую вливали на прошлом ходу
        if last_move and idx_solve_flask == last_move:
            continue
            
        # Перебираем все цвета, начиная с верхнего (последний в списке)
        mono_color_height = 0
        solve_upper_color = [
            [idx_solve_flask, 0],
            [EMPTY, mono_color_height]
        ]  # Пустая колба

        for idx_color in range(count_segments - 1, -1, -1):

            # Получаем необходимую информацию о самом верхнем цвете
            if solve_flask[idx_color] != EMPTY:

                mono_color_height += 1
                solve_upper_color[0][1] = idx_color
                solve_upper_color[1][0] = solve_flask[idx_color]
                break

        # Проверка того, что следующие блоки такого же цвета (переливаться будет сразу весь цвет и это влияет на решение)
        idx_upper_color = solve_upper_color[0][1]

        for idx_color in range(idx_upper_color - 1, -1, -1):

            if solve_flask[idx_color] == solve_upper_color[1][0]:
                mono_color_height += 1
            else:
                break

        solve_upper_color[1][1] = mono_color_height

        # Перебираем все колбы в которые можно перелить
        for idx_target_flask, target_flask in enumerate(position):

            count_segments = len(target_flask)
            
            # Переливать колбу саму в себя нельзя
            if idx_solve_flask == idx_target_flask:
                continue

            # В полную колбу ничего перелить нельзя
            first = target_flask[0]
            if all(color == first for color in target_flask) and target_flask[0] != EMPTY:
                continue

            # Моно цвет в пустую колбу переливать бессмысленно
            if target_flask[0] == EMPTY and solve_colors_count == 2 and EMPTY in solve_flask:
                continue

            # Перебираем все цвета, начиная с верхнего (последний в списке)
            count_empty_slots = 0
            target_upper_color = [
                [idx_target_flask, 0],
                [EMPTY, count_empty_slots]
            ]   # Пустая колба

            for idx_color in range(count_segments - 1, -1, -1):

                if target_flask[idx_color] != EMPTY:
                    target_upper_color[0][1] = idx_color
                    target_upper_color[1][0] = target_flask[idx_color]
                    break
                else:
                    count_empty_slots += 1

            if count_empty_slots > 0:
                target_upper_color[1][1] = count_empty_slots

            # Переливание возможно только если верхние цвета совпадают или если переливаем в пустую колбу и места в целевой колбе достаточно
            if target_upper_color[1][1] >= solve_upper_color[1][1]:

                if solve_upper_color[1][0] == target_upper_color[1][0]:
                    target_upper_color[0][1] += 1
                    target_upper_color[1][0] = EMPTY
                    moves.append([solve_upper_color, target_upper_color])
                elif target_flask[0] == EMPTY:
                    moves.append([solve_upper_color, target_upper_color])

    if len(moves) > 1:
        shuffle(moves)
    
    return moves


async def apply_move(position: tuple, move: list) -> tuple[tuple, str]:
    '''Функция для применения перемещения к текущему положению для получения нового'''

    # Получение данных о колбах, которые задействуются
    solve_flask, target_flask = move

    # Замена цвета в решающей колбе на пустое и заполнение места в целевой колбе
    update_position = []

    for idx_flask, flask in enumerate(position):
        
        if idx_flask == solve_flask[0][0]:
            new_flask = tuple(
                EMPTY if solve_flask[0][1] - solve_flask[1][1] < idx_color <= solve_flask[0][1] else color
                for idx_color, color in enumerate(flask)
            )
            update_position.append(new_flask)
        elif idx_flask == target_flask[0][0]:
            new_flask = tuple(
                solve_flask[1][0] if target_flask[0][1] + solve_flask[1][1] > idx_color >= target_flask[0][1] else color
                for idx_color, color in enumerate(flask)
            )
            update_position.append(new_flask)
        else:
            update_position.append(flask)
    
    step = f'{solve_flask[0][0] + 1} ➡️ {target_flask[0][0] + 1}'

    return tuple(update_position), step


async def transfusion_of_liquids(position: tuple) -> tuple[bool, str | None, int | None]:
    '''Функция перемещения цвета в текущей позиции и записи последовательности шагов'''

    visited_states = {tuple(sorted(position))}
    steps = []
    stack = [[position, await possible_moves(position)]]

    while stack:

        now_position, moves = stack[-1]

        # Проверяем решена ли задача
        if await check_solving(now_position):
            return True, steps, None
        
        if not moves:

            stack.pop()

            if steps:
                steps.pop()
                
            continue

        move = moves.pop()

        # Применяем действие
        new_position, step = await apply_move(now_position, move)

        # Если текущая позиция уже была посещена ранее, то переходим к следующей
        canonical_position = tuple(sorted(new_position))

        if canonical_position in visited_states:
            continue

        # Добавляем текущую позицию в список посещенных
        visited_states.add(canonical_position)
        steps.append(step)
        stack.append([new_position, await possible_moves(new_position, move[1][0][0])])

    return False, None, len(visited_states)


async def transfusion_manage(task: list) -> tuple[bool, str | None, int | None]:
    '''Основная функция модуля, регулирующая процесс переливания'''

    # Возвращаем флаг решения и список шагов, если решение есть
    position_tuple = tuple(tuple(flask) for flask in task)
    is_solved, steps_list, count_states = await transfusion_of_liquids(position_tuple)
    
    if is_solved:

        lines = []

        for idx_step, step in enumerate(steps_list, 1):

            lines.append(step)

            if idx_step % 4 == 0:
                # Добавляем пустую строку, разбивая решение на блоки по 4 хода для удобства отслеживания
                lines.append('')

        result = '\n'.join(lines)

        return is_solved, result, None

    return is_solved, None, count_states
