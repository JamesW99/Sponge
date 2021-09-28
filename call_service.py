import random
from hashlib import md5
import requests
import json

import configparser
import os

inifile = configparser.ConfigParser()
inifile.read(os.getenv('APPDATA') + '/Sponge/config.ini', 'UTF-8')

proxies = {
    'http': 'http://' + inifile.get('Advance', 'http_proxy'),
    'https': 'https://' + inifile.get('Advance', 'http_proxy'),
}


def trans(text, source, target, server):
    '''
    Translate the text into the target language.
    :param text: Words to be translated
    :param source: The language of the text to be translated
    :param target: The language wish translated into
    :param server: Which translate engine wants to be used
    :return: (String) Translation results
    '''

    def baidu():
        appid = inifile.get('ApiKey', 'baiduTraId')
        appkey = inifile.get('ApiKey', 'baiduTraKey')
        # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
        from_lang = inifile.get('baiduTra', source)
        to_lang = inifile.get('baiduTra', target)

        endpoint = 'http://api.fanyi.baidu.com'
        path = '/api/trans/vip/translate'
        url = endpoint + path

        # Generate salt and sign
        def make_md5(s, encoding='utf-8'):
            return md5(s.encode(encoding)).hexdigest()

        salt = random.randint(32768, 65536)
        sign = make_md5(appid + text + str(salt) + appkey)

        # Build request
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        payload = {'appid': appid, 'q': text, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

        # Send request
        result = requests.post(url, params=payload, headers=headers).json()

        onlytextlist = []
        for par in result['trans_result']:
            onlytextlist.append(par['dst'])

        space = '\r\r'
        return space.join(onlytextlist)

    def deepl(**kwargs):
        TOKEN = inifile.get('ApiKey', 'deeplTraKey')
        GATEWAY = 'https://api-free.deepl.com'
        from_lang = inifile.get('deeplTra', source)
        to_lang = inifile.get('deeplTra', target)

        data = {
            'auth_key': TOKEN,
            'text': text,
            'target_lang': to_lang,
            **kwargs
        }
        if inifile.getboolean('Advance', 'use_proxy'):
            resp = requests.post(GATEWAY + '/v2/translate', data=data, proxies=proxies)
        else:
            resp = requests.post(GATEWAY + '/v2/translate', data=data)

        return json.loads(resp.text)['translations'][0]['text']

    def google():
        key = inifile.get('ApiKey', 'googleTraKey')
        url = 'https://translation.googleapis.com/language/translate/v2'
        from_lang = inifile.get('googleTra', source)
        to_lang = inifile.get('googleTra', target)

        data = {
            'target': to_lang,
            'key': key,
            'q': text,
        }
        lt = []
        for k, v in data.items():
            lt.append(k + '=' + str(v))
        query_string = '&'.join(lt)
        url = url + '?' + query_string
        # print(url)

        result = requests.post(url).json()
        return result['data']['translations'][0]['translatedText']

    def lingocloud():
        url = "http://api.interpreter.caiyunai.com/v1/translator"
        token = inifile.get('ApiKey', 'lingocloudTraKey')
        from_lang = inifile.get('lingocloudTra', source)
        to_lang = inifile.get('lingocloudTra', target)

        payload = {
            "source": text,
            "trans_type": from_lang + '2' + to_lang,
            "request_id": "demo",
            "detect": True,
        }

        headers = {
            'content-type': "application/json",
            'x-authorization': "token " + token,
        }

        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        return json.loads(response.text)['target']

    def Default():
        return "Invalid Service"

    servicedict = {
        'baidu': baidu,
        'deepl': deepl,
        'google': google,
        'lingocloud': lingocloud,
        # 'youdao': youdao
    }

    resule = servicedict.get(server, Default)
    return resule()


def ocr(path, target, server):
    '''
    OCR an image in your computer.
    :param path: Path of the image to be OCR
    :param target: Wait for OCR image language
    :param server: Which OCR engine wants to be used
    :return: (String) OCR results, only text
    '''

    def tesseract():
        from PIL import Image
        import pytesseract.pytesseract
        text = pytesseract.image_to_string(Image.open(path))
        return text

    def azure():
        key = inifile.get('ApiKey', 'azureOcrKey')
        endpoint = inifile.get('ApiKey', 'azureOcrEndpoint')
        detectOrientation = 'true'

        lan = inifile.get('azureOcr', target)
        import requests

        url = 'https://' + endpoint + '.api.cognitive.microsoft.com/vision/v3.1/ocr?' + lan + '&detectOrientation=' + detectOrientation

        headers = {
            'Ocp-Apim-Subscription-Key': key,
            'Content-Type': 'application/octet-stream'
        }

        params = {
            'language': 'unk',
            'detectOrientation': 'true'
        }

        image_data = open(path, "rb").read()

        if inifile.getboolean('Advance', 'use_proxy'):
            response = requests.post(url, headers=headers, params=params, data=image_data, proxies=proxies).json()
        else:
            response = requests.post(url, headers=headers, params=params, data=image_data).json()
        # return response['regions'][0]['lines'][0]['words'][0]['text']  # get the first word.
        # time.sleep(1)
        # print(response)
        # return get_text_in_ocr_result(response["regions"][0]["lines"])

        # def get_text_in_ocr_result(ocr_result):
        result = []

        space = ' '
        for line_content in response["regions"][0]["lines"]:
            for word in line_content['words']:
                result.append(word['text'])
        return space.join(result)

    def google():
        lan = inifile.get('googleOcr', target)
        key = inifile.get('ApiKey', 'googleocrkey')
        import base64
        with open(path, 'rb') as img_file:
            base64 = base64.b64encode(img_file.read()).decode('utf8')
        headers = {'Content-Type': 'application/json'}

        data = {
            "requests": [
                {
                    "image": {
                        "content": base64
                    },
                    "features": [
                        {
                            "type": "TEXT_DETECTION"
                        }
                    ]
                }
            ]
        }

        url = 'https://vision.googleapis.com/v1/images:annotate?key=' + key

        if inifile.getboolean('Advance', 'use_proxy'):
            response = requests.post(url, headers=headers, data=json.dumps(data), proxies=proxies).json()
        else:
            response = requests.post(url, headers=headers, data=json.dumps(data)).json()
        texts = response['responses'][0]['textAnnotations'][0]['description']
        # language = response['responses'][0]['textAnnotations'][0]['locale']

        return texts

    def space(overlay=False):
        key = inifile.get('ApiKey', 'spaceocrkey')
        if inifile.get('Translator', 'from') == 'Auto':
            payload = {'isOverlayRequired': overlay,
                       'apikey': key
                       }
        else:
            payload = {'isOverlayRequired': overlay,
                       'apikey': key,
                       'language': inifile.get('spaceOcr', target),
                       }

        with open(path, 'rb') as f:
            if inifile.getboolean('Advance', 'use_proxy'):
                r = requests.post('https://api.ocr.space/parse/image', files={path: f}, data=payload,
                                  proxies=proxies).json()
            else:
                r = requests.post('https://api.ocr.space/parse/image', files={path: f}, data=payload).json()
        return r['ParsedResults'][0]['ParsedText']

    def Default():
        return "Invalid Service"

    servicedict = {
        'tesseract': tesseract,
        'azure': azure,
        'google': google,
        'space': space
        # 'youdao': youdao
    }

    resule = servicedict.get(server, Default)
    return resule()


def tts(text, target, server):
    '''
    Convert a paragraph of text to MP3 and save it.
    :param text: Text to be converted
    :param target: Text to be converted
    :param server: Text to be converted
    :return: Path of mp3 file
    '''
    if text == '':
        text = 'error'

    # https://www.geeksforgeeks.org/convert-text-speech-python-using-win32com-client/
    def localtts():
        import win32com.client
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Speak(text)

    # https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/rest-text-to-speech
    def azure():
        key = inifile.get('ApiKey', 'azurettskey')

    # https://cloud.google.com/text-to-speech/docs/reference/rest/v1/text/synthesize#AudioEncoding
    def google():
        key = inifile.get('ApiKey', 'googlettskey')
        import base64
        url = "https://texttospeech.googleapis.com/v1/text:synthesize"
        data = {
            "input": {"text": text},
            "voice": {"languageCode": target},
            "audioConfig": {"audioEncoding": "MP3"}
        }

        headers = {"content-type": "application/json", "X-Goog-Api-Key": key}

        if inifile.getboolean('Advance', 'use_proxy'):
            r = requests.post(url=url, json=data, headers=headers, proxies=proxies)
        else:
            r = requests.post(url=url, json=data, headers=headers)
        content = json.loads(r.content)
        # save as a mp3 file
        fout = open(os.getenv('APPDATA') + '/Sponge/latest.mp3', 'wb')
        fout.write(base64.b64decode(content['audioContent']))
        fout.close()
        return os.getenv('APPDATA') + '\Sponge\latest.mp3'

    def Default():
        return "Invalid Service"

    servicedict = {
        'localtts': localtts,
        'azure': azure,
        'google': google
    }

    resule = servicedict.get(server, Default)
    return resule()


if __name__ == '__main__':
    from time import ctime, sleep
    a = ocr('get_the_text\ocr\ocrtest.png', 'Auto', 'tesseract')

    print('原文为:' + a)

    print("all over %s" % ctime())
    print(trans(a, 'auto', 'chinese', 'deepl'))
    print("all over %s" % ctime())
