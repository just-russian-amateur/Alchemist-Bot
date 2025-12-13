'''Этот модуль отвечает за поиск и распознавание цветов в каждой колбе'''
import cv2
import numpy as np
from config import model


class BreakAction(Exception):
    pass


# Вместо строк с названиями цветов используются индексы
# Последние 5 цветов были добавлены позже
UNDEFINED = 25
EMPTY = 26
variations = {
    'LIGHT BLUE': (0, (np.array((30, 50, 210), np.uint8), np.array((106, 255, 255), np.uint8)), (224, 161, 103)),
    'ORANGE': (1, (np.array((0, 136, 203), np.uint8), np.array((19, 227, 255), np.uint8)), (68, 144, 226)),
    'YELLOW': (2, (np.array((22, 125, 192), np.uint8), np.array((34, 255, 255), np.uint8)), (64, 185, 227)),
    'RED': (3, (np.array((0, 148, 69), np.uint8), np.array((7, 255, 255), np.uint8)), (30, 43, 173)),
    'LIGHT GREEN': (4, (np.array((41, 0, 162), np.uint8), np.array((65, 255, 255), np.uint8)), (70, 187, 108)),
    'BLUE': (5, (np.array((103, 183, 135), np.uint8), np.array((120, 255, 255), np.uint8)), (207, 90, 39)),
    'BURGUNDY': (6, (np.array((167, 143, 84), np.uint8), np.array((178, 255, 127), np.uint8)), (53, 32, 95)),
    'GREEN': (7, (np.array((86, 121, 86), np.uint8), np.array((96, 255, 100), np.uint8)), (100, 97, 46)),
    'PINK': (8, (np.array((140, 11, 130), np.uint8), np.array((162, 173, 255), np.uint8)), (219, 153, 212)),
    'PEACH': (9, (np.array((140, 103, 183), np.uint8), np.array((195, 191, 255), np.uint8)), (128, 109, 218)),
    'CREAM': (10, (np.array((0, 25, 230), np.uint8), np.array((20, 82, 255), np.uint8)), (194, 218, 248)),
    'PURPLE': (11, (np.array((131, 137, 90), np.uint8), np.array((152, 255, 255), np.uint8)), (201, 64, 132)),
    'GRAY': (12, (np.array((0, 0, 94), np.uint8), np.array((255, 37, 152), np.uint8)), (109, 107, 106)),
    'LILAC': (13, (np.array((117, 16, 135), np.uint8), np.array((132, 255, 255), np.uint8)), (187, 62, 71)),
    'LIME': (14, (np.array((70, 135, 70), np.uint8), np.array((81, 255, 255), np.uint8)), (106, 203, 52)),
    'MOSS': (15, (np.array((50, 135, 57), np.uint8), np.array((68, 255, 138), np.uint8)), (27, 87, 16)),
    'BROWN': (16, (np.array((14, 66, 65), np.uint8), np.array((23, 255, 141), np.uint8)), (23, 76, 119)),
    'CRIMSON': (17, (np.array((153, 146, 104), np.uint8), np.array((167, 255, 255), np.uint8)), (122, 5, 162)),
    'COCOA': (18, (np.array((0, 78, 184), np.uint8), np.array((11, 141, 255), np.uint8)), (111, 138, 202)),
    'DARK BLUE': (19, (np.array((119, 68, 41), np.uint8), np.array((139, 173, 132), np.uint8)), (128, 42, 50)),
    'INDIGO': (20, (np.array((105, 114, 160), np.uint8), np.array((108, 182, 205), np.uint8)), (201, 125, 59)),
    'PALE GREEN': (21, (np.array((52, 35, 139), np.uint8), np.array((59, 120, 161), np.uint8)), (92, 157, 101)),
    'DIRTY CREAM': (22, (np.array((16, 76, 126), np.uint8), np.array((30, 142, 246), np.uint8)), (109, 174, 219)),
    'AQUA': (23, (np.array((80, 58, 127), np.uint8), np.array((98, 255, 255), np.uint8)), (197, 202, 87)),
    'DARK ORANGE': (24, (np.array((9, 151, 124), np.uint8), np.array((13, 255, 213), np.uint8)), (13, 86, 207))
}


