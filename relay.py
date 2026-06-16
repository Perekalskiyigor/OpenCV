import serial
import time

import serial
import time

def start_vibro(work_time):
    try:
        # Увеличил write_timeout
        port = serial.Serial('COM4', 9600, timeout=1, write_timeout=2)
        
        # Даем время на инициализацию
        time.sleep(1)
        
        print(f"Порт {port.name} открыт")
        
        # Включить
        print("Отправка команды включения...")
        port.write(bytes([0xA0, 0x01, 0x01, 0xA2]))
        port.flush()  # Принудительная отправка
        print("Включено")
        
        time.sleep(work_time)
        
        # Выключить
        print("Отправка команды выключения...")
        port.write(bytes([0xA0, 0x01, 0x00, 0xA1]))
        port.flush()
        print("Выключено")
        
        port.close()
        return True
        
    except serial.SerialException as e:
        print(f"Ошибка порта: {e}")
        print("Проверьте:")
        print("- Подключено ли устройство к COM4")
        print("- Не занят ли порт другой программой")
        return False
        
    except serial.SerialTimeoutException as e:
        print(f"Таймаут записи: {e}")
        print("Устройство не отвечает. Проверьте питание и подключение")
        return False
        
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")
        return False

start_vibro(3)

#start_vibro(3)

