from aiogram import Bot
from aiogram.utils.chat_action import ChatActionSender

from random import shuffle
from collections import deque

from found_colors import EMPTY


async def check_solving(position: list) -> bool:
    '''Функция проверки получения решения'''
    full_color = 0
    for flask in position:
        # После очередного перемещения проходим по списку колб
        full_flask = 0
        for color in flask:
            if color == flask[0]:
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


async def possible_moves(position: list, last_move=None) -> list:
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

        # Из пустой колбы ничего перелить нельзя
        if solve_upper_color[1][0] == EMPTY:
            continue

        # Проверка того, что следующие блоки такого же цвета (переливаться будет сразу весь цвет и это влияет на решение)
        idx_upper_color = solve_upper_color[0][1]
        for idx_color in range(idx_upper_color - 1, -1, -1):
            if solve_flask[idx_color] == solve_upper_color[1][0]:
                mono_color_height += 1
            else:
                break

        # Нельзя переливать полностью заполненную колбу
        if mono_color_height == count_segments and count_segments == 4:
            continue

        solve_upper_color[1][1] = mono_color_height

        # Перебираем все колбы в которые можно перелить
        for idx_target_flask, target_flask in enumerate(position):
            count_segments = len(target_flask)
            # Переливать колбу саму в себя нельзя
            if idx_solve_flask != idx_target_flask:
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

                # В полную колбу ничего перелить нельзя, моно цвет в пустую колбу переливать бессмысленно
                if (target_upper_color[0][1] == count_segments - 1 and count_segments != 1) or \
                    (target_upper_color[1][0] == EMPTY and len(set(solve_flask)) == 2 and EMPTY in solve_flask):
                    continue

                # Избавляемся от "глупых" ходов с переливанием в ту колбу из которой выливали на прошлом ходу
                if last_move and target_upper_color[0][0] == last_move[0][0][0] and solve_upper_color[0][0] == last_move[1][0][0]:
                    continue

                # Переливание возможно только если верхние цвета совпадают или если переливаем в пустую колбу и места в целевой колбе достаточно
                if solve_upper_color[1][0] == target_upper_color[1][0] and target_upper_color[1][1] >= solve_upper_color[1][1]:
                    target_upper_color[0][1] += 1
                    target_upper_color[1][0] = EMPTY
                    moves.append([solve_upper_color, target_upper_color])
                elif target_upper_color[1][0] == EMPTY and target_upper_color[1][1] >= solve_upper_color[1][1]:
                    moves.append([solve_upper_color, target_upper_color])

    if len(moves) > 1:
        shuffle(moves)
    
    return moves


async def apply_move(position: list, move: tuple) -> tuple[list, str]:
    '''Функция для применения перемещения к текущему положению для получения нового'''
    # Получение данных о колбах, которые задействуются
    solve_flask, target_flask = move
    
    # Замена цвета в решающей колбе на пустое и заполнение места в целевой колбе 
    for cnt in range(solve_flask[1][1]):
        position[target_flask[0][0]][target_flask[0][1] + cnt] = solve_flask[1][0]
        position[solve_flask[0][0]][solve_flask[0][1] - cnt] = EMPTY
    step = f'{solve_flask[0][0] + 1} ➡️ {target_flask[0][0] + 1}'

    return position, step


async def go_back_move(position: list, move: tuple) -> list:
    '''Функция отмены перемещения'''
    # Получение данных о колбах, которые задействуются
    solve_flask, target_flask = move

    # Замена цвета в целевой колбе на пустое и заполнение места в решающей колбе
    for cnt in range(solve_flask[1][1]):
        position[solve_flask[0][0]][solve_flask[0][1] - cnt] = solve_flask[1][0]
        position[target_flask[0][0]][target_flask[0][1] + cnt] = target_flask[1][0]

    return position


async def transfusion_of_liquids(bot: Bot, chat_id: int, position: list) -> tuple[bool, any, any]:
    '''Функция перемещения цвета в текущей позиции и записи последовательности шагов'''
    now_position_tuple = tuple(tuple(flask) for flask in position)
    visited_states = set()
    stack = [[now_position_tuple, [], deque(await possible_moves(position))]]

    while stack:
        async with ChatActionSender.typing(bot=bot, chat_id=chat_id):
            now_position, steps, moves = stack[0]
            now_position = list(list(flask) for flask in now_position)
            steps = list(steps)

            # Проверяем решена ли задача
            if await check_solving(now_position):
                return True, steps, None
            
            if not moves:
                stack.pop(0)
                continue

            move = moves.popleft()

            # Применяем действие
            now_position, step = await apply_move(now_position, move)
            now_position_tuple = tuple(tuple(flask) for flask in now_position)

            # Если текущая позиция уже была посещена ранее, то возвращаем движение назад
            canonical_position = tuple(sorted(tuple(flask) for flask in now_position))
            if canonical_position in visited_states:
                await go_back_move(now_position, move)
                continue

            # Добавляем текущую позицию в список посещенных
            visited_states.add(canonical_position)
            steps.append(step)
            stack.insert(0, [now_position_tuple, tuple(steps), deque(await possible_moves(now_position, move))])

    return False, None, len(visited_states)


async def transfusion_manage(bot: Bot, chat_id: int, task: list) -> tuple[bool, any]:
    '''Основная функция модуля, регулирующая процесс переливания'''
    # Возвращаем флаг решения и список шагов, если решение есть
    is_solved, steps_list, count_states = await transfusion_of_liquids(bot, chat_id, task)
    if is_solved:
        result = ''
        cnt_block_moves = 0
        for step in steps_list:
            cnt_block_moves += 1
            result += step + '\n'
            if cnt_block_moves == 4:
                # Добавляем пустую строку, разбивая решение на блоки по 4 хода для удобства отслеживания
                cnt_block_moves = 0
                result += '\n'
        return is_solved, result, None

    return is_solved, None, count_states
