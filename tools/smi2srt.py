# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"

import os
from html.parser import HTMLParser


def format_ms(ms):
    hours = ms // 3600000
    ms -= hours * 3600000
    minutes = ms // 60000
    ms -= minutes * 60000
    seconds = ms // 1000
    ms -= seconds * 1000
    return '{:02}:{:02}:{:02},{:03}'.format(hours, minutes, seconds, ms)


class SubtitleItem:
    def __init__(self):
        self.start_ts = 0
        self.end_ts = 0
        self.contents = []

    def __str__(self):
        return '{} --> {}\n{}\n'.format(format_ms(self.start_ts), format_ms(self.end_ts), '\n'.join(self.contents))


class SmiParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.__subtitle_item = None
        self.__subtitle_items = []

    def subtitles(self):
        return self.__subtitle_items

    def handle_starttag(self, tag, attrs):
        if tag != 'sync':
            return

        start_ts = None
        end_ts = None
        for attr in attrs:
            if attr[0] == 'start':
                start_ts = int(attr[1])
            if attr[0] == 'end':
                end_ts = int(attr[1])

        if start_ts is None or end_ts is None:
            return

        if self.__subtitle_item is not None:
            if self.__subtitle_item.start_ts == start_ts and self.__subtitle_item.end_ts == end_ts:
                return
            self.__subtitle_items.append(self.__subtitle_item)
        self.__subtitle_item = SubtitleItem()
        self.__subtitle_item.start_ts = start_ts
        self.__subtitle_item.end_ts = end_ts

    def handle_endtag(self, tag):
        if self.__subtitle_item is not None:
            self.__subtitle_items.append(self.__subtitle_item)
            self.__subtitle_item = None

    def handle_data(self, data):
        data = data.strip()
        if not self.__subtitle_item or not data:
            return
        self.__subtitle_item.contents.append(data)


def read_smi_file(smi_file):
    print('Info: read smi file {}'.format(smi_file))
    if not os.path.exists(smi_file):
        print('Error: smi file {} not exists'.format(smi_file))
        return None

    from charset_normalizer import from_path
    smi_sgml = str(from_path(smi_file).best())

    parser = SmiParser()
    parser.feed(smi_sgml)
    return parser.subtitles()


def write_srt_file(srt_file, subtitle_items):
    print('Info: write srt file {}, count {}'.format(srt_file, len(subtitle_items)))
    with open(srt_file, 'w', encoding='utf-8') as f:
        subtitle_count = 1
        for subtitle_item in subtitle_items:
            f.write('{}\n{}\n'.format(subtitle_count, str(subtitle_item)))
            subtitle_count += 1


def smi2srt(smi_file, srt_file):
    if not srt_file:
        srt_file = os.path.join(os.path.splitext(smi_file)[0], '.srt')

    try:
        subtitle_items = read_smi_file(smi_file)
        if not subtitle_items:
            print('Error: read smi file {} failed'.format(smi_file))
            return

        write_srt_file(srt_file, subtitle_items)
    except Exception as e:
        print('Error: {}'.format(repr(e)))


def main():
    import argparse
    arg_parser = argparse.ArgumentParser(description='Convert smi to srt')
    arg_parser.add_argument('-i', '--input', type=str, help='path to smi file', required=True)
    arg_parser.add_argument('-o', '--output', type=str, help='path to srt file')
    args = arg_parser.parse_args()
    smi2srt(args.input, args.output)


if __name__ == '__main__':
    main()
