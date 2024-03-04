'''Этот модуль отвечает за поиск и распознавание цветов в каждой колбе'''
import cv2

def found_colors_in_flasks(image_for_search):
    # Чтение изображения в цветном и черно-белом форматах
    original_image = cv2.imread(image_for_search)
    size = original_image.shape
    height = size[0]
    weight = size[1]
    cropped_image = original_image[height*0.125:height*0.875, 0:weight]
    gray_noise = cv2.imread(cropped_image, 0)

    # Размытие фона для ч/б изображения
    blurred = cv2.GaussianBlur(gray_noise, (5, 5), 0)

    # Пороговая обработка изображения
    thresholder = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY)[1]

    # Определение контуров элементов и их отрисовка на цветном изображении
    contours_flasks, _ = cv2.findContours(thresholder, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.imwrite(image_for_search, cv2.drawContours(original_image, contours_flasks, -1, (0, 255, 0), 2))
