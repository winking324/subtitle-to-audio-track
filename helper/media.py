# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"


import re
import os

import ffmpy
import decimal
import subprocess
import collections
from pytimeparse import parse as timeparse


def duration_with_precision(d):
    return decimal.Decimal(d).quantize(decimal.Decimal('.01'), rounding=decimal.ROUND_HALF_EVEN)


SPACE_DURATION = duration_with_precision(0.5)
MAX_MIX_COUNT = 30


def time_format(duration):
    seconds = int(duration)
    milliseconds = round(duration * 100 - seconds * 100)
    seconds = int(seconds)
    minutes = 0
    hours = 0
    if seconds > 60:
        minutes = int(seconds / 60)
        seconds = seconds % 60
        if minutes > 60:
            hours = int(minutes/60)
            minutes = minutes % 60
    return "%02d:%02d:%02d.%02d" % (hours, minutes, seconds, milliseconds)


def extract_audio(video_file, audio_file):
    ff = ffmpy.FFmpeg(
        inputs={video_file: None},
        outputs={audio_file: ["-vn"]}
    )
    ff.run(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def create_blank_audio(audio_file, duration):
    ff = ffmpy.FFmpeg(
        global_options=["-f", "lavfi"],
        inputs={"anullsrc=r=16000:cl=mono": None},
        outputs={audio_file: ["-t", str(duration), "-q:a", "9"]}
        # outputs={audio_file: ["-t", str(duration), "-q:a", "9", "-acodec", "libmp3lame"]}
    )
    ff.run(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def audio_duration(audio_file):
    ff = ffmpy.FFmpeg(
        inputs={audio_file: None},
        outputs={None: ["-f", "null", "-"]}
    )
    _, output = ff.run(stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return duration_with_precision(timeparse(re.findall(r'Duration: ([\d:.]+)', output.decode())[0]))


def mix_audios(inputs, output, filters, amix):
    for i in range(len(filters)):
        filters[i] = filters[i].format(len(filters) - i)
    filters.append(amix + 'amix=inputs={}[out]'.format(len(inputs)))
    ff = ffmpy.FFmpeg(
        inputs=collections.OrderedDict(inputs),
        outputs={
            output: [
                '-filter_complex',
                '; '.join(filters),
                '-map',
                '[out]'
            ]
        }
    )
    print(ff.cmd)
    ff.run(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def add_audio_track(video_file, audio_file, output_file):
    ff = ffmpy.FFmpeg(
        inputs={
            video_file: None,
            audio_file: None
        },
        outputs={
            output_file: ['-map', '0', '-map', '1', '-c', 'copy']
        }
    )
    ff.run(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def mix_speech(blank_audio_file, dialogues, output_path):
    mixed_count = 0
    inputs = [(blank_audio_file, None)]
    filters = []
    amix = '[0:a]'
    outputs = []
    for i in range(len(dialogues)):
        if len(inputs) >= MAX_MIX_COUNT:
            output_file = os.path.join(output_path, "mixed_{}.mp3".format(mixed_count))
            mix_audios(inputs, output_file, filters, amix)
            outputs.append(output_file)

            mixed_count += 1
            inputs = [(blank_audio_file, None)]
            filters = []
            amix = '[0:a]'

        dialogue_filename = os.path.join(output_path, "{}.mp3".format(i))
        inputs.append((dialogue_filename, None))

        delay = int(duration_with_precision(timeparse(dialogues[i]["start"])) * 1000)
        filters.append('[{p}]adelay={d}|{d},volume={{}}[a{p}]'.format(p=len(inputs) - 1, d=delay))
        amix += '[a{}]'.format(len(inputs) - 1)
    if len(inputs) > 0:
        output_file = os.path.join(output_path, "mixed_{}.mp3".format(mixed_count))
        mix_audios(inputs, output_file, filters, amix)
        outputs.append(output_file)
    return outputs


def mix_accompaniment(accompaniment, speech, output_path):
    speech.insert(0, accompaniment)
    inputs = []
    filters = []
    amix = []
    for i in range(len(speech)):
        inputs.append((speech[i], None))
        filters.append('[{p}]volume={v}[a{p}]'.format(p=i, v=len(speech) - i))
        amix.append('[a{}]'.format(i))
    mix_audios(inputs, output_path, filters, ''.join(amix))


def audios_duration(dialogues, output_path):
    for i in range(len(dialogues)):
        output_filename = os.path.join(output_path, "{}.mp3".format(i))
        if not os.path.exists(output_filename):
            print("WARN: audio file {} not exist".format(i))
            dialogues[i]["duration"] = duration_with_precision(0)
            continue

        duration = audio_duration(output_filename)
        if duration.compare(SPACE_DURATION) > 0:
            duration = duration - SPACE_DURATION
        else:
            print("WARN: audio file {} duration {}s".format(i, duration))
        dialogues[i]["duration"] = duration
    return dialogues


def check_dialogues_audios(dialogues, output_path):
    dialogues = audios_duration(dialogues, output_path)
    overlap_count = 0
    for i in range(len(dialogues) - 1):
        dialogue = dialogues[i]
        next_dialogue = dialogues[i + 1]
        duration = dialogue["duration"]
        dialogue_duration = duration_with_precision(timeparse(next_dialogue["start"])) - duration_with_precision(timeparse(dialogue["start"]))
        if duration.compare(dialogue_duration) > 0:
            overlap_count += 1
            duration_delta = duration - dialogue_duration
            total_duration = duration + next_dialogue["duration"]
            if i + 2 < len(dialogues):
                total_dialogue_duration = duration_with_precision(timeparse(dialogues[i + 2]["start"])) - duration_with_precision(timeparse(dialogue["start"]))
                if total_duration.compare(total_dialogue_duration) > 0:
                    print("WARN: audio file {} duration {}s longer than {}[{}, {}]".format(
                        i, duration, dialogue_duration, dialogue["start"], next_dialogue["start"]))
                    continue
                print("WARN: modify next dialogue [{}, {}] delta {}".format(
                    next_dialogue["start"], next_dialogue["end"], duration_delta))
            next_dialogue["start"] = time_format(duration_with_precision(timeparse(next_dialogue["start"])) + duration_delta)
            next_dialogue["end"] = time_format(duration_with_precision(timeparse(next_dialogue["end"])) + duration_delta)
    return dialogues, overlap_count
