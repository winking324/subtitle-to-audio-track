# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"


from charset_normalizer import from_path


def file_encoding(filename):
    return from_path(filename).best().encoding


def filter_dialogue(dialogue):
    pos = dialogue.find('\\N')
    dialogue = dialogue[:pos] if pos > 0 else dialogue

    for i in [('(', ')'), ('（', '）'), ('《', '》')]:
        start_pos = dialogue.find(i[0])
        if start_pos < 0:
            continue
        end_pos = dialogue.find(i[1])
        if end_pos < 0:
            print("WARN: filter '{}' failed".format(dialogue))
            continue
        dialogue = dialogue[:start_pos] + dialogue[end_pos + 1:]
    return dialogue


def parse_subtitle(subtitle_file):
    dialogues = []
    with open(subtitle_file, "r", encoding=file_encoding(subtitle_file)) as f:
        dialogue_format = []
        start_parse = False
        for line in f:
            if not start_parse:
                if not line.startswith("[Events]"):
                    continue
                else:
                    start_parse = True

            if line.startswith("Dialogue:"):
                if not dialogue_format:
                    print("ERROR: ass unknown format")
                    return
                formated_line = line[9:].strip().split(',')
                dialogue_text = filter_dialogue(formated_line[text_pos])
                if dialogue_text:
                    dialogues.append({
                        "text": dialogue_text,
                        "start": formated_line[start_pos],
                        "end": formated_line[end_pos]
                    })

            if line.startswith("Format:"):
                dialogue_format = line[7:].strip().split(', ')
                start_pos = dialogue_format.index("Start")
                end_pos = dialogue_format.index("End")
                text_pos = dialogue_format.index("Text")
    return dialogues
