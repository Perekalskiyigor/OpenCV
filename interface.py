import tkinter as tk
from PIL import Image, ImageTk
import main
import os
import time

res = (0)
itogo = "..."

def load_and_display_image():
    """Функция для загрузки и отображения изображения"""
    try:
        if os.path.exists("dbg_final_result.png"):
            image = Image.open("dbg_final_result.png")
            # Автоматическая подстройка размера под окно
            image.thumbnail((1000, 700), Image.Resampling.LANCZOS)
            new_photo = ImageTk.PhotoImage(image)
            label_image.config(image=new_photo)
            label_image.image = new_photo
            return True
        else:
            label_image.config(text="Файл изображения не найден", image="")
            return False
    except Exception as e:
        print(f"Ошибка загрузки изображения: {e}")
        label_image.config(text=f"Ошибка: {e}", image="")
        return False

def process_loop():
    global res
    if res[1] > 0:
        res = main.start()
        load_and_display_image()
        root.after(500, process_loop)  # Через 1 секунду вызвать снова
        itogo = "..."
        label_output.config(text=str(itogo))
    else:
        itogo = res[0]
        label_output.config(text=str(itogo))

def pusk_f():
    global res
    global itogo
    res = main.start()
    load_and_display_image()
    process_loop()

        

# Создаём главное окно
root = tk.Tk()
root.title("Подсчет номенклатурных единиц")
root.geometry("950x950")

# Метка для изображения (изначально пустая или с текстом)
label_image = tk.Label(root, text="Нажмите 'Пуск' для загрузки изображения", 
                       font=("Arial", 14), fg="blue", bg="lightgray")
label_image.pack(pady=10, fill=tk.BOTH, expand=True)

# Метка для вывода числа
label_output = tk.Label(root, text=str(itogo), font=("Arial", 48), 
                        width=10, height=2, relief="sunken")
label_output.pack(pady=20)

# Кнопка пуск
button_start = tk.Button(root, text="Пуск", command=pusk_f, 
                        font=("Arial", 14), width=10, bg="green", fg="white")
button_start.pack(pady=10)


# Запуск основного цикла
root.mainloop()