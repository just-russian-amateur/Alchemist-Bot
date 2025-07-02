'''Этот модуль отвечает за поиск и распознавание цветов в каждой колбе'''
import cv2
import numpy as np
import os


class BreakAction(Exception):
    pass


# Вместо строк с названиями цветов используются индексы (19 = 'UNDEFINED', 20 = 'EMPTY' - зарезервированные индексы)
variations = {
    'LIGHT BLUE': (0, (np.array((30, 50, 210), np.uint8), np.array((106, 255, 255), np.uint8)), (224, 161, 103)),
    'ORANGE': (1, (np.array((0, 165, 203), np.uint8), np.array((19, 255, 255), np.uint8)), (68, 144, 226)),
    'YELLOW': (2, (np.array((22, 46, 192), np.uint8), np.array((34, 255, 255), np.uint8)), (64, 185, 227)),
    'RED': (3, (np.array((0, 148, 114), np.uint8), np.array((7, 255, 255), np.uint8)), (30, 43, 173)),
    'LIGHT GREEN': (4, (np.array((41, 0, 160), np.uint8), np.array((65, 255, 255), np.uint8)), (70, 187, 108)),
    'BLUE': (5, (np.array((103, 181, 135), np.uint8), np.array((120, 255, 255), np.uint8)), (207, 90, 39)),
    'BURGUNDY': (6, (np.array((158, 135, 84), np.uint8), np.array((255, 255, 127), np.uint8)), (53, 32, 95)),
    'GREEN': (7, (np.array((86, 121, 86), np.uint8), np.array((96, 255, 255), np.uint8)), (100, 97, 46)),
    'PINK': (8, (np.array((140, 0, 197), np.uint8), np.array((154, 255, 255), np.uint8)), (219, 153, 212)),
    'PEACH': (9, (np.array((140, 88, 183), np.uint8), np.array((195, 255, 255), np.uint8)), (128, 109, 218)),
    'CREAM': (10, (np.array((0, 0, 241), np.uint8), np.array((20, 255, 255), np.uint8)), (194, 218, 248)),
    'PURPLE': (11, (np.array((131, 157, 186), np.uint8), np.array((255, 255, 255), np.uint8)), (201, 64, 132)),
    'GRAY': (12, (np.array((0, 0, 94), np.uint8), np.array((255, 29, 116), np.uint8)), (109, 107, 106)),
    'LILAC': (13, (np.array((117, 155, 136), np.uint8), np.array((125, 255, 255), np.uint8)), (187, 62, 71)),
    'LIME': (14, (np.array((70, 135, 70), np.uint8), np.array((81, 255, 255), np.uint8)), (106, 203, 52)),
    'MOSS': (15, (np.array((50, 135, 57), np.uint8), np.array((68, 255, 95), np.uint8)), (27, 87, 16)),
    'BROWN': (16, (np.array((12, 149, 82), np.uint8), np.array((23, 255, 132), np.uint8)), (23, 76, 119)),
    'CRIMSON': (17, (np.array((145, 199, 55), np.uint8), np.array((160, 255, 168), np.uint8)), (122, 5, 162)),
    'COCOA': (18, (np.array((0, 90, 184), np.uint8), np.array((10, 141, 255), np.uint8)), (111, 138, 202))
}


async def check_background(image: str) -> bool:
    '''Функция для проверки уровня на яркость заднего фона, для выбора подходящего подхода для распознавания'''
    gray_image = cv2.imread(image)
    height, width, _ = gray_image.shape
    hsv_image = cv2.cvtColor(gray_image, cv2.COLOR_BGR2HSV)
    # Эмпирически определенный порог для отделения фона от колб на изображении со светлым фоном
    thresholder = cv2.inRange(hsv_image, np.array((104, 90, 0), np.uint8), np.array((120, 223, 202), np.uint8))

    if cv2.countNonZero(thresholder) > 2 * ((height * width) - cv2.countNonZero(thresholder)):
        # Если белые пиксели занимают больше двух третей изображения, то считаем, что фон был светлым, иначе темный
        return True
    
    return False


