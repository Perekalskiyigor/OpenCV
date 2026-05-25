import tkinter as tk
from PIL import Image, ImageTk
import main
import os

res = (0)

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

def pusk_f():
    global res
    res = main.main()  # выполнение основной программы (может создать/обновить изображение)
    
    if res is not None:
        label_output.config(text=str(res))
    
    # Загружаем и отображаем изображение после выполнения main
    load_and_display_image()

# Создаём главное окно
root = tk.Tk()
root.title("Подсчет номенклатурных единиц")
root.geometry("950x950")

# Метка для изображения (изначально пустая или с текстом)
label_image = tk.Label(root, text="Нажмите 'Пуск' для загрузки изображения", 
                       font=("Arial", 14), fg="blue", bg="lightgray")
label_image.pack(pady=10, fill=tk.BOTH, expand=True)

# Метка для вывода числа
label_output = tk.Label(root, text=str(res), font=("Arial", 48), 
                        width=10, height=2, relief="sunken")
label_output.pack(pady=20)

# Кнопка пуск
button_start = tk.Button(root, text="Пуск", command=pusk_f, 
                        font=("Arial", 14), width=10, bg="green", fg="white")
button_start.pack(pady=10)

# Запуск основного цикла
root.mainloop()