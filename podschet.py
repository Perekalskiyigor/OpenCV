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
    MIN_AREA = 700    # минимальная площадь объекта для учёта
    MAX_AREA = 300000   # МАКСИМАЛЬНАЯ площадь объекта (чтобы отсечь чёрный контур/фон)
    
    # НОВЫЕ НАСТРОЙКИ ДЛЯ ОБНАРУЖЕНИЯ СЛИПШИХСЯ ОБЪЕКТОВ
    EXPECTED_AREA_RANGE = (800, 1200)  # Ожидаемый диапазон площади ОДНОГО винта (мин, макс)
    AREA_MULTIPLIER_THRESHOLD = 1.8   # Если площадь больше ожидаемой в 1.8+ раз - подозрение на слипание

    DEBUG_SAVE = True

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
    bg_mask = ((S <= S_MAX_BG) & (V >= V_MIN_BG)).astype(np.uint8) * 255
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
        suspected_stuck_count = 0
        filtered_out_count = 0  # счётчик отфильтрованных объектов
        vis = img.copy()
        area_analysis = []
        
        # Проходим по всем компонентам (пропускаем фон - индекс 0)
        for i in range(1, num):
            area = stats[i, cv2.CC_STAT_AREA]
            
            # ФИЛЬТРАЦИЯ: пропускаем объекты, которые слишком МАЛЕНЬКИЕ или слишком БОЛЬШИЕ
            if area < MIN_AREA or area > MAX_AREA:
                if area > MAX_AREA:
                    filtered_out_count += 1
                    print(f"  ⚠️ Отфильтрован ОГРОМНЫЙ объект (площадь={area}px) - вероятно, чёрный контур")
                continue
            
            # Получаем координаты bounding box
            x, y, w, h = (stats[i, cv2.CC_STAT_LEFT],
                         stats[i, cv2.CC_STAT_TOP],
                         stats[i, cv2.CC_STAT_WIDTH],
                         stats[i, cv2.CC_STAT_HEIGHT])
            
            # Проверка на аномально большую площадь (для слипания)
            is_suspected_stuck = False
            estimated_parts = 1
            
            if area > EXPECTED_AREA_RANGE[1]:
                avg_expected_area = (EXPECTED_AREA_RANGE[0] + EXPECTED_AREA_RANGE[1]) / 2
                estimated_parts = int(round(area / avg_expected_area))
                
                if area >= EXPECTED_AREA_RANGE[1] * AREA_MULTIPLIER_THRESHOLD:
                    is_suspected_stuck = True
                    suspected_stuck_count += 1
            
            count += 1
            
            area_analysis.append({
                'id': count,
                'area': area,
                'bbox': (x, y, w, h),
                'is_stuck': is_suspected_stuck,
                'estimated_parts': estimated_parts if is_suspected_stuck else 1
            })
            
            # Рисуем рамки
            if is_suspected_stuck:
                cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 0, 255), 3)
                cv2.putText(vis, f"#{count}", (x, y-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            else:
                cv2.rectangle(vis, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(vis, str(count), (x, y-5), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            cv2.putText(vis, f"{area}", (x + w + 5, y + h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
        
        # ВЫВОД РЕЗУЛЬТАТОВ
        print("\n" + "="*60)
        print("РЕЗУЛЬТАТЫ АНАЛИЗА ОБЪЕКТОВ:")
        
        for obj in area_analysis:
            status = "⚠️ ПОДОЗРИТЕЛЬНЫЙ" if obj['is_stuck'] else "✓ НОРМАЛЬНЫЙ"
            print(f"Объект #{obj['id']}: площадь={obj['area']}px, {status}")
            if obj['is_stuck']:
                print(f"   → Возможно слиплось {obj['estimated_parts']} деталей вместе!")
        
        print("-"*60)
        print(f"ВСЕГО объектов (после фильтрации): {count}")
        print(f"Отфильтровано огромных объектов (контур/фон): {filtered_out_count}")
        print(f"Подозрительных объектов (возможно слипшихся): {suspected_stuck_count}")
        
        # Статистика по площадям
        if area_analysis:
            areas = [obj['area'] for obj in area_analysis]
            normal_areas = [obj['area'] for obj in area_analysis if not obj['is_stuck']]
            
            print(f"\nСтатистика по площадям:")
            print(f"  - Минимальная площадь: {min(areas)}px")
            print(f"  - Максимальная площадь: {max(areas)}px")
            print(f"  - Средняя площадь: {sum(areas)/len(areas):.0f}px")
            if normal_areas:
                print(f"  - Средняя площадь нормальных объектов: {sum(normal_areas)/len(normal_areas):.0f}px")
        
        if suspected_stuck_count > 0:
            print(f"\n⚠️ ВНИМАНИЕ: Обнаружены {suspected_stuck_count} объектов с аномально большой площадью!")
            print("   Возможно, это слипшиеся детали (отмечены красным).")
        else:
            print("\n✓ Все объекты имеют нормальную площадь. Слипаний не обнаружено.")
        
        print("="*60 + "\n")
        
        return vis, count, suspected_stuck_count, area_analysis, filtered_out_count

    # -------------------------
    # 6) Подсчёт и проверка
    # -------------------------
    vis, count, stuck_count, analysis, filtered_out = count_white_objects()
    
    print(f"\nИТОГО:")
    print(f"  - Количество учтённых объектов: {count}")
    print(f"  - Отфильтровано (гигантские объекты): {filtered_out}")
    print(f"  - Подозрительных на слипание: {stuck_count}")
    
    # -------------------------
    # 7) Визуализация и вывод
    # -------------------------
    save("dbg_final_result.png", vis)
    save("dbg_final_mask.png", parts_eroded)
    
    return count, stuck_count

# if __name__ == "__main__":
#     # Пример вызова
#     erosion_size = 3  # подберите нужный размер эрозии
#     count, stuck = main(erosion_size)