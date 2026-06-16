import cv2
import numpy as np

def get_screw_area(erosion_size, image_path):
    """
    Определение площади одного винта на изображении
    
    Параметры:
    - erosion_size: размер ядра эрозии (по умолчанию 3)
    - image_path: путь к изображению с винтом (по умолчанию 'daheng_snapshot_circle.png')
    
    Возвращает:
    - area: площадь винта в пикселях (int)
    """
    
    # -------------------------
    # НАСТРОЙКИ
    # -------------------------
    # Порог белого фона в HSV
    S_MAX_BG = 80     # чем меньше, тем "белее" (50-80)
    V_MIN_BG = 210    # чем больше, тем ярче (170-210)
    
    # Морфология маски деталей
    OPEN_K = 5        # убрать мелкий мусор
    OPEN_IT = 1
    CLOSE_K = 1       # подлечить дырки/резьбу
    CLOSE_IT = 1
    
    # Фильтр по площади
    MIN_AREA = 700    # минимальная площадь объекта
    MAX_AREA = 300000 # максимальная площадь объекта
    
    # -------------------------
    # 1) Загрузка изображения
    # -------------------------
    img = cv2.imread(image_path)
    if img is None:
        raise RuntimeError(f"Не удалось открыть {image_path}")
    
    # -------------------------
    # 2) Преобразование в HSV и выделение винта
    # -------------------------
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    H, S, V = cv2.split(hsv)
    
    # Создаём маску фона (белый фон)
    bg_mask = ((S <= S_MAX_BG) & (V >= V_MIN_BG)).astype(np.uint8) * 255
    
    # Инвертируем маску, получаем маску винта
    screw_mask = cv2.bitwise_not(bg_mask)
    
    # Морфологическая обработка для очистки
    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (OPEN_K, OPEN_K))
    k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (CLOSE_K, CLOSE_K))
    
    screw_mask = cv2.morphologyEx(screw_mask, cv2.MORPH_OPEN, k_open, iterations=OPEN_IT)
    screw_mask = cv2.morphologyEx(screw_mask, cv2.MORPH_CLOSE, k_close, iterations=CLOSE_IT)
    
    # -------------------------
    # 3) Эрозия для разделения (если нужно)
    # -------------------------
    erosion_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erosion_size, erosion_size))
    screw_mask_eroded = cv2.erode(screw_mask, erosion_kernel, iterations=1)
    
    # -------------------------
    # 4) Поиск связных компонент
    # -------------------------
    num, labels, stats, centroids = cv2.connectedComponentsWithStats(screw_mask_eroded, connectivity=8)
    
    # -------------------------
    # 5) Анализ объекта и поиск площади
    # -------------------------
    screw_areas = []
    
    # Проходим по всем компонентам (пропускаем фон - индекс 0)
    for i in range(1, num):
        area = stats[i, cv2.CC_STAT_AREA]
        
        # Фильтрация по площади
        if area < MIN_AREA or area > MAX_AREA:
            continue
        
        screw_areas.append(area)
    
    # -------------------------
    # 6) Возвращаем результат
    # -------------------------
    if len(screw_areas) == 0:
        print(f"⚠️ Винт не найден при erosion_size={erosion_size}")
        return 0
    elif len(screw_areas) == 1:
        return screw_areas[0]
    else:
        # Если найдено несколько объектов, возвращаем самый большой
        return max(screw_areas)


# -------------------------
# ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:
# -------------------------
area3 = get_screw_area(erosion_size=15, image_path ='daheng_snapshot_circle.png')
print(area3)