async def preprocessing_image(image: str, light_background_flag: bool) -> cv2.typing.MatLike:
    '''Функция предобработки изображения'''
    # Чтение обрезанного изображения в ч/б формате
    gray_noise = cv2.imread(image, 0)
    # Размытие фона для ч/б изображения
    blurred = cv2.GaussianBlur(
        gray_noise,
        (5, 5),
        0
    )

    # Пороговая обработка изображения
    if light_background_flag:
        thresholder = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            81,
            1
        )
    else:
        thresholder = cv2.threshold(
            blurred,
            68,
            255,
            cv2.THRESH_BINARY
        )[1]

    return thresholder


async def found_rect(contour: cv2.typing.MatLike, my_list: list, height: int, width=None) -> tuple[list, np.intp]:
    '''Функция распознавания прямоугольника'''
    rect = cv2.minAreaRect(contour)
    box = np.intp(cv2.boxPoints(rect))
    if width == None:
        if rect[1][0] >= height and rect[1][1] >= height:
            my_list.append(rect)
    else:
        if (rect[2] < 30 and width <= rect[1][0] <= width * 1.75 and height <= rect[1][1] <= height * 1.75) or \
            (rect[2] > 60 and width <= rect[1][1] <= width * 1.75 and height <= rect[1][0] <= height * 1.75):
            # Добавляем прямоугольники с колбами в список
            my_list.append(rect)

    return my_list, box


async def crop_rects(contours: list, cropped_image: np.ndarray, id_client: int) -> list:
    '''Функция для выделения каждой отдельной колбы или цвета в ней для распознавания цветов'''
    flasks_info = []
    for cnt in contours:
        filename = f'./tmp/{id_client}_flask_{cnt}.jpg'
        # Взаимодействие с колбой
        if cnt[2] > 45:
            height_flask = [round(cnt[0][1] - cnt[1][0] / 2), round(cnt[0][1] + cnt[1][0] / 2)]
            width_flask = [round(cnt[0][0] - cnt[1][1] / 2), round(cnt[0][0] + cnt[1][1] / 2)]
        else:
            height_flask = [round(cnt[0][1] - cnt[1][1] / 2), round(cnt[0][1] + cnt[1][1] / 2)]
            width_flask = [round(cnt[0][0] - cnt[1][0] / 2), round(cnt[0][0] + cnt[1][0] / 2)]
        flask = cropped_image[height_flask[0]:height_flask[1], width_flask[0]:width_flask[1]]
        cv2.imwrite(filename, flask)
        flasks_info.append((filename, (width_flask[1] - width_flask[0], height_flask[1] - height_flask[0])))

    return flasks_info


