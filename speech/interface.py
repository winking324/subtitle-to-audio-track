# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"


import abc


class SpeechInterface(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def text_to_speech(self, input_text: str, output_filename: str, **kwargs) -> bool:
        pass