async def create_color_list(image: cv2.typing.MatLike) -> list:
    '''Функция для создания списка колб с цветами вместо числовых значений'''
    # Делим колбу на 4 равных сегмента и работаем с каждым сегментом отдельно
    segments = []
    height, width, _ = image.shape
    cnt_undefined = 0
    for i in range(3, 33, 8):
        height_seg, width_seg = round(height*(i+2)/32) - round(height*i/32), round(width*5/8) - round(width*3/8)

        segment = image[round(height*i/32):round(height*(i+2)/32), round(width*3/8):round(width*5/8)]
        # Более агрессивный подход для удаления ненужных шумов с изображения с использованием эрозии
        morph_kernel = np.ones((3, 3))
        erode_image = cv2.erode(segment, kernel=morph_kernel, iterations=3)
        hsv_colors = cv2.cvtColor(erode_image, cv2.COLOR_BGR2HSV)

        try:
            OK_COLOR = False
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
                    for cnt in contours_color:
                        rect = cv2.minAreaRect(cnt)
                        if rect[1][0] * rect[1][1] >= height_seg * width_seg * 0.51:
                            segments.insert(0, variation[0])
                            OK_COLOR = True
                            raise BreakAction
        except BreakAction:
            pass

        if not OK_COLOR:
            cnt_undefined += 1
            segments.insert(0, UNDEFINED)
        
        if cnt_undefined == 4:
            segments = [EMPTY, EMPTY, EMPTY, EMPTY]
    
    return segments


async def sorted_flasks(flasks_id_list: list) -> list:
    '''Пользовательская функция для сортировки колб в нужном порядке'''
    sorted_flasks_list = []
    flasks_id_list.sort(key=lambda item: item[1])
    layer = []
    for flask in flasks_id_list:
        if not layer:
            layer.append(flask)
        else:
            if flask[1] - layer[0][1] < 25:
                layer.append(flask)
            else:
                layer.sort()
                sorted_flasks_list += layer.copy()
                layer.clear()
                layer.append(flask)
    layer.sort()
    sorted_flasks_list += layer.copy()

    return sorted_flasks_list


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
            if key != UNDEFINED:
                added_colors[key] = int(4 - colors_dict[key])
    
    # Случай, когда пользователь еще не открыл все варианты цветов хотя бы в одном экземпляре
    if flasks_id_list.shape[0] > len(colors_dict):
        for _ in range(flasks_id_list.shape[0] - len(colors_dict)):
            for variation in variations.keys():
                if not variations[variation][0] in sorted(added_colors.keys()):
                    added_colors[variations[variation][0]] = 4
                    break

    return added_colors


async def found_colors_in_flasks(image_for_search: str) -> tuple[dict, list]:
    '''Основная функция для распознавания цветов на картинке и добавления их в массив'''
    # Чтение изображения в цветном формате
    original_image = cv2.imread(image_for_search)

    boxes = model(image_for_search)[0].boxes
    flasks = [] # Список прямоугольников-колб

    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        w, h = x2 - x1, y2 - y1
        ratio = h / w
        
        if 3 < ratio < 4:
            flasks.append([x1, y1, x2, y2])

    flasks = await sorted_flasks(flasks)
    flasks_info = []
    for cnt in flasks:
        flask = original_image[cnt[1]:cnt[3], cnt[0]:cnt[2]]
        flasks_info.append(flask)

    flasks_id_list = []    # Список цветов в колбах
    for flask_contour in flasks_info:
        # Находим контуры цветов внутри каждой колбы
        colors_list = await create_color_list(flask_contour)
        flasks_id_list.append(colors_list)

    return await replace_undefined(flasks_id_list), flasks_id_list


async def replace_in_list(flasks_id_list: list, color_id: int) -> list:
    '''Функция для замены неопределенных цветов на выбранные пользователем'''
    try:
        for flask in flasks_id_list:
            for color in range(len(flask)):
                if flask[color] == UNDEFINED:
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
            idx_color = flasks_id_list[colors][color]
            if idx_color == UNDEFINED:
                cnt_undef += 1
                if cnt_undef == 1:
                    color_circle = cv2.circle(template, (int(circle_x), int(circle_y)), 47, (0, 255, 0), 6)
                else:
                    color_circle = cv2.circle(template, (int(circle_x), int(circle_y)), 47, (255, 255, 255), 6)
                cv2.imwrite(filename, color_circle)
            elif idx_color < UNDEFINED:
                color_circle = cv2.circle(template, (int(circle_x), int(circle_y)), 47, list(variations.values())[idx_color][2], -1)
                cv2.imwrite(filename, color_circle)


async def add_empty_flask(flasks_id_list: list, idx_segment: int) -> list:
    '''Функция для добавления пустой части колбы в конец'''
    if idx_segment == 1:
        flasks_id_list.append([EMPTY])
    else:
        flasks_id_list.pop()
        new_segment = []
        for _ in range(idx_segment):
            new_segment.append(EMPTY)
        flasks_id_list.append(new_segment)
    return flasks_id_list