async def create_color_list(image: str) -> list:
    '''Функция для создания списка колб с цветами вместо числовых значений'''
    # Более агрессивный подход для удаления ненужных шумов с изображения с использованием эрозии
    morph_kernel = np.ones((3, 3))
    erode_image = cv2.erode(cv2.imread(image), kernel=morph_kernel, iterations=3)
    cv2.imwrite(image, erode_image)
    color_pixels = cv2.imread(image)
    height, _, _ = color_pixels.shape
    hsv_colors = cv2.cvtColor(color_pixels, cv2.COLOR_BGR2HSV)

    colors_info, count_colors = [], []
    # Подбор коэффициентов
    height_color = round(height / 6.8)
    for variation in variations.values():
        # Проверяем пороговое значение для каждой вариации цвета на картинке и находим контуры
        thresholder = cv2.inRange(hsv_colors, variation[1][0], variation[1][1])
        contours_color, _ = cv2.findContours(
            thresholder,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )
        if contours_color:
            # В случае если контур был найден, определяем координаты и размеры прямоугольника с цветом
            color = []
            for cnt in contours_color:
                color_coords, _ = await found_rect(cnt, color, height_color)
            for cnt in color_coords:
                # Исключаем наложение прямоугольников друг на друга
                add_flag = True
                if len(colors_info) > 0:
                    for add_color in colors_info:
                        if abs(cnt[0][1] - add_color[1][1]) < height_color:
                            add_flag = False
                            break
                if add_flag == True:
                    # Добавляем в список информацию о цвете и его местоположении
                    color_id = variation[0]
                    colors_info.append([color_id, cnt[0], cnt[1], cnt[2]])
                    count_colors.append([variation[0]])
                    
    # Поддержка 2 и более цветов друг за другом
    if len(colors_info) > 1 and len(colors_info) < 4:
        min_color_rect = min(
            colors_info,
            key=lambda
            item:
            item[2][0]
        )[2][0]
        idx_line = 0
        while idx_line < len(colors_info):
            idx_height = 0
            if colors_info[idx_line][3] < 45:
                idx_height = 1

            if colors_info[idx_line][2][idx_height] > 3.25 * min_color_rect:
                for _ in range(2):
                    colors_info.insert(idx_line, colors_info[idx_line])
                idx_line += 3
            elif colors_info[idx_line][2][idx_height] > 1.75 * min_color_rect:
                colors_info.insert(idx_line, colors_info[idx_line])
                idx_line += 2
            else:
                idx_line += 1

    # Сортировка распознанных цветов
    colors_info = sorted(
        colors_info,
        key=lambda
        item:
        item[1][1],
        reverse=True
    )

    if len(colors_info) < 4 and len(colors_info) > 1:
        # Добавляем функционал для донатеров (когда между двумя элементами может быть неопределенный цвет)
        idx_line = 1
        while idx_line < len(colors_info): 
            current_idx_height, previos_idx_height = 0, 0
            if colors_info[idx_line][3] < 45:
                current_idx_height = 1
            if colors_info[idx_line - 1][3] < 45:
                previos_idx_height = 1
            
            previous_coord = colors_info[idx_line - 1][1][1] - colors_info[idx_line - 1][2][previos_idx_height] / 2
            current_coord = colors_info[idx_line][1][1] + colors_info[idx_line][2][current_idx_height] / 2
            if previous_coord - current_coord > min_color_rect:
                colors_info.insert(idx_line, [19, (0, colors_info[idx_line][1][1] + 1), (0, 0), 0])
                idx_line += 1
            idx_line += 1

    # Не учитываем пустые списки (пустые колбы будут добавляться отдельно)
    if len(colors_info) < 4 and len(colors_info) > 0: 
        # Добавляем неопределившиеся значения список цветов в колбе
        for _ in range(4 - len(colors_info)):
            colors_info.insert(0, [19, (0, height), (0, 0), 0])
    
    return colors_info


async def sorted_flasks(flasks_id_list: list) -> list:
    '''Пользовательская функция для сортировки колб в нужном порядке'''
    min_coord = min(
        flasks_id_list,
        key=lambda
        item:
        item[0][1]
    )[0][1]
    max_flask_height = max(
        flasks_id_list,
        key=lambda
        item:
        item[1][0]
    )[1][0]
    layer_height = max_flask_height * 1.55
    sorted_flask_list, layer_1, layer_2, layer_3 = [], [], [], []
    
    for coord_flask in flasks_id_list:
        number_layer = round((coord_flask[0][1] - min_coord) / layer_height)
        if number_layer == 0:
            layer_1.append(coord_flask)
        elif number_layer == 1:
            layer_2.append(coord_flask)
        elif number_layer == 2:
            layer_3.append(coord_flask)
    
    if len(layer_1) != 0:
        layer_1 = sorted(layer_1)
    if len(layer_2) != 0:
        layer_2 = sorted(layer_2)
    if len(layer_3) != 0:
        layer_3 = sorted(layer_3)

    for element in layer_1:
        sorted_flask_list.append(element)
    for element in layer_2:
        sorted_flask_list.append(element)
    for element in layer_3:
        sorted_flask_list.append(element)

    return sorted_flask_list


