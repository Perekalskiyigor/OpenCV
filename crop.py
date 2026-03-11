from PIL import Image

def crop_to_square_center(image_path, output_path, size=2600):
    """
    Обрезает изображение до квадрата от центра
    
    Args:
        image_path: путь к исходному изображению
        output_path: путь для сохранения результата
        size: размер итогового квадрата (по умолчанию 2000)
    """
    # Открываем изображение
    img = Image.open(image_path)
    
    # Получаем размеры исходного изображения
    width, height = img.size
    
    # Находим центр
    center_x = width // 2
    center_y = height // 2
    
    # Вычисляем координаты для обрезки (квадрат от центра)
    left = center_x - (size // 2)
    top = center_y - (size // 2)
    right = left + size
    bottom = top + size
    
    # Проверяем, что координаты в пределах изображения
    if left < 0:
        left = 0
        right = size
    if top < 0:
        top = 0
        bottom = size
    if right > width:
        right = width
        left = width - size
    if bottom > height:
        bottom = height
        top = height - size
    
    # Обрезаем изображение
    cropped_img = img.crop((left, top, right, bottom))
    
    # Сохраняем результат
    cropped_img.save(output_path)
    print(f"Изображение сохранено: {output_path}")
    print(f"Исходный размер: {width}x{height}")
    print(f"Новый размер: {cropped_img.size[0]}x{cropped_img.size[1]}")
    return True

def resize_to_exact(image_path, output_path, width, height):
    """
    Изменяет размер изображения до точных размеров
    
    Args:
        image_path: путь к исходному изображению
        output_path: путь для сохранения результата
        width: новая ширина
        height: новая высота
    """
    # Открываем изображение
    img = Image.open(image_path)
    
    # Изменяем размер
    resized_img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    # Сохраняем результат
    resized_img.save(output_path, quality=95)
    print(f"Изменено: {img.size} -> {resized_img.size}")
    print(f"Сохранено в: {output_path}")
    return True


# Использование
# crop_to_square_center("daheng_snapshot.jpg", "crop_daheng_snapshot.jpg")
# resize_to_exact("crop_daheng_snapshot.jpg", "resize_daheng_snapshot.jpg", 1000, 1000)