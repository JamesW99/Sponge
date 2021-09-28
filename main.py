# http://makble.com/python-win32-programming-example-register-hotkey-and-switching-tab

import ctypes
import ctypes.wintypes
import win32con
import time
import win32gui
import win32api
import threading

import win32clipboard
from get_the_text.direct_text.direct_text import copy_clipboard
from get_the_text.ocr.screenshot import screenshot
from call_service import trans, ocr, tts

import configparser
import os
inifile = configparser.ConfigParser()
inifile.read(os.getenv('APPDATA') + '/Sponge/config.ini', 'UTF-8')
appData = os.getenv('APPDATA')

# 尝试置顶

class GlobalHotKeys(object):
    """
    Register a key using the register() method, or using the @register decorator
    Use listen() to start the message pump

    Example:

    from globalhotkeys import GlobalHotKeys

    @GlobalHotKeys.register(GlobalHotKeys.VK_F1)
    def hello_world():
        print 'Hello World'

    GlobalHotKeys.listen()
    """

    key_mapping = []
    user32 = ctypes.windll.user32

    MOD_ALT = win32con.MOD_ALT
    MOD_CTRL = win32con.MOD_CONTROL
    MOD_CONTROL = win32con.MOD_CONTROL
    MOD_SHIFT = win32con.MOD_SHIFT
    MOD_WIN = win32con.MOD_WIN

    @classmethod
    def register(cls, vk, modifier=0, func=None):
        """
        vk is a windows virtual key code
         - can use ord('X') for A-Z, and 0-1 (note uppercase letter only)
         - or win32con.VK_* constants
         - for full list of VKs see: http://msdn.microsoft.com/en-us/library/dd375731.aspx

        modifier is a win32con.MOD_* constant

        func is the function to run.  If False then break out of the message loop
        """

        # Called as a decorator?
        if func is None:
            def register_decorator(f):
                cls.register(vk, modifier, f)
                return f

            return register_decorator
        else:
            cls.key_mapping.append((vk, modifier, func))

    @classmethod
    def listen(cls):
        """
        Start the message pump
        """

        try:
            for index, (vk, modifiers, func) in enumerate(cls.key_mapping):
                if not cls.user32.RegisterHotKey(None, index, modifiers, vk):
                    raise Exception(
                        'Unable to register hot key: ' + str(vk) + ' error code is: ' + str(
                            ctypes.windll.kernel32.GetLastError()))
        except:
            print('别开多个窗口')
            import sys
            sys.exit()

        try:
            msg = ctypes.wintypes.MSG()
            while cls.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                if msg.message == win32con.WM_HOTKEY:
                    (vk, modifiers, func) = cls.key_mapping[msg.wParam]
                    if not func:
                        break
                    func()

                cls.user32.TranslateMessage(ctypes.byref(msg))
                cls.user32.DispatchMessageA(ctypes.byref(msg))

        finally:
            for index, (vk, modifiers, func) in enumerate(cls.key_mapping):
                cls.user32.UnregisterHotKey(None, index)

    @classmethod
    def _include_defined_vks(cls):
        for item in win32con.__dict__:
            item = str(item)
            if item[:3] == 'VK_':
                setattr(cls, item, win32con.__dict__[item])

    @classmethod
    def _include_alpha_numeric_vks(cls):
        for key_code in (list(range(ord('A'), ord('Z'))) + list(range(ord('0'), ord('9') + 1))):
            setattr(cls, 'VK_' + chr(key_code), key_code)
        # pass


# Not sure if this is really a good idea or not?
#
# It makes decorators look a little nicer, and the user doesn't have to explicitly use win32con (and we add missing VKs
# for A-Z, 0-9
#
# But there no auto-complete (as it's done at run time), and lint'ers hate it
GlobalHotKeys._include_defined_vks()
GlobalHotKeys._include_alpha_numeric_vks()


class translationThread(threading.Thread):
    def __init__(self, text, server):
        threading.Thread.__init__(self)
        self.text = text
        self.server = server

    def fun1(self, text, server):
        try:
            a = trans(text, inifile.get('Translator', 'from'),
                      inifile.get('Translator', 'to'), server)
            print('\n%s：%s' % (server, a))
        except:
            print(server + '：我抽风了，请重试！')

    def run(self):  # 定义每个线程要运行的函数
        self.fun1(self.text, self.server)
        time.sleep(0.1)


def show(text):
    try:
        hwnd = win32gui.FindWindow(None, win32api.GetConsoleTitle())
        win32gui.SetForegroundWindow(hwnd)  # show window
    except:
        pass

    t1 = translationThread(text, inifile.get('Service', 'trabox1'))
    t2 = translationThread(text, inifile.get('Service', 'trabox2'))
    t3 = translationThread(text, 'deepl')
    t3.start()
    t1.start()
    t2.start()


# 划词翻译
@GlobalHotKeys.register(GlobalHotKeys.VK_A, GlobalHotKeys.MOD_ALT)
def shift_f1():
    print('\n开始进行划词翻译')
    try:
        text = copy_clipboard()
        print('原文：' + text + '\n')
        show(text)

    except:
        print('\n未获取到文本')


# 截图翻译
@GlobalHotKeys.register(GlobalHotKeys.VK_S, GlobalHotKeys.MOD_ALT)
def shift_f2():
    print('\n开始进行截图翻译')
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    # try:
    screenshot()
    time.sleep(0.1)
    try:
        text = ocr(appData + '/Sponge/paste.png', inifile.get('Translator', 'from'),
                   inifile.get('Service', 'ocrserver'))
        print('原文：' + text)
        show(text)
        os.remove(appData + '/Sponge/paste.png')

    except:
        print('ocr时出现了未知错误，请再试一次')


# 输入翻译
@GlobalHotKeys.register(GlobalHotKeys.VK_D, GlobalHotKeys.MOD_ALT)
def shift_f3():
    text = input('\n请输入原文：')
    show(text)


# 大声朗读
@GlobalHotKeys.register(GlobalHotKeys.VK_R, GlobalHotKeys.MOD_ALT)
def shift_f4():
    print('\n开始朗读')
    try:
        text = copy_clipboard()
        print('朗读以下内容：' + text)
        tts(text, 'en-US', 'localtts')

    except:
        print('\n未获取到文本')


# 退出
@GlobalHotKeys.register(GlobalHotKeys.VK_Q, GlobalHotKeys.MOD_ALT)
def shift_f5():
    import sys
    sys.exit()


if __name__ == "__main__":
    print("listening")
    GlobalHotKeys.listen()
