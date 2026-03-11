import time
import Cam
import crop
import OpenCV
import tkinter as tk
from itertools import cycle

COUNT = 0

# Создаем список текстов для циклического переключения
texts = []

# def change_text():
#     """Функция для автоматического изменения текста в label."""
#     # Получаем следующий текст из цикла
#     next_text = next(text_cycle)
#     # Меняем текст в label
#     label.config(text=next_text)
#     # Планируем следующий вызов этой же функции через 1000 мс (1 секунда)
#     root.after(1000, change_text)


if __name__ == "__main__":
    
    Cam.main()
    time.sleep(3)
    crop.crop_to_square_center("daheng_snapshot.jpg", "crop_daheng_snapshot.jpg")
    crop.resize_to_exact("crop_daheng_snapshot.jpg", "crop_daheng_snapshot.jpg", 1000, 1000)
    texts.append(COUNT)
    text_cycle = cycle(texts)  # Бесконечный цикл по списку
    #COUNT = OpenCV.recieve_value()
    #print(COUNT)

    # # Создаем главное окно
    # root = tk.Tk()
    # root.title("Пример с Label")
    # root.geometry("400x300")  # Ширина x Высота

    # # Создаем Label с крупным шрифтом
    # # font=("Arial", 24) - можно изменить шрифт и размер по желанию
    # label = tk.Label(
    #     root,
    #     text="Привет, мир!",
    #     font=("Arial", 24),  # Крупный шрифт
    #     fg="black",          # Цвет текста
    #     bg="lightgray"       # Цвет фона
    # )

    # # Размещаем label в окне (растягиваем с отступами)
    # label.pack(pady=50, padx=20, expand=True)

    # # Запускаем первое обновление текста через 1 секунду после старта
    # # (можно сразу, тогда укажите 0)
    # root.after(1000, change_text)

    # # Запускаем главный цикл окна
    # root.mainloop()
   