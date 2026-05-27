from PIL import Image, ImageDraw
import os


def take_photo():
# Получаем путь к текущей папке
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Путь к исходному файлу
    input_path = os.path.join(current_dir, "daheng_snapshot.jpg")
    output_path = os.path.join(current_dir, "daheng_snapshot_circle.png")

    # Открываем изображение
    img = Image.open(input_path).convert('RGBA')

    # Параметры круга
    diameter = 3000
    width, height = img.size
    center_x, center_y = width // 2, height // 2

    # Обрезаем квадрат
    half = diameter // 2
    cropped = img.crop((
        max(0, center_x - half),
        max(0, center_y - half),
        min(width, center_x + half),
        min(height, center_y + half)
    ))

    # Создаем маску круга
    mask = Image.new('L', (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter, diameter), fill=255)

    # Применяем маску
    result = Image.new('RGBA', (diameter, diameter), (0, 0, 0, 0))
    result.paste(cropped, (0, 0), mask)

    # Сохраняем результат
    result.save(output_path, 'PNG')
    print(f"Готово! Файл сохранен: {output_path}")
    return True

