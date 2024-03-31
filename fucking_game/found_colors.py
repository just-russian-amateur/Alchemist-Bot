'''Этот модуль отвечает за поиск и распознавание цветов в каждой колбе'''
import cv2
import numpy as np
import json
import os


variations = [
    ('LIGHTBLUE', (np.array((30, 50, 210), np.uint8), np.array((106, 255, 255), np.uint8))),
    ('ORANGE', (np.array((0, 165, 203), np.uint8), np.array((19, 255, 255), np.uint8))),
    ('YELLOW', (np.array((22, 46, 192), np.uint8), np.array((34, 255, 255), np.uint8))),
    ('RED', (np.array((0, 148, 114), np.uint8), np.array((7, 255, 255), np.uint8))),
    ('LIGHTLIGHT', (np.array((41, 0, 160), np.uint8), np.array((65, 255, 255), np.uint8))),
    ('BLUE', (np.array((103, 181, 135), np.uint8), np.array((120, 255, 255), np.uint8))),
    ('BURGUNDY', (np.array((158, 135, 84), np.uint8), np.array((255, 255, 127), np.uint8))),
    ('GREEN', (np.array((86, 121, 86), np.uint8), np.array((96, 255, 255), np.uint8))),
    ('PINK', (np.array((140, 0, 197), np.uint8), np.array((154, 255, 255), np.uint8))),
    ('CRIMSON', (np.array((140, 88, 183), np.uint8), np.array((195, 255, 255), np.uint8))),
    ('CREAM', (np.array((0, 0, 241), np.uint8), np.array((20, 255, 255), np.uint8))),
    ('PURPLE', (np.array((131, 157, 186), np.uint8), np.array((255, 255, 255), np.uint8))),
    ('GRAY', (np.array((0, 0, 94), np.uint8), np.array((255, 29, 116), np.uint8))),
    ('LILAC', (np.array((117, 155, 136), np.uint8), np.array((125, 255, 255), np.uint8)))
]


def preprocessing_image(image):
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
    thresholder = cv2.threshold(
        blurred,
        68,
        255,
        cv2.THRESH_BINARY
    )[1]

    return thresholder


def found_rect(contour, my_list, coeff_width, coeff_height, is_flask):
    '''Функция распознавания прямоугольника'''
    rect = cv2.minAreaRect(contour)
    box = np.intp(cv2.boxPoints(rect))
    if is_flask ==True:
        if rect[1][0] >= coeff_height and rect[1][1] >= coeff_height:
            my_list.append(rect)
    else:
        if (rect[1][0] >= rect[1][1] and rect[1][1] >= coeff_width and rect[1][0] >= coeff_height) or \
            (rect[1][0] < rect[1][1] and rect[1][0] >= coeff_width and rect[1][1] >= coeff_height):
            # Добавляем прямоугольники с колбами в список
            my_list.append(rect)

    return my_list, box


def crop_rects(contours, cropped_image):
    '''Функция для выделения каждой отдельной колбы или цвета в ней для распознавания цветов'''
    flasks_info = []
    for cnt in contours:
        filename = f'./images/flask_{cnt}.jpg'
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


def create_color_list(image):
    '''Функция для создания списка колб с цветами вместо числовых значений'''
    # Более агрессивный подход для удаления ненужных шумов с изображения с использованием эрозии
    morph_kernel = np.ones((3, 3))
    erode_image = cv2.erode(cv2.imread(image), kernel=morph_kernel, iterations=3)
    cv2.imwrite(image, erode_image)
    color_pixels = cv2.imread(image)
    height, width, _ = color_pixels.shape
    hsv_colors = cv2.cvtColor(color_pixels, cv2.COLOR_BGR2HSV)

    colors_info, count_colors = [], []
    # Подбор коэффициентов
    coeff_width = round(width / 1.5)
    coeff_height = round(height / 6.8)
    for variation in variations:
        # Проверяем пороговое значение для каждой вариации цвета на картинке и находим контуры
        thresholder = cv2.inRange(hsv_colors, variation[1][0], variation[1][1])
        contours_color, _ = cv2.findContours(
            thresholder,
            cv2.RETR_TREE,
            cv2.CHAIN_APPROX_SIMPLE
        )

        if len(contours_color) != 0:
            # В случае если контур был найден, определяем координаты и размеры прямоугольника с цветом
            color = []
            for cnt in contours_color:
                color_coords, _ = found_rect(cnt, color, coeff_width, coeff_height, is_flask=True)
            for cnt in color_coords:
                # Исключаем наложение прямоугольников друг на друга
                add_flag = True
                if len(colors_info) > 0:
                    for add_color in colors_info:
                        if abs(cnt[0][1] - add_color[1][1]) < 38:
                            add_flag = False
                            break
                if add_flag == True:
                    # Добавляем в список информацию о цвете и его местоположении
                    color_name = variation[0]
                    colors_info.append([color_name, cnt[0]])
                    count_colors.append([variation[0]])
    
    # Добавляем абсолютно пустую колбу, если список пуст
    if len(colors_info) == 0:
        for i in range(4):
            colors_info.append(['EMPTY', (0, i)])

    if len(colors_info) < 4:
        # Добавляем неопределившиеся значения список цветов в колбе
        for i in range(4 - len(colors_info)):
            colors_info.append(['UNDEFINED', (0, height)])
    
    return colors_info


