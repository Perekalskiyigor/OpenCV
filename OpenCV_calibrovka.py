import cv2
import numpy as np

def main(erosion_size, true_count):

    IMAGE_PATH = 'resize_daheng_snapshot.jpg'

    # -------------------------
    # НАСТРОЙКИ
    # -------------------------
    # Порог белого фона в HSV:
    S_MAX_BG = 80     # чем меньше, тем "белее" (50-80)
    V_MIN_BG = 210    # чем больше, тем ярче (170-210)

    # Морфология маски деталей
    OPEN_K = 5        # убрать мелкий мусор
    OPEN_IT = 1

    CLOSE_K = 1       # подлечить дырки/резьбу
    CLOSE_IT = 1

    # Фильтр по площади (выкинуть мусорные компоненты)
    MIN_AREA = 100   # минимальная площадь объекта для учёта

    DEBUG_SAVE = True

    # принимаем путь фото
    def upload_image(PATH):
        global IMAGE_PATH
        IMAGE_PATH = PATH
        print(IMAGE_PATH)

    def save(name, img):
        if DEBUG_SAVE:
            cv2.imwrite(name, img)

    # -------------------------
    # 1) Загрузка
    # -------------------------
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        raise RuntimeError(f"Не удалось открыть {IMAGE_PATH}")

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    H, S, V = cv2.split(hsv)

    # -------------------------
    # 2) Убираем белый фон (делаем маску деталей)
    # -------------------------
    # фон: S низкий и V высокий
    bg_mask = ((S <= S_MAX_BG) & (V >= V_MIN_BG)).astype(np.uint8) * 255

    # детали = НЕ фон
    parts = cv2.bitwise_not(bg_mask)

    # Лёгкая подчистка шумов на старте
    k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (OPEN_K, OPEN_K))
    k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (CLOSE_K, CLOSE_K))

    parts = cv2.morphologyEx(parts, cv2.MORPH_OPEN, k_open, iterations=OPEN_IT)
    parts = cv2.morphologyEx(parts, cv2.MORPH_CLOSE, k_close, iterations=CLOSE_IT)

    save("dbg_parts_mask_before_erode.png", parts)

    # -------------------------
    # 3) ЭРОЗИЯ - уменьшаем объекты, чтобы разделить слипшиеся
    # -------------------------
    erosion_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erosion_size, erosion_size))
    parts_eroded = cv2.erode(parts, erosion_kernel, iterations=1)

    save("dbg_parts_mask_after_erode.png", parts_eroded)

    # -------------------------
    # 4) Находим связные компоненты (белые пятна)
    # -------------------------
    num, labels, stats, _ = cv2.connectedComponentsWithStats(parts_eroded, connectivity=8)

    # -------------------------
    # 5) Считаем ТОЛЬКО белые объекты (каждый отдельно)
    # -------------------------
    def count_white_objects():
        count = 0
        vis = img.copy()
        
        # Проходим по всем компонентам (пропускаем фон - индекс 0)
        for i in range(1, num):
            area = stats[i, cv2.CC_STAT_AREA]
            
            # Фильтруем по минимальной площади
            if area < MIN_AREA:
                continue
            
            # Получаем координаты bounding box
            x, y, w, h = (stats[i, cv2.CC_STAT_LEFT],
                         stats[i, cv2.CC_STAT_TOP],
                         stats[i, cv2.CC_STAT_WIDTH],
                         stats[i, cv2.CC_STAT_HEIGHT])
            
            # Увеличиваем счётчик
            count += 1
            
            # Рисуем прямоугольник вокруг каждого найденного объекта
            cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)  # зелёный прямоугольник
            cv2.putText(vis, str(count), (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        return vis, count

    # -------------------------
    # 6) Подсчёт и проверка
    # -------------------------
    vis, count = count_white_objects()
    
    print(f"\n\nПосчитанное количество: {count}")
    print(f"Значение эрозии: {erosion_size}")
    print(f"Ожидаемое количество: {true_count}")
    
    # Сохраняем результаты всегда
    save("dbg_final_result.png", vis)
    save("dbg_final_mask.png", parts_eroded)
    
    # Показываем изображения ТОЛЬКО если количество совпадает
    if count == true_count:
        print("✅ Количество совпадает")
        
        cv2.imshow("Original Image", img)
        cv2.imshow("White Objects Mask", parts_eroded)
        cv2.imshow("Detected Objects", vis)
        
        print("Нажмите любую клавишу для продолжения")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return True
    else:
        print(f"❌ Количество НЕ совпадает (найдено {count}, ожидалось {true_count})")
        # cv2.imshow("Original Image", img)
        # cv2.imshow("White Objects Mask", parts_eroded)
        # cv2.imshow("Detected Objects", vis)
        # print("Нажмите любую клавишу для продолжения")
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
        return False
