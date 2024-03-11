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


def preprocessing_image(image, image_for_sharp):
    '''Функция предобработки изображения'''
    # sharp_filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    # sharped_image = cv2.filter2D(cropped_image, ddepth=-1, kernel=sharp_filter)
    # cv2.imwrite(image, sharped_image)

    # CLAHE (Contrast Limited Adaptive Histogram Equalization) - Повышение контрастности
    clahe = cv2.createCLAHE(clipLimit=0.1, tileGridSize=(8,8))
    lab = cv2.imread(image)
    lab = cv2.cvtColor(lab, cv2.COLOR_BGR2LAB)  # Конвертация RGB в LAB
    l, a, b = cv2.split(lab)  # Разделение на 3 канала
    l2 = clahe.apply(l)  # Применение коэффициента к каналу яркости
    lab = cv2.merge((l2,a,b))  # Слияние каналов
    cv2.imwrite(image, cv2.cvtColor(lab, cv2.COLOR_LAB2BGR))  # Обратная конвертация

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
        gray_noise,
        75,
        255,
        cv2.THRESH_BINARY
    )[1]

    return thresholder


def found_rect(cnt, image, coeff_width_flask, cropped_image):
    '''Функция рисования прямоугольника'''
    rect = cv2.minAreaRect(cnt)
    box = np.int0(cv2.boxPoints(rect))
    if (rect[1][0] >= rect[1][1] and rect[1][1] >= coeff_width_flask) or \
        (rect[1][0] < rect[1][1] and rect[1][0] >= coeff_width_flask):
        # print(rect)
        draw_contours(image, box, (0, 255, 0))
        # Добавляем прямоугольники с колбами в список
        # flasks.append(rect)
        # Или взаимодействуем сразу, если колба найдена
        cropped_height_flask_first = round(rect[0][1] - rect[1][0] / 2)
        cropped_height_flask_last = round(rect[0][1] + rect[1][0] / 2)
        cropped_width_flask_first = round(rect[0][0] - rect[1][1] / 2)
        cropped_width_flask_last = round(rect[0][0] + rect[1][1] / 2)
        cropped_flask = cropped_image[cropped_height_flask_first:cropped_height_flask_last, cropped_width_flask_first:cropped_width_flask_last]
        cv2.imwrite(image, cropped_flask)
    # elif 33.0 <= rect[2] <= 57.0 and 16 <= round(rect[1][0]) <= 22 and \
    #     16 <= round(rect[1][1]) <= 22:
    #     draw_contours(image_for_search, box, (255, 255, 255))


def found_colors_in_flasks(image_for_search, id):
    '''Основная функция для распознавания цветов на картинке и добавления их в массив'''
    # TODO: Надо улучшить распознавание, чтобы с учетом погрешностей точно были видны все прямоугольники
    # Чтение изображения в цветном формате
    original_image = cv2.imread(image_for_search)
    # Получение параметров размера изображения и вывод параметров обрезки
    height, width, _ = original_image.shape
    cropped_height_first = round(height * 0.125)
    cropped_height_last = round(height * 0.875)
    print(height, width)
    print(cropped_height_last - cropped_height_first, width)
    # Обрзка изображения под определенные границы (чтобы были видны только колбы)
    cropped_image = original_image[cropped_height_first:cropped_height_last, 0:width]
    cv2.imwrite(image_for_search, cropped_image)

    thresholder = preprocessing_image(image_for_search, cropped_image)

    # Определение контуров элементов и их отрисовка на цветном изображении
    contours_flasks, _ = cv2.findContours(
        thresholder,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    coeff_width_flask = round(width / 11)    # Эмпирически полученный коэффициент отношения ширины экрана к ширине колбы
    # coeff_height_flask = round((cropped_height_last - cropped_height_first) / 4.75)    # Эмпирически полученный коэффициент отношения высоты экрана к высоте колбы
    # flasks = [] # Список прямоугольников-колб
    # Проходим по всем контурам и подсвечиваем прямоугольники целых колб
    for cnt_contours in contours_flasks:
        '''Определение границ прямоугольников и добавление цвета прямоугольника в список'''
        found_rect(cnt_contours, image_for_search, coeff_width_flask, cropped_image)
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
