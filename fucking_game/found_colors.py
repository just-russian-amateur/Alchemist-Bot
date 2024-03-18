'''Этот модуль отвечает за поиск и распознавание цветов в каждой колбе'''
import cv2
import numpy as np
import json
from skimage import io


# variations = [
#     ('BLUE', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('ORANGE', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('YELLOW', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('RED', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('GREEN', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('DARKBLUE', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('DARKRED', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('DARKGREEN', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('PINK', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('DARKPINK', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('LIGHTPINK', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('PURPLE', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('GRAY', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('LILAC', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('EMPTY', (np.array((), np.uint0), np.array((), np.uint0))),
#     ('UNDEFINED' (np.array((), np.uint0), np.array((), np.uint0)))
# ]


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


def preprocessing_image(image, is_flask):
    '''Функция предобработки изображения'''
    if is_flask == True:
        # Более агрессивный подход для удаления ненужных шумов с изображения с использованием эрозии
        morph_kernel = np.ones((3, 3))
        erode_image = cv2.erode(cv2.imread(image), kernel=morph_kernel, iterations=4)
        cv2.imwrite(image, erode_image)

    # image_for_sharp = cv2.imread(image)
    # sharp_filter = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    # sharped_image = cv2.filter2D(image_for_sharp, ddepth=-1, kernel=sharp_filter)
    # cv2.imwrite(image, sharped_image)

    # CLAHE (Contrast Limited Adaptive Histogram Equalization) - Повышение контрастности
    # clahe = cv2.createCLAHE(clipLimit=1, tileGridSize=(8,8))
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
        72,
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


def found_rect(filename, contour, my_list, coeff_width, coeff_height):
    '''Функция распознавания прямоугольника'''
    rect = cv2.minAreaRect(contour)
    box = np.int0(cv2.boxPoints(rect))
    # draw_contours(filename, box, (0, 255, 0))
    if (rect[1][0] >= rect[1][1] and rect[1][1] >= coeff_width and rect[1][0] >= coeff_height) or \
        (rect[1][0] < rect[1][1] and rect[1][0] >= coeff_width and rect[1][1] >= coeff_height):
        # Добавляем прямоугольники с колбами в список
        my_list.append(rect)

    return my_list, box


def crop_rects(contours, cropped_image):
    '''Функция для выделения каждой отдельной колбы или цвета в ней для распознавания цветов'''
    flasks_info = []
    for cnt in contours:
        filename = f'flask_{cnt}.jpg'
        # Взаимодействие с колбой
        height_flask = [round(cnt[0][1] - cnt[1][0] / 2), round(cnt[0][1] + cnt[1][0] / 2)]
        width_flask = [round(cnt[0][0] - cnt[1][1] / 2), round(cnt[0][0] + cnt[1][1] / 2)]
        flask = cropped_image[height_flask[0]:height_flask[1], width_flask[0]:width_flask[1]]
        cv2.imwrite(filename, flask)
        flasks_info.append((filename, (width_flask[1] - width_flask[0], height_flask[1] - height_flask[0])))

    return flasks_info


def stack_colors(image):
    '''Определение цвета внутри контура и добавление цвета в стек'''
    # color_pixels = io.imread(image)
    # pixels = np.float32(color_pixels.reshape(-1, 3))

    # n_colors = 5
    # criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    # flags = cv2.KMEANS_RANDOM_CENTERS

    # _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    # _, counts = np.unique(labels, return_counts=True)

    # dominant = palette[np.argmax(counts)]

    # return dominant
    color_pixels = cv2.imread(image)
    hsv_colors = cv2.cvtColor(color_pixels, cv2.COLOR_BGR2HSV)
    mean_color = hsv_colors.mean(axis=0).mean(axis=0)

    return mean_color


# def create_color_list(image):
#     '''Функция для создания списка колб с цветами вместо числовых значений'''
#     color_pixels = cv2.imread(image)
#     hsv_colors = cv2.cvtColor(color_pixels, cv2.COLOR_BGR2HSV)

#     for i in range(len(variations)):
#         thresholder = cv2.inRange(hsv_colors, variations[i][1][0], variations[i][1][1])
#         if thresholder == 255:
#             color_name = variations[i][0]
#             break

#     return color_name


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
    # Предобработка начального изображения после кропа
    contours_of_flasks = preprocessing_image(image_for_search, is_flask=False)

    # Задаем эмпирически полученные коэффициенты отношения высоты и ширины экрана к высоте и ширине колбы (возможно получится подстраиваться)
    coeff_width_flask = round(width / 11)
    coeff_height_flask = round((cropped_height[1] - cropped_height[0]) / 5.2)
    flasks = [] # Список прямоугольников-колб
    # Проходим по всем контурам и подсвечиваем прямоугольники целых колб
    for contour in contours_of_flasks:
        # Определение границ прямоугольников и добавление цвета прямоугольника в список
        flasks, _ = found_rect(image_for_search, contour, flasks, coeff_width_flask, coeff_height_flask)
    flasks = sorted(flasks)
    images_of_flasks = crop_rects(flasks, cropped_image)

    flasks_list = []
    for images_contour in images_of_flasks:
        # Повторная предобработка изображений содержащих только колбы
        original_flask = preprocessing_image(images_contour[0], is_flask=True)
        # Определение цветов внутри колбы
        # Задаем эмпирически полученные коэффициенты отношения высоты и ширины колбы к высоте и ширине цвета в колбе (возможно получится подстраиваться)
        coeff_width_color = 1
        coeff_height_color = 1
        # coeff_width_color = round(cnt_images[1][0] / 1.35)  # Эмпирически полученный коэффициент для отношения ширины колбы к ширине цвета
        # coeff_height_color = round(cnt_images[1][1] / 4.9)  # Эмпирически полученный коэффициент для отношения высоты колбы к ширине цвета
        
        # Находим контуры цветов внутри каждой колбы
        internal_contours = [] # Список со стеком цветовых контуров внутри колб
        for internal_flask in original_flask:
            internal_contours, _ = found_rect(images_contour[0], internal_flask, internal_contours, coeff_width_color, coeff_height_color)
        internal_contours = sorted(internal_contours, reverse=True)
        
        # Непосредственно определяем цвет и добавляем его в список для конкретной колбы
        internal_colors = []
        single_colors = crop_rects(internal_contours, cv2.imread(images_contour[0]))
        for color_contour in single_colors:
            internal_colors = stack_colors(color_contour[0])
            # internal_colors.append(create_color_list(color_contour[0]))
        flasks_list.append(internal_colors)

    # color_list = create_color_list(flasks_list)

    return create_json(flasks_list, id)


def create_json(flasks_list, id_client):
    '''Создание и заполнение json файла с распознанными цветами'''
    with open(f"./levels/this_level_{id_client}.json", "w") as this_level:
        json.dump({"bottles": flasks_list}, this_level)

    return this_level
