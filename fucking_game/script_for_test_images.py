import cv2
import numpy as np


variations = [
    ('BLUE', (np.array((30, 50, 192), np.uint8), np.array((108, 255, 255), np.uint8))),
    ('ORANGE', (np.array((0, 165, 203), np.uint8), np.array((19, 255, 255), np.uint8))),
    ('YELLOW', (np.array((22, 46, 192), np.uint8), np.array((34, 255, 255), np.uint8))),
    ('RED', (np.array((0, 148, 114), np.uint8), np.array((7, 255, 255), np.uint8))),
    ('GREEN', (np.array((41, 0, 160), np.uint8), np.array((65, 255, 255), np.uint8))),
    ('DARKBLUE', (np.array((48, 195, 169), np.uint8), np.array((195, 255, 255), np.uint8))),
    ('DARKRED', (np.array((164, 135, 84), np.uint8), np.array((255, 255, 110), np.uint8))),
    ('DARKGREEN', (np.array((61, 108, 80), np.uint8), np.array((96, 255, 255), np.uint8))),
    ('PINK', (np.array((137, 0, 197), np.uint8), np.array((152, 255, 255), np.uint8))),
    ('DARKPINK', (np.array((140, 85, 183), np.uint8), np.array((195, 255, 255), np.uint8))),
    ('LIGHTPINK', (np.array((10, 0, 228), np.uint8), np.array((20, 255, 255), np.uint8))),
    ('PURPLE', (np.array((131, 157, 103), np.uint8), np.array((255, 255, 255), np.uint8))),
    ('GRAY', (np.array((0, 0, 94), np.uint8), np.array((255, 29, 116), np.uint8))),
    ('LILAC', (np.array((117, 155, 136), np.uint8), np.array((125, 255, 255), np.uint8))),
    ('UNDEFINED', (np.array((0, 0, 26), np.uint8), np.array((0, 0, 26), np.uint8)))
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
    # '''Функция предобработки изображения'''
    # # Чтение обрезанного изображения в ч/б формате
    # gray_noise = cv2.imread(image, 0)
    # print(gray_noise.shape)
    # # Размытие фона для ч/б изображения
    # blurred = cv2.GaussianBlur(
    #     gray_noise,
    #     (5, 5),
    #     0
    # )

    # # Пороговая обработка изображения
    # # TODO: подбор коэффициента для корректного распознавания пустых колб
    # thresholder = cv2.threshold(
    #     blurred,
    #     68,
    #     255,
    #     cv2.THRESH_BINARY
    # )[1]

    # return thresholder

    pass


def main():
    for j in range(1, 15):
        with open(f'/home/laptev/Документы/Projects/flasks/fucking_game/test_flasks/{j}.jpg', 'r') as test_img:
        # with open(f'/home/laptev/Документы/Projects/flasks/fucking_game/test_pictures/{i}.jpg', 'r') as test_img:
            # Чтение изображения в цветном формате
            original_image = cv2.imread(test_img.name)
            # Получение параметров размера изображения и вывод параметров обрезки
            height, width, _ = original_image.shape
            print(original_image.shape)
            # cropped_height = [round(height * 0.125), round(height * 0.875)]
            # # Обрзка изображения под определенные границы (чтобы были видны только колбы)
            # cropped_image = original_image[cropped_height[0]:cropped_height[1], 0:width]
            # cv2.imwrite(f'/home/laptev/Документы/Projects/flasks/fucking_game/out_test_flasks/{i}.jpg', cropped_image)
            # cv2.imwrite(f'/home/laptev/Документы/Projects/flasks/fucking_game/out_test/{i}.jpg', cropped_image)

            # Предобработка начального изображения после кропа
            # Определение контуров элементов и их отрисовка на цветном изображении
            # contours_of_flasks, _ = cv2.findContours(
            #     preprocessing_image(f'/home/laptev/Документы/Projects/flasks/fucking_game/out_test_flasks/{i}.jpg'),
            #     # preprocessing_image(f'/home/laptev/Документы/Projects/flasks/fucking_game/out_test/{i}.jpg'),
            #     cv2.RETR_TREE,
            #     cv2.CHAIN_APPROX_SIMPLE
            # )

            # coeff_width = round(width / 11)
            # coeff_height = round(height / 5.2)


            # Более агрессивный подход для удаления ненужных шумов с изображения с использованием эрозии
            color_pixels = cv2.imread(f'/home/laptev/Документы/Projects/flasks/fucking_game/test_flasks/{j}.jpg')
            hsv_colors = cv2.cvtColor(color_pixels, cv2.COLOR_BGR2HSV)

            colors_info = []
            # TODO: подбор коэффициентов, чтобы исключить ненужные прямоугольники
            # coeff_width = round(width / 1.5)
            coeff_height = round(height / 6.5)
            for i in range(len(variations)):
                thresholder = cv2.inRange(hsv_colors, variations[i][1][0], variations[i][1][1])
                contours_color, _ = cv2.findContours(
                    thresholder,
                    cv2.RETR_TREE,
                    cv2.CHAIN_APPROX_SIMPLE
                )
                if len(contours_color) != 0:
                    # color = []
                    color_name = variations[i][0]
                    for cnt in contours_color:
                        rect = cv2.minAreaRect(cnt)
                        box = np.int0(cv2.boxPoints(rect))
                        # if i == 11:
                        # print(rect)
                        if rect[1][0] >= coeff_height and rect[1][1] >= coeff_height:
                            print(rect)
                            draw_contours(f'/home/laptev/Документы/Projects/flasks/fucking_game/out_test_flasks/{j}.jpg', box, (255, 255, 255))
                            # draw_contours(f'/home/laptev/Документы/Projects/flasks/fucking_game/out_test/{i}.jpg', box, (255, 255, 255))

                    # for cnt in color_coords:
                    #     # Определение контуров элементов и их отрисовка на цветном изображении
                            # for k in range(len(colors_info)):
                            #     if len(colors_info) > 0:
                            #         if colors_info[k][0][0] - colors_info[k-1][0][0] >= 15:
                            #             colors_info.append((color_name, cnt[0]))
                            #     else:
                            #         colors_info.append((color_name, cnt[0]))


            # return colors_info


            # for contour in contours_of_flasks:
            #     rect = cv2.minAreaRect(contour)
            #     box = np.int0(cv2.boxPoints(rect))
            #     # if i == 11:
            #     #     print(rect)
            #     if (rect[1][0] >= rect[1][1] and rect[1][1] >= coeff_width and rect[1][0] >= coeff_height) or \
            #         (rect[1][0] < rect[1][1] and rect[1][0] >= coeff_width and rect[1][1] >= coeff_height):
            #         draw_contours(f'/home/laptev/Документы/Projects/flasks/fucking_game/out_test_flasks/{i}.jpg', box, (255, 255, 255))
            #         # draw_contours(f'/home/laptev/Документы/Projects/flasks/fucking_game/out_test/{i}.jpg', box, (255, 255, 255))



    

if __name__ == '__main__':
    main()