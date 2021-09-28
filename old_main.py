# https://blog.csdn.net/Fandes_F/article/details/103226341

import os
import threading

import time
import win32clipboard
from get_the_text.direct_text.direct_text import copy_clipboard
from get_the_text.ocr.screenshot import screenshot

from threading import Thread
from pynput import keyboard
from call_service import trans, ocr, tts
import configparser
import os

inifile = configparser.ConfigParser()
inifile.read(os.getenv('APPDATA') + '/Sponge/config.ini', 'UTF-8')

ALT = False
A = False
S = False
D = False

appData = os.getenv('APPDATA')


def listen():  # 键盘监听函数
    print("listening")

    class MyThread(threading.Thread):
        def __init__(self, text, server):
            threading.Thread.__init__(self)
            self.text = text
            self.server = server

        def fun1(self, text, server):
            try:
                from time import ctime, sleep
                T1 = time.process_time()
                a = trans(text, inifile.get('Translator', 'from'), inifile.get('Translator', 'to'),
                          server)
                print('%s：%s\n' % (server, a))
                T2 =time.process_time()
                print(server+' :%s毫秒' ,((T2 - T1) * 1000))
            except:
                pass

        def run(self):  # 定义每个线程要运行的函数
            self.fun1(self.text, self.server)
            time.sleep(0.1)

    def show(text):
        t1 = MyThread(text, inifile.get('Service', 'trabox1'))
        t2 = MyThread(text, inifile.get('Service', 'trabox2'))
        t3 = MyThread(text, 'deepl')
        t1.start()
        t2.start()
        t3.start()

    def action1():
        print('\n开始进行划词翻译')
        try:
            text = copy_clipboard()
            print('原文：' + text + '\n')
            show(text)

        except:
            print('\n未获取到文本')

    def action2():
        print('\n开始进行截图翻译')
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        try:
            screenshot()
            time.sleep(0.1)
            # try:
            text = ocr(appData + '/Sponge/tem_image/paste.png', inifile.get('Translator', 'from'),
                       inifile.get('Service', 'ocrserver'))
            print('原文：' + text)
            show(text)
            os.remove(appData + '/Sponge/tem_image/paste.png')

        except:
            print('\n出现了未知错误，请再试一次')

    def action3():
        text = input('\n请输入原文：')
        show(text)

    def on_press(key):
        global ALT, A, S, D
        if key == keyboard.Key.alt or key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            ALT = True
        if key == keyboard.KeyCode(char='a') or key == keyboard.KeyCode(char='A'):
            A = True
        if key == keyboard.KeyCode(char='s') or key == keyboard.KeyCode(char='S'):
            S = True
        if key == keyboard.KeyCode(char='d') or key == keyboard.KeyCode(char='D'):
            D = True

        if ALT and A:  # 检测到Alt和a同时按下时
            ALT = A = False
            action1()

        if ALT and S:  # 检测到Alt和a同时按下时
            ALT = S = False
            action2()

        if ALT and D:  # 检测到Alt和a同时按下时
            ALT = D = False
            action3()

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()


class ListenThread(Thread):  # 截屏监听线程，监听函数一定要放在后台线程里康康说明那个join了吗（￣︶￣）↗　

    def __init__(self):
        super().__init__()

    def run(self):
        listen()


if __name__ == "__main__":
    listenThread = ListenThread()  # 创建监听线程
    listenThread.start()
