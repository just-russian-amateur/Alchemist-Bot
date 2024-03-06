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


def found_colors_in_flasks(image_for_search, id):
    '''Распознавание цветов на картинке и добавления их в массив'''
    # TODO: Надо улучшить распознавание, чтобы с учетом погрешностей точно были видны все прямоугольники
    # Чтение изображения в цветном формате
    original_image = cv2.imread(image_for_search)
    # Получение параметров размера изображения и вывод параметров обрезки
    height, weight, _ = original_image.shape
    cropped_height_first = round(height * 0.125)
    cropped_height_last = round(height * 0.875)
    # Обрзка изображения под определенные границы (чтобы были видны только колбы)
    cropped_image = original_image[cropped_height_first:cropped_height_last, 0:weight]
    cv2.imwrite(image_for_search, cropped_image)

    sharp_filter = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharped_image = cv2.filter2D(cropped_image, ddepth=-1, kernel=sharp_filter)
    cv2.imwrite(image_for_search, sharped_image)
    # Чтение обрезанного изображения в ч/б формате
    gray_noise = cv2.imread(image_for_search, 0)

    # Размытие фона для ч/б изображения
    blurred = cv2.GaussianBlur(
        gray_noise,
        (5, 5),
        0
    )

    # Пороговая обработка изображения
    # thresholder = cv2.threshold(
    #     gray_noise,
    #     66,
    #     255,
    #     cv2.THRESH_BINARY
    # )[1]

    thresholder = cv2.threshold(
        gray_noise,
        100,
        255,
        cv2.THRESH_BINARY
    )[1]

    # Определение контуров элементов и их отрисовка на цветном изображении
    contours_flasks, _ = cv2.findContours(
        thresholder,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # Проходим по всем контурам и подсвечиваем различные прямоугольники
    for cnt_contours in contours_flasks:
        '''Определение границ прямоугольников и добавление цвета прямоугольника в список'''
        rect = cv2.minAreaRect(cnt_contours)
        box = np.int0(cv2.boxPoints(rect))
        if (rect[1][0] >= rect[1][1] and rect[1][1] >= 51.0) or \
            (rect[1][0] < rect[1][1] and rect[1][0] >= 51.0):
            draw_contours(image_for_search, box, (0, 255, 0))
        elif 33.0 <= rect[2] <= 57.0 and 16 <= round(rect[1][0]) <= 22 and \
            16 <= round(rect[1][1]) <= 22:
            draw_contours(image_for_search, box, (255, 255, 255))
        else:
            draw_contours(image_for_search, box, (255, 255, 255))
    
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
