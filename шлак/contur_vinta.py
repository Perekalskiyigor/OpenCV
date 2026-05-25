import cv2
import numpy as np
import matplotlib.pyplot as plt

def find_screw_contour(image_path):
    """
    Функция для обнаружения контура винта на изображении
    
    Args:
        image_path: путь к изображению
    
    Returns:
        image_with_contour: изображение с выделенным контуром винта
        screw_contour: контур винта
    """
    
    # 1. Загрузка изображения
    img = cv2.imread(image_path)
    if img is None:
        print(f"Ошибка: не удалось загрузить изображение по пути {image_path}")
        return None, None
    
    original_img = img.copy()
    
    # 2. Преобразование в оттенки серого
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 3. Применение размытия для уменьшения шума
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # 4. Адаптивная пороговая обработка для лучшего выделения
    # Используем несколько методов для повышения надежности
    
    # Метод 1: Адаптивный порог
    adaptive_thresh = cv2.adaptiveThreshold(blurred, 255, 
                                           cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                           cv2.THRESH_BINARY_INV, 11, 2)
    
    # Метод 2: Порог Оцу
    _, otsu_thresh = cv2.threshold(blurred, 0, 255, 
                                   cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Комбинируем методы
    combined = cv2.bitwise_or(adaptive_thresh, otsu_thresh)
    
    # 5. Морфологические операции для очистки
    kernel = np.ones((3, 3), np.uint8)
    cleaned = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)
    
    # 6. Поиск контуров
    contours, hierarchy = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, 
                                           cv2.CHAIN_APPROX_SIMPLE)
    
    # 7. Фильтрация контуров для поиска винта
    # Винт обычно имеет определенные характеристики: площадь, периметр, форму
    screw_contour = None
    max_area = 0
    
    for contour in contours:
        area = cv2.contourArea(contour)
        
        # Фильтруем слишком маленькие контуры (шум)
        if area < 500:  # Минимальная площадь, можно настроить
            continue
        
        # Аппроксимируем контур
        epsilon = 0.02 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        
        # Винт часто имеет неправильную форму, но должен быть достаточно большим
        # Ищем контур с максимальной площадью (предполагая, что винт - главный объект)
        if area > max_area:
            max_area = area
            screw_contour = contour
    
    # 8. Визуализация результатов
    result_img = original_img.copy()
    
    if screw_contour is not None:
        # Рисуем основной контур винта
        cv2.drawContours(result_img, [screw_contour], -1, (0, 255, 0), 2)
        
        # Рисуем выпуклую оболочку винта
        hull = cv2.convexHull(screw_contour)
        cv2.drawContours(result_img, [hull], -1, (255, 0, 0), 1)
        
        # Находим центр масс контура
        M = cv2.moments(screw_contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(result_img, (cX, cY), 5, (0, 0, 255), -1)
            
            # Добавляем информацию на изображение
            area = cv2.contourArea(screw_contour)
            perimeter = cv2.arcLength(screw_contour, True)
            cv2.putText(result_img, f"Area: {int(area)}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.putText(result_img, f"Perimeter: {int(perimeter)}", (10, 60), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        print(f"Контур винта найден! Площадь: {area:.1f}, Периметр: {perimeter:.1f}")
    else:
        print("Контур винта не найден")
        # Показываем все найденные контуры для отладки
        cv2.drawContours(result_img, contours, -1, (0, 255, 0), 1)
    
    return result_img, screw_contour

def show_results(image_path):
    """
    Отображение результатов обработки
    """
    # Находим контур винта
    result_img, screw_contour = find_screw_contour(image_path)
    
    if result_img is None:
        return
    
    # Загружаем оригинальное изображение
    original = cv2.imread(image_path)
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    result_rgb = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
    
    # Создаем фигуру для отображения
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Отображаем оригинальное изображение
    axes[0].imshow(original_rgb)
    axes[0].set_title('Оригинальное изображение')
    axes[0].axis('off')
    
    # Отображаем результат с контуром
    axes[1].imshow(result_rgb)
    axes[1].set_title('Обнаруженный контур винта')
    axes[1].axis('off')
    
    # Если контур найден, отображаем увеличенную область
    if screw_contour is not None:
        x, y, w, h = cv2.boundingRect(screw_contour)
        cropped = result_rgb[y:y+h, x:x+w]
        axes[2].imshow(cropped)
        axes[2].set_title('Увеличенный контур винта')
        axes[2].axis('off')
    
    plt.tight_layout()
    plt.show()

def save_result(image_path, output_path):
    """
    Сохранение результата в файл
    """
    result_img, _ = find_screw_contour(image_path)
    if result_img is not None:
        cv2.imwrite(output_path, result_img)
        print(f"Результат сохранен в {output_path}")

# Пример использования
if __name__ == "__main__":
    # Укажите путь к вашему изображению
    image_path = "C:/Users/m.dubrovin/Documents/GitHub/OpenCV/resize_daheng_snapshot.jpg"  # Замените на путь к вашему изображению
    
    # Отображение результатов
    show_results(image_path)
    
    # Сохранение результата (опционально)
    # save_result(image_path, "output_screw_contour.jpg")
    
    