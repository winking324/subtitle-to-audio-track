# -*- coding: utf-8 -*-
__author__ = "winking324@gmail.com"


import ffmpy
import os.path
import argparse
import helper.media
import helper.speech
import helper.subtitle
from spleeter.separator import Separator


SPLEET_OUTPUT = "spleet_output"
SPEECH_OUTPUT = "speech_output"


def extract_audio(video_file, audio_file):
    ff = ffmpy.FFmpeg(
        inputs={video_file: None},
        outputs={audio_file: ["-vn", "-loglevel", "quiet"]}
    )
    ff.run()


def spleet_audio(audio_file, duration):
    separator = Separator("spleeter:2stems")
    spleet_path = os.path.join(os.path.dirname(audio_file), SPLEET_OUTPUT)
    separator.separate_to_file(audio_file, spleet_path, duration=float(duration))


def subtitle_to_audio_track(video_file):
    base_file = os.path.splitext(video_file)[0]
    if not os.path.exists(base_file):
        os.mkdir(base_file)

    video_path = os.path.dirname(video_file)
    video_filename = os.path.basename(video_file)

    speech_path = os.path.join(video_path, os.path.splitext(video_filename)[0], SPEECH_OUTPUT)
    if not os.path.exists(speech_path):
        os.mkdir(speech_path)

    print("parse subtitle ...")
    subtitle_file = base_file + ".ass"
    if not os.path.exists(subtitle_file):
        print("ERROR: not exist subtitle file (*.ass)")
        return False
    dialogues = helper.subtitle.parse_subtitle(os.path.splitext(video_file)[0] + ".ass")
    helper.speech.dialogues_to_audios(dialogues, speech_path)

    print("check speech ...")
    dialogues, overlap_count = helper.media.check_dialogues_audios(dialogues, speech_path)
    if overlap_count > 0:
        print("re-check speech ...")
        _, overlap_count = helper.media.check_dialogues_audios(dialogues, speech_path)
        if overlap_count > 0:
            print("ERROR: re-check speech overlap failed, count {}".format(overlap_count))

    print("extract audio ...")
    audio_file = os.path.join(base_file, "origin.mp3")
    total_duration = helper.media.audio_duration(audio_file)
    if os.path.exists(audio_file):
        print("audio file already extracted, ignore")
    else:
        extract_audio(video_file, audio_file)

    print("spleet audio ...")
    spleet_path = os.path.join(video_path, os.path.splitext(video_filename)[0], SPLEET_OUTPUT)
    vocals_file = os.path.join(spleet_path, "vocals.wav")
    accompaniment_file = os.path.join(spleet_path, "accompaniment.wav")
    if os.path.exists(vocals_file) and os.path.exists(accompaniment_file):
        print("audio file already spleeted, ignore")
    else:
        spleet_audio(audio_file, total_duration)

    print("create blank audio file ...")
    blank_audio_file = os.path.join(speech_path, "blank.mp3")
    if os.path.exists(blank_audio_file):
        print("blank audio file already created, ignore")
    else:
        helper.media.create_blank_audio(blank_audio_file, total_duration)

    print("mix speech files ...")
    mixed_auido_file = os.path.join(speech_path, "mixed.mp3")
    if os.path.exists(mixed_auido_file):
        print("mixed audio file already existed, ignore")
    else:
        outputs = helper.media.mix_speech(blank_audio_file, dialogues, speech_path)
        helper.media.mix_accompaniment(accompaniment_file, outputs, mixed_auido_file)

    print("add audio track ...")
    output_video_file = base_file + ".ch" + os.path.splitext(video_file)[1]
    if os.path.exists(output_video_file):
        print("output video file already existed, ignore")
    else:
        helper.media.add_audio_track(video_file, mixed_auido_file, output_video_file)

    print("done, enjoy the video")


def main():
    arg_parser = argparse.ArgumentParser(description='Subtitle to audio track')
    arg_parser.add_argument('video', type=str, help='path to video file')
    args = arg_parser.parse_args()
    subtitle_to_audio_track(args.video)


if __name__ == '__main__':
    main()
