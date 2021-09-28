# https://stackoverflow.com/questions/51505304/copy-highlighted-text-to-clipboard-then-use-the-clipboard-to-append-it-to-a-lis


import pyautogui as pya
import pyperclip  # handy cross-platform clipboard text handler
import time

def copy_clipboard():
    # time.sleep(0.2)  # ctrl-c is usually very fast but your program may execute faster
    time.sleep(0.9)
    pya.hotkey('ctrl', 'c')
    return pyperclip.paste()

if __name__ == '__main__':
    print(copy_clipboard())