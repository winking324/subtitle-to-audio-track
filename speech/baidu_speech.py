# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"
"""
[百度语音合成服务](https://ai.baidu.com/ai-doc/SPEECH/Gk38y8lzk)
"""

import http
import json
import uuid
import requests
import interface
from urllib.parse import quote


class BaiduSpeech(interface.SpeechInterface):
    def __init__(self, client_id: str, client_secret: str, cuid: str = ''):
        self.__cuid = cuid if cuid else uuid.uuid4()
        self.__token = ''
        self.__request_token(client_id, client_secret)

    def __request_token(self, client_id: str, client_secret: str) -> None:
        try:
            response = requests.post(
                url="https://aip.baidubce.com/oauth/2.0/token",
                params={
                    "grant_type": "client_credentials",
                    "client_id": client_id,
                    "client_secret": client_secret,
                }
            )
            if response.status_code != http.HTTPStatus.OK:
                print("ERROR: request for baidu token failed")
                return
            self.__token = json.loads(response.content)["access_token"]
        except Exception as e:
            print("ERROR: request for baidu token failed, {}".format(repr(e)))

    def text_to_speech(self, input_text: str, output_filename: str, **kwargs) -> bool:
        if not self.__token:
            print("Error: baidu access token not set")
            return False

        params = dict(kwargs)
        tex = quote(quote(input_text))
        data = "tex={}&tok={}&cuid={}&ctp=1&lan=zh&spd={}&pit={}&vol={}&per={}&aue={}".format(
            tex, self.__token, self.__cuid, params.get('spd', 5), params.get('pit', 5),
            params.get('vol', 5), params.get('per', 3), params.get('aue', 3))
        try:
            response = requests.post(
                url="https://tsn.baidu.com/text2audio",
                data=data
            )
            if response.status_code != http.HTTPStatus.OK:
                print("ERROR: request for baidu text to audio failed")
                return False

            with open(output_filename, 'wb') as f:
                f.write(response.content)
                f.flush()
            return True
        except Exception as e:
            print("ERROR: request for baidu text to audio failed, {}".format(repr(e)))
            return False




