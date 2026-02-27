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
    'GREEN': (7, (np.array((86, 121, 86), np.uint8), np.array((96, 255, 108), np.uint8)), (100, 97, 46)),
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
    morph_kernel = np.ones((3, 3))
    hsv_colors = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    for i in range(3, 33, 8):
        y1, y2, x1, x2 = round(height*i/32), round(height*(i+2)/32), round(width*3/8), round(width*5/8)
        segment = hsv_colors[y1:y2, x1:x2]

        # Более агрессивный подход для удаления ненужных шумов с изображения с использованием эрозии
        segment = cv2.erode(segment, kernel=morph_kernel, iterations=3)

        OK_COLOR = False
        for variation in variations.values():
            # Проверяем пороговое значение для каждой вариации цвета на картинке и находим площадь, которую занимает цвет
            thresholder = cv2.inRange(segment, variation[1][0], variation[1][1])
            if cv2.countNonZero(thresholder) / thresholder.size > 0.51:
                segments.append(variation[0])
                OK_COLOR = True
                break

        if not OK_COLOR:
            cnt_undefined += 1
            segments.append(UNDEFINED)
        
        if cnt_undefined == 4:
            return [EMPTY] * 4
    
    return segments[::-1]


async def sorted_flasks(flasks_id_list: list) -> list:
    '''Пользовательская функция для сортировки колб в нужном порядке'''
    sorted_flasks_list = []
    flasks_id_list.sort(key=lambda item: item[1])
    layer = []
    for flask in flasks_id_list:
        if not layer:
            layer.append(flask)
            continue

        if flask[1] - layer[0][1] < 25:
            layer.append(flask)
        else:
            layer.sort()
            sorted_flasks_list.extend(layer)
            layer = [flask]
    
    if layer:
        layer.sort()
        sorted_flasks_list.extend(layer)

    return sorted_flasks_list


async def replace_undefined(flasks_id_list: list) -> dict:
    '''Функция для составления списка неопределенных значений недостающими цветами'''
    # Подготовление списка с цвтеами и их количеством, которые нужно добавить
    flasks_id_list = np.array(flasks_id_list)
    colors_id, counts = np.unique(flasks_id_list, return_counts=True)
    # Приведение ключей numpy.int32 к типу int
    colors_dict = {int(k): int(v) for k, v in zip(colors_id, counts)}
    added_colors = dict()

    if UNDEFINED not in colors_dict:
        return added_colors
    
    for key in colors_dict.keys():
        if colors_dict[key] >= 4:
            continue
            
        if key != UNDEFINED:
            added_colors[key] = int(4 - colors_dict[key])
    
    # Случай, когда пользователь еще не открыл все варианты цветов хотя бы в одном экземпляре
    if flasks_id_list.shape[0] > len(colors_dict):
        for _ in range(flasks_id_list.shape[0] - len(colors_dict)):
            for variation in variations.keys():
                if not variations[variation][0] in added_colors.keys():
                    added_colors[variations[variation][0]] = 4
                    break

    return added_colors


async def found_colors_in_flasks(image_for_search: str) -> tuple[dict, list]:
    '''Основная функция для распознавания цветов на картинке и добавления их в массив'''
    # Чтение изображения в цветном формате
    original_image = cv2.imread(image_for_search)

    boxes = model(original_image)[0].boxes
    flasks = [] # Список прямоугольников-колб

    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        w, h = x2 - x1, y2 - y1
        
        if 3 * w < h < 4 * w:
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
    for flask in flasks_id_list:
        for i, color in enumerate(flask):
            if color == UNDEFINED:
                flask[i] = color_id
                return flasks_id_list
            
    return flasks_id_list


async def replace_selected_color(flasks_id_list: list, color_id: int, choosen_flask: int, choosen_segment: int) -> list:
    '''Функция для замены выбранного пользователем сегмента в колбе другим цветом'''
    flasks_id_list[choosen_flask][choosen_segment] = color_id

    return flasks_id_list


async def remove_selected_flask(flasks_id_list: list, choosen_flask: int) -> list:
    '''Функция для удаления лишней колбы, выбранной пользователем'''
    flasks_id_list.pop(choosen_flask)

    return flasks_id_list


async def create_image_for_replace(flasks_id_list: list, id_client: int):
    '''Функция для отрисовки изображения с подсветкой того цвета, который нужно заполнить'''
    # Создание и сохранение пустого черного изображения
    filename = f'./tmp/level_for_{id_client}.jpg'
    height, width = 1800, 1400
    template = np.zeros((height, width, 3), np.uint8)

    # Установка количества линий с колбами и размеров колбы
    count_flasks = len(flasks_id_list)
    width_flask = 100
    count_lines = int(np.ceil(count_flasks / 6))
    flasks_centers = []

    # Заполнение массива с центрами колб
    step_y = height / (count_lines + 1)
    step_x = width / 7
    for i in range(count_lines):
        for j in range(1, 7):
            flasks_centers.append([int(j * step_x), int((i + 1) * step_y)])
            if len(flasks_centers) >= count_flasks:
                break

        if len(flasks_centers) >= count_flasks:
            break
    
    cnt_undef = 0
    # Отрисовка всех колб с цветами и пустыми полями внутри них
    for idx_flask, colors in enumerate(flasks_id_list):
        height_flask = width_flask * len(colors)
        cx, cy = flasks_centers[idx_flask]
        
        x1, y1 = int(cx - width_flask / 2), int(cy - height_flask / 2)
        x2, y2 = int(cx + width_flask / 2), int(cy + height_flask / 2)
        
        cv2.rectangle(template, (x1, y1), (x2, y2), (176, 176, 90), 6)

        for idx_color, color in enumerate(colors):
            circle_x, circle_y = cx, int(y2 - (y2 - y1) * (2 * idx_color + 1) / 8)
            
            if color == UNDEFINED:
                cnt_undef += 1
                if cnt_undef == 1:
                    circle_color = (0, 255, 0)
                else:
                    circle_color = (255, 255, 255)
                cv2.circle(template, (circle_x, circle_y), 47, circle_color, 6)
            elif color < UNDEFINED:
                cv2.circle(template, (circle_x, circle_y), 47, list(variations.values())[color][2], -1)

    cv2.imwrite(filename, template)


async def add_empty_flask(flasks_id_list: list, idx_segment: int) -> list:
    '''Функция для добавления пустой части колбы в конец'''
    if idx_segment == 1:
        flasks_id_list.append([EMPTY])
    else:
        flasks_id_list.pop()
        flasks_id_list.append([EMPTY] * idx_segment)
        
    return flasks_id_list
