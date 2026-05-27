import Cam
import podschet
import tkinter as tk
import circle_photo

def show_res(res):
    print(res)
    return res
def main():
    val = Cam.main()
    if val == True:
        val1 = circle_photo.take_photo()
        if val1 == True:
            res = podschet.main(15)
            return res[0]
            
            
