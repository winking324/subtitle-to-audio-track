# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"
"""
https://ale5000.altervista.org/subtitles.htm
"""


from charset_normalizer import from_path


class Subtitle(object):
    def __init__(self, start, end, text):
        self.__start = start
        self.__end = end
        self.__text = text

    @property
    def start(self) -> str:
        return self.__start

    @property
    def end(self) -> str:
        return self.__end

    @property
    def text(self) -> str:
        return self.__text


class SrtParser(object):
    def __init__(self):
        self.subtitles = {}

    def parse(self, srt_file):
        subtitle_file_content = str(from_path(srt_file).best()).splitlines()
        i = 0
        while i < len(subtitle_file_content):
            try:
                line_number = int(subtitle_file_content[i].strip())
            except ValueError:
                continue
            i += 1
            showtime = subtitle_file_content[i].strip().split()
            i += 1
            text = []
            while subtitle_file_content[i].strip() != '':
                text.append(subtitle_file_content[i].strip())
                i += 1
            self.subtitles[line_number] = Subtitle(showtime[0], showtime[2], text)
            i += 1
