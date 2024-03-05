'''Этот модуль отвечает за поиск и распознавание цветов в каждой колбе'''
import cv2
import numpy as np

def found_colors_in_flasks(image_for_search):
    # Чтение изображения в цветном формате
    original_image = cv2.imread(image_for_search)
    # Получение параметров размера изображения и вывод параметров обрезки
    height, weight, _ = original_image.shape
    cropped_height_first = round(height * 0.125)
    cropped_height_last = round(height * 0.875)
    # Обрзка изображения под определенные границы (чтобы были видны только колбы)
    cropped_image = original_image[cropped_height_first:cropped_height_last, 0:weight]
    cv2.imwrite(image_for_search, cropped_image)
    # Чтение обрезанного изображения в ч/б формате
    gray_noise = cv2.imread(image_for_search, 0)

    # Размытие фона для ч/б изображения
    blurred = cv2.GaussianBlur(
        gray_noise,
        (5, 5),
        0
    )

    # Пороговая обработка изображения
    thresholder = cv2.threshold(
        blurred,
        66,
        255,
        cv2.THRESH_BINARY
    )[1]

    # Определение контуров элементов и их отрисовка на цветном изображении
    contours_flasks, _ = cv2.findContours(
        thresholder,
        cv2.RETR_TREE,
        cv2.CHAIN_APPROX_SIMPLE
    )

    # cv2.imwrite(
    #     image_for_search,
    #     cv2.drawContours(
    #         cv2.imread(image_for_search),
    #         contours_flasks,
    #         -1,
    #         (0, 255, 0),
    #         2
    #     )
    # )
    max_weight = 0
    for cnt_contours in contours_flasks:
        rect = cv2.minAreaRect(cnt_contours)
        box = np.int0(cv2.boxPoints(rect))
        print(rect)
        # if box.shape[1] > max_weight:
        #     max_weight = box.shape[1]
        cv2.imwrite(
            image_for_search,
            cv2.drawContours(
                cv2.imread(image_for_search),
                [box],
                0,
                (255, 255, 255),
                2
            )
        )
    # print(max_weight)
