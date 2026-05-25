import time
import Cam
import crop
import OpenCV_calibrovka

#ввести колво винтов
true_count = 10
  

if __name__ == "__main__":
    val = Cam.main()
    if val == True:
        val1 = crop.crop_to_square_center("daheng_snapshot.jpg", "crop_daheng_snapshot.jpg")
        if val1 == True:
            val2 = crop.resize_to_exact("crop_daheng_snapshot.jpg", "resize_daheng_snapshot.jpg", 1000, 1000)
        if val2 == True: 
            for ero in range (1 , 40):
                res = OpenCV_calibrovka.main(ero, true_count)
                if res == True:
                    print (f"Lля данной единицы номенклаутры, параметры настроены ({ero})")

                    
            
