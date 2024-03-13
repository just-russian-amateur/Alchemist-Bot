'''Этот модуль отвечает за поиск и распознавание цветов в каждой колбе'''
import cv2
import numpy as np
import json


variations = [
    'BLUE', 'ORANGE', 'YELLOW', 'RED', 'GREEN', 'DARKBLUE', 'DARKRED', 'DARKGREEN',
    'PINK', 'DARKPINK', 'LIGHTPINK', 'PURPLE', 'GRAY', 'LILAC', 'EMPTY', 'UNDEFINED'
]


def draw_contours(file, box, color):
    '''Временная функция для визуализации границ'''
    cv2.imwrite(
        file,
        cv2.drawContours(
            cv2.imread(file),
            [box],
            0,
            color,
            2
        )
    )


def preprocessing_image(image):
    '''Функция предобработки изображения'''
    image_for_sharp = cv2.imread(image)
    sharp_filter = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    sharped_image = cv2.filter2D(image_for_sharp, ddepth=-1, kernel=sharp_filter)
    cv2.imwrite(image, sharped_image)

    # CLAHE (Contrast Limited Adaptive Histogram Equalization) - Повышение контрастности
    # clahe = cv2.createCLAHE(clipLimit=0.1, tileGridSize=(8,8))
    # lab = cv2.imread(image)
    # lab = cv2.cvtColor(lab, cv2.COLOR_BGR2LAB)  # Конвертация RGB в LAB
    # l, a, b = cv2.split(lab)  # Разделение на 3 канала
    # l2 = clahe.apply(l)  # Применение коэффициента к каналу яркости
    # lab = cv2.merge((l2,a,b))  # Слияние каналов
    # cv2.imwrite(image, cv2.cvtColor(lab, cv2.COLOR_LAB2BGR))  # Обратная конвертация

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
        75,
        255,
        cv2.THRESH_BINARY
    )[1]

    # Определение контуров элементов и их отрисовка на цветном изображении
    contours_flasks, _ = cv2.findContours(
        thresholder,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    return contours_flasks


def found_rect(cnt, my_list, coeff_width, coeff_height):
    '''Функция распознавания прямоугольника'''
    rect = cv2.minAreaRect(cnt)
    if (rect[1][0] >= rect[1][1] and rect[1][1] >= coeff_width and rect[1][0] >= coeff_height) or \
        (rect[1][0] < rect[1][1] and rect[1][0] >= coeff_width and rect[1][1] >= coeff_height):
        # Добавляем прямоугольники с колбами в список
        my_list.append(rect)
    return my_list


def crop_rects(my_list, image, cropped_image):
    '''Функция для увеличения каждой отдельной колбы для распознавания цветов внутри нее'''
    flasks_info = []
    for cnt in my_list:
        filename = f'flask_{cnt}.jpg'
        # Взаимодействие с колбой
        height_flask = [round(cnt[0][1] - cnt[1][0] / 2), round(cnt[0][1] + cnt[1][0] / 2)]
        width_flask = [round(cnt[0][0] - cnt[1][1] / 2), round(cnt[0][0] + cnt[1][1] / 2)]
        flask = cropped_image[height_flask[0]:height_flask[1], width_flask[0]:width_flask[1]]
        cv2.imwrite(filename, flask)
        flasks_info.append((filename, (width_flask[1] - width_flask[0], height_flask[1] - height_flask[0])))
    return flasks_info


def found_colors_in_flasks(image_for_search, id):
    '''Основная функция для распознавания цветов на картинке и добавления их в массив'''
    # TODO: Надо улучшить распознавание, чтобы с учетом погрешностей точно были видны все прямоугольники
    # Чтение изображения в цветном формате
    original_image = cv2.imread(image_for_search)
    # Получение параметров размера изображения и вывод параметров обрезки
    height, width, _ = original_image.shape
    cropped_height = [round(height * 0.125), round(height * 0.875)]
    # Обрзка изображения под определенные границы (чтобы были видны только колбы)
    cropped_image = original_image[cropped_height[0]:cropped_height[1], 0:width]
    cv2.imwrite(image_for_search, cropped_image)

    contours_flasks = preprocessing_image(image_for_search)

    coeff_width_flask = round(width / 11)    # Эмпирически полученный коэффициент отношения ширины экрана к ширине колбы
    coeff_height_flask = round((cropped_height[1] - cropped_height[0]) / 4.9)    # Эмпирически полученный коэффициент отношения высоты экрана к ширине колбы
    flasks = [] # Список прямоугольников-колб
    # Проходим по всем контурам и подсвечиваем прямоугольники целых колб
    for cnt_contours in contours_flasks:
        '''Определение границ прямоугольников и добавление цвета прямоугольника в список'''
        flasks = found_rect(cnt_contours, flasks, coeff_width_flask, coeff_height_flask)
    flasks_images = crop_rects(flasks, image_for_search, cropped_image)

    colors_into_flask = []
    for cnt_images in flasks_images:
        only_flasks = preprocessing_image(cnt_images[0])
        # Определение цветов внутри колбы
        coeff_width_color = round(cnt_images[1][0] / 1.35)  # Эмпирически полученный коэффициент для отношения ширины колбы к ширине цвета
        coeff_height_color = round(cnt_images[1][1] / 4.9)  # Эмпирически полученный коэффициент для отношения высоты колбы к ширине цвета
        for cnt_contours_flask in only_flasks:
            colors_into_flask = found_rect(cnt_contours_flask, colors_into_flask, coeff_width_color, coeff_height_color)
        for cnt_box in colors_into_flask:
            box = np.int0(cv2.boxPoints(cnt_box))
            draw_contours(cnt_images[0], box, (0, 255, 0))
 
    # flasks_list = create_list()
    # return create_json(flasks_list, id)
            

# def create_list():
#     '''Создание списка со списками цветов в колбах'''

#     return flasks_list


def create_json(flasks_list, id_client):
    '''Создание и заполнение json файла с распознанными цветами'''
    with open(f"./levels/this_level_{id_client}.json", "w") as this_level:
        json.dump(flasks_list, this_level)
    return this_level
