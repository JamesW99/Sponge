# thanks you vishvaluke
# ref: https://github.com/vishvaluke/Snip-Sketch-OCR/blob/master/Faster%20Execution/cpocr.py
# https://docs.microsoft.com/en-us/windows/uwp/launch-resume/launch-screen-snipping
import os

appData = os.getenv('APPDATA')


def screenshot():
    try:
        '''
        call snip & sketch to take a snipshorts for selected area. Image be saved at appData/Sponge/paste.png
        :return: None
        '''
        import webbrowser
        webbrowser.open('ms-screenclip:?source=myapp&clippingMode=Rectangle')
        # webbrowser.open('ms-screenclip:edit?source=biyiapp&isTemporary=true')

        from PIL import ImageGrab
        img = ImageGrab.grabclipboard()
        i = 0
        from time import sleep
        while (img == None):
            i += 1
            sleep(1)
            img = ImageGrab.grabclipboard()
            if i > 9:
                exit()
        img = ImageGrab.grabclipboard()
        img = img.convert('RGB')
        img.save(appData + '/Sponge/paste.png', 'PNG')
    except:
        pass


if __name__ == '__main__':
    screenshot()
