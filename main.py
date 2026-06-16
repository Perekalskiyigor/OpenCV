import Cam
import podschet
import tkinter as tk
import circle_photo
import relay

def show_res(res):
    print(res)
    return res
def start():
    val = Cam.main()
    if val == True:
        val1 = circle_photo.take_photo()
        val2 = relay.start_vibro(1)
        if val1 == True and val2 == True:
            res = podschet.main(15)
            stuck_count = res[1]
            count_green = res[0]
            print(stuck_count)
            Cam.main()
            return res


            
            