async def replace_undefined(flasks_id_list: list) -> dict:
    '''Функция для составления списка неопределенных значений недостающими цветами'''
    # Подготовление списка с цвтеами и их количеством, которые нужно добавить
    flasks_id_list = np.asarray(flasks_id_list)
    colors_id, counts = np.unique(flasks_id_list, return_counts=True)
    # Приведение ключей numpy.int32 к типу int
    colors_dict = {int(k): int(v) for k, v in zip(colors_id, counts)}
    added_colors = dict()
    for key in colors_dict.keys():
        if colors_dict[key] < 4:
            if key != 19:
                added_colors[key] = int(4 - colors_dict[key])
    return added_colors


async def found_colors_in_flasks(image_for_search: str, id_client: int, reload_image=False) -> tuple[dict, list]:
    '''
    Основная функция для распознавания цветов на картинке и добавления их в массив
    В ходе тестирования на разных разрешениях экрана были получены следующие эмпирические значения:
    - Коэффициент отношения ширины экрана к ширине колбы (11.82)
    - Коэффициент отношения высоты колбы к ширине колбы (3.74)
    - Коэффициент отношения пустого пространства между слоями колб к высоте колбы (0.4)
    - Коэффициент отношения высоты нижнего слоя кнопок к ширине колбы (1)
    - Эмпирическая формула для определения рамки с колбами по которой надо обрезать:
        - Для дисплеев с коэффициентом отношения высоты к ширине >= 2.0:
            Высота колбы = Ширина экрана / коэффициент ширины экрана и колбы * коэффициент высоты колбы к ширине
            Высота колбы * (максимальное количество слоев колб (3) + количество пустых пространств (4) * коэффициент высот колбы и пустого простарнства)
        - Для дисплеев с коэффициентом отношения высоты к ширине < 2.0:
            Высота колбы = Ширина экрана / коэффициент ширины экрана и колбы * коэффициент высоты колбы к ширине
            Высота колбы * (максимальное количество слоев колб (3) + количество пустых пространств (3) * коэффициент высот колбы и пустого простарнства)
    - Высота нижнего отступа до начала рамки с колбами (3.5 или 4.5 (для коэффициента отношения сторон >= 2) высоты нижних кнопок)
    '''
    # Чтение изображения в цветном формате
    original_image = cv2.imread(image_for_search)
    # Получение параметров размера изображения и вывод параметров обрезки
    height, width, _ = original_image.shape
    # Задаем эмпирически полученные коэффициенты отношения высоты и ширины экрана к высоте и ширине колбы
    width_flask = round(width / 11.82)
    height_flask = round(width_flask * 3.74)
    if reload_image == False:
        if height / width < 2:
            flasks_frame = round(height_flask * 4.2)
            indent_down = round(width_flask * 3.5)
        else:
            flasks_frame = round(height_flask * 4.6)
            indent_down = round(width_flask * 4.5)
        cropped_height = [round(height - indent_down - flasks_frame), round(height - indent_down)]
    else:
        cropped_height = [0, height]
    # Обрзка изображения под определенные границы (чтобы были видны только колбы)
    cropped_image = original_image[cropped_height[0]:cropped_height[1], 0:width]
    cv2.imwrite(image_for_search, cropped_image)
    # Предобработка начального изображения после кропа
    # Определение яркости заднего фона для корректировки порога для обработки
    light_background_flag = await check_background(image_for_search)
    # Определение контуров элементов и их отрисовка на цветном изображении
    contours_of_flasks, _ = cv2.findContours(
        await preprocessing_image(image_for_search, light_background_flag),
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    flasks = [] # Список прямоугольников-колб
    # Проходим по всем контурам и подсвечиваем прямоугольники целых колб
    for contour in contours_of_flasks:
        # Определение границ прямоугольников и добавление цвета прямоугольника в список
        flasks, _ = await found_rect(contour, flasks, height_flask, width_flask)
    flasks = await sorted_flasks(flasks)
    images_of_flasks = await crop_rects(flasks, cropped_image, id_client)

    flasks_id_list = []    # Список цветов в колбах
    for images_contour in images_of_flasks:
        # Находим контуры цветов внутри каждой колбы
        colors_list = await create_color_list(images_contour[0])
        if colors_list:
            colors = []
            for color in colors_list:
                colors.append(color[0])
            flasks_id_list.append(colors)
    
    # Вручную добавляем 2 пустые колбы
    for _ in range(2):
        flasks_id_list.append([20, 20, 20, 20])

    # Удаление всех временных файлов для экономии места
    for flask_info in images_of_flasks:
        os.remove(flask_info[0])

    return await replace_undefined(flasks_id_list), flasks_id_list


async def replace_in_list(flasks_id_list: list, color_id: int) -> list:
    '''Функция для замены неопределенных цветов на выбранные пользователем'''
    try:
        for flask in flasks_id_list:
            for color in range(len(flask)):
                if flask[color] == 19:
                    flask[color] = color_id
                    raise BreakAction
    except BreakAction:
        pass

    return flasks_id_list


async def create_image_for_replace(flasks_id_list: list, id_client: int):
    '''Функция для отрисовки изображения с подсветкой того цвета, который нужно заполнить'''
    # Создание и сохранение пустого черного изображения
    filename = f'./tmp/level_for_{id_client}.jpg'
    height, width = 1800, 1400
    template = np.zeros((height, width, 3), np.uint8)
    cv2.imwrite(filename, template)

    # Установка количества линий с колбами и размеров колбы
    count_flasks = len(flasks_id_list)
    width_flask = 100
    count_lines = np.trunc(count_flasks / 6) + 1
    flasks_centers = []
    # Заполнение массива с центрами колб
    try:
        for y in range(int(height / (count_lines + 1)), height, int(height / (count_lines + 1))):
            for x in range(int(width / 7), width, int(width / 7)):
                flasks_centers.append([x, y])
                if len(flasks_centers) == count_flasks:
                    raise BreakAction
    except BreakAction:
        pass
    
    cnt_undef = 0
    # Отрисовка всех колб с цветами и пустыми полями внутри них
    for colors in range(count_flasks):
        height_flask = width_flask * len(flasks_id_list[colors])
        
        x1, y1 = flasks_centers[colors][0] - width_flask / 2, flasks_centers[colors][1] - height_flask / 2
        x2, y2 = flasks_centers[colors][0] + width_flask / 2, flasks_centers[colors][1] + height_flask / 2
        flask_rect = cv2.rectangle(template, (int(x1), int(y1)), (int(x2), int(y2)), (176, 176, 90), 6)
        cv2.imwrite(filename, flask_rect)

        for color in range(len(flasks_id_list[colors])):
            circle_x, circle_y = flasks_centers[colors][0], y2 - (y2 - y1) * (2 * color + 1) / 8
            for variation in variations.values():
                if flasks_id_list[colors][color] == 19:
                    cnt_undef += 1
                    if cnt_undef == 1:
                        color_circle = cv2.circle(template, (int(circle_x), int(circle_y)), 47, (0, 255, 0), 6)
                    else:
                        color_circle = cv2.circle(template, (int(circle_x), int(circle_y)), 47, (255, 255, 255), 6)
                    cv2.imwrite(filename, color_circle)
                    break
                elif flasks_id_list[colors][color] == variation[0]:
                    color_circle = cv2.circle(template, (int(circle_x), int(circle_y)), 47, variation[2], -1)
                    cv2.imwrite(filename, color_circle)
                    break


async def add_empty_flask(flasks_id_list: list, idx_segment: int) -> list:
    '''Функция для добавления пустой части колбы в конец'''
    if idx_segment == 1:
        flasks_id_list.append([20])
    else:
        flasks_id_list.pop()
        new_segment = []
        for _ in range(idx_segment):
            new_segment.append(20)
        flasks_id_list.append(new_segment)
    return flasks_id_list
