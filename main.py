import Cam
import crop
import podschet
import tkinter as tk

def show_res(res):
    print(res)
    return res
def main():
    val = Cam.main()
    if val == True:
        val1 = crop.crop_to_square_center("daheng_snapshot.jpg", "crop_daheng_snapshot.jpg")
        if val1 == True:
            val2 = crop.resize_to_exact("crop_daheng_snapshot.jpg", "resize_daheng_snapshot.jpg", 1500, 1500)
        if val2 == True: 
            res = podschet.main(15)
            return res[0]
            
            
