import gxipy as gx
import cv2
import numpy as np
import sys

def main():
    """
    Пример подключения к камере Daheng MER2-2000-19U3M,
    отправки команды на захват кадра и сохранения фото.
    """
    print("Инициализация DeviceManager...")
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_device_list()

    if dev_num == 0:
        print("Ошибка: Камера не найдена. Проверьте подключение.")
        sys.exit(1)

    print(f"Найдено устройств: {dev_num}")
    # Для примера берем первую найденную камеру
    cam = device_manager.open_device_by_index(1)
    # Альтернатива: открыть по серийному номеру
    # sn = dev_info_list[0].get("sn")
    # cam = device_manager.open_device_by_sn(sn)

    # --- Настройка параметров камеры перед съемкой ---
    print("Настройка параметров камеры...")

    # 1. Отключаем автоматические режимы, чтобы иметь полный контроль.
    #    Это критически важно, если мы хотим отправлять точные команды.
    #    Значения передаются как целые числа: 0 = Off, 1 = Once, 2 = Continuous [citation:9].
    if hasattr(cam, 'ExposureAuto'):
        cam.ExposureAuto.set(0)  # 0 = Off
        print("  ExposureAuto: Off")
    if hasattr(cam, 'GainAuto'):
        cam.GainAuto.set(0)      # 0 = Off
        print("  GainAuto: Off")

    # 2. Устанавливаем ручные значения (примеры)
    #    Убедитесь, что значения поддерживаются вашей камерой.
    if hasattr(cam, 'ExposureTime'):
        # Устанавливаем время экспозиции, например, 20000 микросекунд (20 мс)
        cam.ExposureTime.set(20000.0)
        print(f"  ExposureTime: {cam.ExposureTime.get()}")
    if hasattr(cam, 'Gain'):
        # Устанавливаем усиление, например, 0.0 дБ
        cam.Gain.set(0.0)
        print(f"  Gain: {cam.Gain.get()}")

    # --- Отправка команды на захват и получение данных ---
    print("\nОтправка команды на захват кадра...")
    # Включаем поток данных. Это необходимо сделать перед захватом [citation:2][citation:8].
    cam.stream_on()

    # Получаем один кадр из потока данных
    # data_stream[0] - первый (и обычно единственный) канал данных [citation:7].
    raw_image = cam.data_stream[0].get_image()

    if raw_image is None:
        print("Ошибка: Не удалось получить изображение.")
        cam.stream_off()
        cam.close_device()
        sys.exit(1)

    print(f"  Кадр получен. Статус: {raw_image.get_status()}")

    # --- Обработка и сохранение изображения ---
    # Конвертируем сырые данные в формат RGB (если камера цветная)
    # Для монохромной камеры можно использовать raw_image.get_numpy_array() напрямую.
    rgb_image = raw_image.convert("RGB")
    if rgb_image is None:
        print("Ошибка конвертации в RGB.")
        cam.stream_off()
        cam.close_device()
        sys.exit(1)

    # Получаем numpy массив для работы с OpenCV
    numpy_frame = rgb_image.get_numpy_array()

    # OpenCV использует формат BGR, конвертируем из RGB
    frame_bgr = cv2.cvtColor(numpy_frame, cv2.COLOR_RGB2BGR)

    # Сохраняем изображение
    output_filename = "daheng_snapshot.jpg"
    cv2.imwrite(output_filename, frame_bgr)
    print(f"  Снимок сохранен как '{output_filename}'")

    # --- Завершение работы ---
    print("Остановка потока и закрытие устройства...")
    cam.stream_off()
    cam.close_device()
    print("Готово.")
    return True

# if __name__ == "__main__":
#      main()