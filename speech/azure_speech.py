# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"
"""
[文本转语音 REST API](https://docs.microsoft.com/zh-cn/azure/cognitive-services/speech-service/rest-text-to-speech)
[语音合成标记语言 (SSML)](https://docs.microsoft.com/zh-cn/azure/cognitive-services/speech-service/speech-synthesis-markup)
[语音服务的语言和语音支持](https://docs.microsoft.com/zh-cn/azure/cognitive-services/speech-service/language-support)
"""


import http
import requests
import interface


class AzureSpeech(interface.SpeechInterface):
    def __init__(self, subscription_key, region='eastasia', **kwargs):
        self.__subscription_key = subscription_key
        self.__region = region
        self.__token = ''
        self.__request_token(region)
        self.__ssml = ''
        self.__init_ssml(**kwargs)

    def __init_ssml(self, **kwargs):
        params = dict(kwargs)
        voice_name = params.get('voice_name', 'zh-CN-XiaomoNeural')
        self.__ssml = '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" ' \
                      'xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="zh-CN">' \
                      '<voice name="{}">{{}}</voice></speak>'.format(voice_name)

    def __request_token(self, region):
        try:
            response = requests.post(
                url="https://{}.api.cognitive.microsoft.com/sts/v1.0/issuetoken".format(region),
                headers={
                    "Ocp-Apim-Subscription-Key": self.__subscription_key,
                    "Content-type": "application/x-www-form-urlencoded",
                },
            )
            if response.status_code != http.HTTPStatus.OK:
                print("ERROR: request for azure token failed")
                return
            self.__token = response.content.decode()
        except Exception as e:
            print("ERROR: request for azure token failed, {}".format(repr(e)))

    def text_to_speech(self, input_text: str, output_filename: str, **kwargs) -> bool:
        if not self.__token:
            print("Error: azure token not set")
            return False
        params = dict(kwargs)
        try:
            response = requests.post(
                url="https://{}.tts.speech.microsoft.com/cognitiveservices/v1".format(self.__region),
                headers={
                    "X-Microsoft-OutputFormat": params.get('output_format', 'audio-16khz-32kbitrate-mono-mp3'),
                    "Content-Type": "application/ssml+xml",
                    "Authorization": "Bearer {}".format(self.__token)
                },
                data=self.__ssml.format(input_text).encode('utf-8')
            )
            if response.status_code != http.HTTPStatus.OK:
                print("ERROR: request for azure text to audio failed, code {}".format(response.status_code))
                return False

            with open(output_filename, 'wb') as f:
                f.write(response.content)
                f.flush()
            return True
        except Exception as e:
            print("ERROR: request for azure text to audio failed, {}".format(repr(e)))
            return False
