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
    

def move_colors(position):
    '''Функция перемещения цвета в текущей позиции'''
    pass
    # return new_position


def write_step():
    '''Функция записи шагов решения'''
    pass
    # return steps_list


def transfusion_manage(task, result):
    '''Основная функция модуля, регулирующая процесс переливания'''
    # Вызываем функцию для считывания файлов из json
    start_position = get_level_from_json(task)
    
    is_attempt_completed = False
    more_moves = True
    buffer = []
    intermediate = move_colors(start_position)  # Делаем первое перемещение
    while is_attempt_completed == False:
        full_color = 0
        for flask in intermediate:
            # После очередного перемещения проходим по списку колб
            if flask[0] == flask[1] == flask[2] == flask[3]:
                full_color += 1
            else:
                return

        if full_color == len(start_position):
            # Количество одноцветных колб совпадает с количеством колб
            steps_list = write_step()
            is_attempt_completed = True
        else:
            if more_moves == True:
                # Если есть путь для перемещения, то делаем следующее перемешение...
                buffer.append(intermediate)
                intermediate = move_colors(intermediate)
            else:
                # ...если такого пути нет, то возвращаемся на шаг назад или выходим из цикла если возвращаться некуда
                if len(steps_list) == 0:
                    # Решения нет
                    is_attempt_completed = True
                else:
                    steps_list.pop()
                    intermediate = buffer.pop()

    return send_result_to_txt(result, steps_list)
