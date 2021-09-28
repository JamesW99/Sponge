import time
import pyautogui as pag
import os

def mouse_location():
    x, y = pag.position()
    return (x,y)

if __name__ == '__main__':
    try:
        while True:
            print("Press Ctrl-C to end")
            screenWidth, screenHeight = pag.size()  # 获取屏幕的尺寸
            x, y = pag.position()  # 返回鼠标的坐标
            print("Position : (%s, %s)\n" % (x, y))  # 打印坐标

            time.sleep(1)  # 每个1s中打印一次 , 并执行清屏
            os.system('cls')  # 执行系统清屏指令
    except KeyboardInterrupt:
        print('end')