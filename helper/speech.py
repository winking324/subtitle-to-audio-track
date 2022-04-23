# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"


import json
import http
import os.path
import requests
from urllib.parse import quote


# Refer to Baidu API document
# https://ai.baidu.com/ai-doc/SPEECH/Gk38y8lzk
BAIDU_CUID = ""
BAIDU_CLIENT_ID = ""
BAIDU_CLIENT_SECRET = ""


def request_token():
    try:
        response = requests.post(
            url="https://aip.baidubce.com/oauth/2.0/token",
            params={
                "grant_type": "client_credentials",
                "client_id": BAIDU_CLIENT_ID,
                "client_secret": BAIDU_CLIENT_SECRET,
            }
        )
        if response.status_code != http.HTTPStatus.OK:
            print("ERROR: request for baidu token failed")
            return None
        return json.loads(response.content)["access_token"]
    except Exception as e:
        print("ERROR: request for baidu token failed, {}".format(repr(e)))
        return None


def text_to_audio(filename, tex, tok, spd=5, pit=5, vol=5, per=3, aue=3):
    tex = quote(quote(tex))
    data = "tex={}&tok={}&cuid={}&ctp=1&lan=zh&spd={}&pit={}&vol={}&per={}&aue={}".format(
        tex, tok, BAIDU_CUID, spd, pit, vol, per, aue)
    try:
        response = requests.post(
            url="https://tsn.baidu.com/text2audio",
            data=data
        )
        if response.status_code != http.HTTPStatus.OK:
            print("ERROR: request for baidu text to audio failed")
            return False

        with open(filename, 'wb') as f:
            f.write(response.content)
            f.flush()
        return True
    except Exception as e:
        print("ERROR: request for baidu text to audio failed, {}".format(repr(e)))
        return False


def dialogues_to_audios(dialogues, output_path):
    tok = request_token()
    for i in range(len(dialogues)):
        dialogue = dialogues[i]
        output_filename = os.path.join(output_path, "{}.mp3".format(i))
        if os.path.exists(output_filename):
            continue
        text_to_audio(output_filename, dialogue["text"], tok)