def sorted_flasks(flasks_list):
    '''Пользовательская функция для сортировки колб в нужном порядке'''
    min_coord = min(
        flasks_list,
        key=lambda
        item:
        item[0][1]
    )[0][1]
    max_flask_height = max(
        flasks_list,
        key=lambda
        item:
        item[1][0]
    )[1][0]
    layer_height = max_flask_height * 1.55
    sorted_flask_list, layer_1, layer_2, layer_3 = [], [], [], []
    
    for coord_flask in flasks_list:
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


def replace_undefined(flasks_list):
    '''Функция для составления списка неопределенных значений недостающими цветами'''
    # Подготовление списка с цвтеами и их количеством, которые нужно добавить
    flasks_list = np.asarray(flasks_list)
    colors, counts = np.unique(flasks_list, return_counts=True)
    colors_dict = dict(zip(colors, counts))
    added_colors = dict()
    for key in colors_dict.keys():
        if colors_dict[key] < 4:
            added_colors.update(key=4 - colors_dict[key])
    return added_colors


def found_colors_in_flasks(image_for_search, id):
    '''Основная функция для распознавания цветов на картинке и добавления их в массив'''
    # Чтение изображения в цветном формате
    original_image = cv2.imread(image_for_search)
    # Получение параметров размера изображения и вывод параметров обрезки
    height, width, _ = original_image.shape
    cropped_height = [round(height * 0.125), round(height * 0.875)]
    # Обрзка изображения под определенные границы (чтобы были видны только колбы)
    cropped_image = original_image[cropped_height[0]:cropped_height[1], 0:width]
    cv2.imwrite(image_for_search, cropped_image)
    # Предобработка начального изображения после кропа
    # Определение контуров элементов и их отрисовка на цветном изображении
    contours_of_flasks, _ = cv2.findContours(
        preprocessing_image(image_for_search),
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Задаем эмпирически полученные коэффициенты отношения высоты и ширины экрана к высоте и ширине колбы
    coeff_width_flask = round(width / 11)
    coeff_height_flask = round((cropped_height[1] - cropped_height[0]) / 5.2)
    flasks = [] # Список прямоугольников-колб
    # Проходим по всем контурам и подсвечиваем прямоугольники целых колб
    for contour in contours_of_flasks:
        # Определение границ прямоугольников и добавление цвета прямоугольника в список
        flasks, _ = found_rect(contour, flasks, coeff_width_flask, coeff_height_flask, is_flask=False)
    flasks = sorted_flasks(flasks)
    images_of_flasks = crop_rects(flasks, cropped_image)

    flasks_list = []    # Список цветов в колбах
    for images_contour in images_of_flasks:
        # Находим контуры цветов внутри каждой колбы
        internal_colors = []
        colors_list = create_color_list(images_contour[0])
        for colors_contours in colors_list:
            internal_colors.append((colors_contours[0], colors_contours[1]))
        internal_colors = sorted(
            internal_colors,
            key=lambda
            item:
            item[1][1],
            reverse=True
        )
        
        colors = []
        for color in internal_colors:
            colors.append(color[0])
        flasks_list.append(colors)
    
    # Удаление всех временных файлов для экономии места
    for flask_info in images_of_flasks:
        os.remove(flask_info[0])

    create_json(flasks_list, id)

    return replace_undefined(flasks_list)


def create_json(flasks_list, id_client):
    '''Создание и заполнение json файла с распознанными цветами'''
    with open(f"./levels/start_level_{id_client}.json", "w") as this_level:
        json.dump({"bottles": flasks_list}, this_level, indent=2)
