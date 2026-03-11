import time
import Cam
import crop



if __name__ == "__main__":
    val = Cam.main()
    if val == True:
        val1 = crop.crop_to_square_center("daheng_snapshot.jpg", "crop_daheng_snapshot.jpg")
        if val1 == True:
            val2 = crop.resize_to_exact("crop_daheng_snapshot.jpg", "resize_daheng_snapshot.jpg", 1000, 1000)
            if val2 == True:
                import OpenCV
             
                OpenCV.recieve_value()
