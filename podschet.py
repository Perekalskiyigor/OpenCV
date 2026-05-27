# import cv2
# import numpy as np

# def main(erosion_size):

#     IMAGE_PATH = 'resize_daheng_snapshot.jpg'

#     # -------------------------
#     # НАСТРОЙКИ
#     # -------------------------
#     # Порог белого фона в HSV:
#     S_MAX_BG = 80     # чем меньше, тем "белее" (50-80)
#     V_MIN_BG = 210    # чем больше, тем ярче (170-210)

#     # Морфология маски деталей
#     OPEN_K = 5        # убрать мелкий мусор
#     OPEN_IT = 1

#     CLOSE_K = 1       # подлечить дырки/резьбу
#     CLOSE_IT = 1

#     # Фильтр по площади (выкинуть мусорные компоненты)
#     MIN_AREA = 100   # минимальная площадь объекта для учёта

#     DEBUG_SAVE = True

#     # принимаем путь фото
#     def upload_image(PATH):
#         global IMAGE_PATH
#         IMAGE_PATH = PATH
#         print(IMAGE_PATH)

#     def save(name, img):
#         if DEBUG_SAVE:
#             cv2.imwrite(name, img)

#     # -------------------------
#     # 1) Загрузка
#     # -------------------------
#     img = cv2.imread(IMAGE_PATH)
#     if img is None:
#         raise RuntimeError(f"Не удалось открыть {IMAGE_PATH}")

#     hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
#     H, S, V = cv2.split(hsv)

#     # -------------------------
#     # 2) Убираем белый фон (делаем маску деталей)
#     # -------------------------
#     # фон: S низкий и V высокий
#     bg_mask = ((S <= S_MAX_BG) & (V >= V_MIN_BG)).astype(np.uint8) * 255

#     # детали = НЕ фон
#     parts = cv2.bitwise_not(bg_mask)

#     # Лёгкая подчистка шумов на старте
#     k_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (OPEN_K, OPEN_K))
#     k_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (CLOSE_K, CLOSE_K))

#     parts = cv2.morphologyEx(parts, cv2.MORPH_OPEN, k_open, iterations=OPEN_IT)
#     parts = cv2.morphologyEx(parts, cv2.MORPH_CLOSE, k_close, iterations=CLOSE_IT)

#     save("dbg_parts_mask_before_erode.png", parts)

#     # -------------------------
#     # 3) ЭРОЗИЯ - уменьшаем объекты, чтобы разделить слипшиеся
#     # -------------------------
#     erosion_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erosion_size, erosion_size))
#     parts_eroded = cv2.erode(parts, erosion_kernel, iterations=1)

#     save("dbg_parts_mask_after_erode.png", parts_eroded)

#     # -------------------------
#     # 4) Находим связные компоненты (белые пятна)
#     # -------------------------
#     num, labels, stats, _ = cv2.connectedComponentsWithStats(parts_eroded, connectivity=8)

#     # -------------------------
#     # 5) Считаем ТОЛЬКО белые объекты (каждый отдельно)
#     # -------------------------
#     def count_white_objects():
#         count = 0
#         vis = img.copy()
        
#         # Проходим по всем компонентам (пропускаем фон - индекс 0)
#         for i in range(1, num):
#             area = stats[i, cv2.CC_STAT_AREA]
            
#             # Фильтруем по минимальной площади
#             if area < MIN_AREA:
#                 continue
            
#             # Получаем координаты bounding box
#             x, y, w, h = (stats[i, cv2.CC_STAT_LEFT],
#                          stats[i, cv2.CC_STAT_TOP],
#                          stats[i, cv2.CC_STAT_WIDTH],
#                          stats[i, cv2.CC_STAT_HEIGHT])
            
#             # Увеличиваем счётчик
#             count += 1
            
#             # Рисуем прямоугольник вокруг каждого найденного объекта
#             cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)  # зелёный прямоугольник
#             cv2.putText(vis, str(count), (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
#         return vis, count

#     # -------------------------
#     # 6) Подсчёт и проверка
#     # -------------------------
#     vis, count = count_white_objects()
#     print("--"*60, count)
#     cv2.imshow("Original Image", img)
#     cv2.imshow("White Objects Mask", parts_eroded)
#     cv2.imshow("Detected Objects", vis)
      
#     print("Нажмите любую клавишу для продолжения")
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
#     return (count)
#     # Сохраняем результаты всегда
#     save("dbg_final_result.png", vis)
#     save("dbg_final_mask.png", parts_eroded)
    
#     # Показываем изображения ТОЛЬКО если количество совпадает
import cv2
import numpy as np

def main(erosion_size):

    IMAGE_PATH = 'daheng_snapshot_circle.png'

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
    MIN_AREA = 100    # минимальная площадь объекта для учёта
    
    # НОВЫЕ НАСТРОЙКИ ДЛЯ ОБНАРУЖЕНИЯ СЛИПШИХСЯ ОБЪЕКТОВ
    EXPECTED_AREA_RANGE = (50, 200)  # Ожидаемый диапазон площади ОДНОГО винта (мин, макс)
    AREA_MULTIPLIER_THRESHOLD = 1.8   # Если площадь больше ожидаемой в 1.8+ раз - подозрение на слипание
    # (2.0 означает ровно в 2 раза, 1.8 - чуть меньше для надёжности)

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
    # 5) Считаем объекты С ФИЛЬТРАЦИЕЙ ПО ПЛОЩАДИ
    # -------------------------
    def count_white_objects():
        count = 0
        suspected_stuck_count = 0  # счётчик подозрительных объектов
        vis = img.copy()
        area_analysis = []  # для хранения информации о всех объектах
        
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
            
            # НОВЫЙ КОД: Проверка на аномально большую площадь
            is_suspected_stuck = False
            estimated_parts = 1  # предполагаемое количество слипшихся деталей
            
            # Проверяем, превышает ли площадь ожидаемый диапазон
            if area > EXPECTED_AREA_RANGE[1]:
                # Рассчитываем примерное количество деталей
                avg_expected_area = (EXPECTED_AREA_RANGE[0] + EXPECTED_AREA_RANGE[1]) / 2
                estimated_parts = int(round(area / avg_expected_area))
                
                # Проверяем, входит ли объект в критерии "слипания"
                if area >= EXPECTED_AREA_RANGE[1] * AREA_MULTIPLIER_THRESHOLD:
                    is_suspected_stuck = True
                    suspected_stuck_count += 1
            
            # Увеличиваем счётчик
            count += 1
            
            # Сохраняем информацию для анализа
            area_analysis.append({
                'id': count,
                'area': area,
                'bbox': (x, y, w, h),
                'is_stuck': is_suspected_stuck,
                'estimated_parts': estimated_parts if is_suspected_stuck else 1
            })
            
            # Рисуем прямоугольник вокруг каждого найденного объекта
            if is_suspected_stuck:
                # КРАСНЫЙ прямоугольник для подозрительных (слипшихся)
                cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 0, 255), 3)  # красный, толще
                # Дополнительная маркировка

                cv2.putText(vis, f"#{count}", (x, y-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                # ЗЕЛЁНЫЙ прямоугольник для нормальных объектов
                cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(vis, str(count), (x, y-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Также показываем площадь рядом с каждым объектом
            cv2.putText(vis, f"{area}", (x + w + 5, y + h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        # ВЫВОД РЕЗУЛЬТАТОВ АНАЛИЗА В КОНСОЛЬ
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА ОБЪЕКТОВ:")
        #print("="*60)
        
        for obj in area_analysis:
            status = "⚠️ ПОДОЗРИТЕЛЬНЫЙ" if obj['is_stuck'] else "✓ НОРМАЛЬНЫЙ"
           # print(f"Объект #{obj['id']}: площадь={obj['area']}px, {status}")
            if obj['is_stuck']:
                print(f"   → Возможно слиплось {obj['estimated_parts']} деталей вместе!")
        
        print("-"*60)
        print(f"ВСЕГО объектов: {count}")
        print(f"Подозрительных объектов (возможно слипшихся): {suspected_stuck_count}")
        
        # Дополнительная статистика по площадям
        if area_analysis:
            areas = [obj['area'] for obj in area_analysis]
            normal_areas = [obj['area'] for obj in area_analysis if not obj['is_stuck']]
            
            # print(f"\nСтатистика по площадям:")
            print(f"  - Минимальная площадь: {min(areas)}px")
            print(f"  - Максимальная площадь: {max(areas)}px")
            # print(f"  - Средняя площадь: {sum(areas)/len(areas):.0f}px")
            if normal_areas:
                print(f"  - Средняя площадь нормальных объектов: {sum(normal_areas)/len(normal_areas):.0f}px")
        
        # ПРЕДУПРЕЖДЕНИЕ В КОНСОЛЬ
        if suspected_stuck_count > 0:
          # print("\n" + "!"*60)
           # print("⚠️ ВНИМАНИЕ: Обнаружены объекты с аномально большой площадью!")
            print(f"   Возможно, {suspected_stuck_count} объект(ов) содержит слипшиеся детали.")
          #  print("   Рекомендуется проверить эти области визуально (отмечены красным).")
          #  print("!"*60)
        else:
            print("\n✓ Все объекты имеют нормальную площадь. Слипаний не обнаружено.")
        
        #print("="*60 + "\n")
        
        return vis, count, suspected_stuck_count, area_analysis

    # -------------------------
    # 6) Подсчёт и проверка
    # -------------------------
    vis, count, stuck_count, analysis = count_white_objects()
    
    print(f"Количество обнаруженных объектов: {count}")
    print(f"Количество слипшихся объектов: {stuck_count}")
    
    # -------------------------
    # 7) Визуализация и вывод
    # -------------------------
    # cv2.imshow("Original Image", img)
    # cv2.imshow("White Objects Mask", parts_eroded)
    # cv2.imshow("Detected Objects", vis)
    
    # Сохраняем результаты
    save("dbg_final_result.png", vis)
    save("dbg_final_mask.png", parts_eroded)
    
    # print("Нажмите любую клавишу для завершения")
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    
    return count, stuck_count