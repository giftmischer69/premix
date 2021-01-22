import subprocess

import streamlit as st

import sox
from pytube import YouTube

from pathlib import Path

import librosa
import numpy as np
from spleeter.separator import Separator


def get_wav_file_name(file_name: str) -> str:
    suffix = Path(file_name).suffix
    return file_name.replace(suffix, ".wav")


def convert_to_wav(stream, file_handle):
    if "beat" in file_handle.lower():
        new_file = "beat.wav"  # get_wav_file_name(file_handle)
    else:
        new_file = "vocals.wav"
    subprocess.run(["ffmpeg", "-y", "-i", file_handle, "-ar", "44100", new_file])
    print(f"built {new_file}")


def download_to_wav(url: str):
    yt = YouTube(url)
    yt.register_on_complete_callback(convert_to_wav)
    stream = yt.streams.filter(only_audio=True).order_by("abr").first()
    print(stream)
    stream.download()


def detect_bpm(wav_file):
    y, sr = librosa.load(wav_file)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    print(tempo)
    return tempo


def get_beat_times(wav_file):
    # detect beats https://stackoverflow.com/a/57390408
    y, sr = librosa.load(wav_file)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    # beats now contains the beat *frame positions*
    # convert to timestamps like this:
    beat_times = librosa.frames_to_time(beats, sr=sr)
    return beat_times


def get_downbeat_times(wav_file):
    # https://stackoverflow.com/a/57390408
    y, sr = librosa.load(wav_file)
    # get onset envelope
    onset_env = librosa.onset.onset_strength(y, sr=sr, aggregate=np.median)
    # get tempo and beats
    tempo, beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    # we assume 4/4 time
    meter = 4
    # calculate number of full measures
    measures = (len(beats) // meter)
    # get onset strengths for the known beat positions
    # Note: this is somewhat naive, as the main strength may be *around*
    #       rather than *on* the detected beat position.
    beat_strengths = onset_env[beats]
    # make sure we only consider full measures
    # and convert to 2d array with indices for measure and beatpos
    measure_beat_strengths = beat_strengths[:measures * meter].reshape(-1, meter)
    # add up strengths per beat position
    beat_pos_strength = np.sum(measure_beat_strengths, axis=0)
    # find the beat position with max strength
    downbeat_pos = np.argmax(beat_pos_strength)
    # convert the beat positions to the same 2d measure format
    full_measure_beats = beats[:measures * meter].reshape(-1, meter)
    # and select the beat position we want: downbeat_pos
    downbeat_frames = full_measure_beats[:, downbeat_pos]
    # print('Downbeat frames: {}'.format(downbeat_frames))
    # print times
    downbeat_times = librosa.frames_to_time(downbeat_frames, sr=sr)
    # print('Downbeat times in s: {}'.format(downbeat_times))
    return downbeat_times


def seperate_voice_beat(wav_file):
    # Using embedded configuration.
    separator = Separator("spleeter:2stems")
    separator.separate_to_file(wav_file, "splitted")


def stretch_wav(splitted_vocal_wav, output_file, stretch_factor):
    tfm = sox.Transformer()
    tfm.tempo(stretch_factor)
    tfm.build(splitted_vocal_wav, output_file)


def add_delay(stretched_vcl, output_file, dly):
    tfm = sox.Transformer()
    tfm.delay([dly, dly])
    tfm.build(stretched_vcl, output_file)


def merge_wav(wav_01, wav_02, output_wav):
    cbm = sox.Combiner()
    cbm.build([wav_01, wav_02], output_wav, "mix-power")



if __name__ == '__main__':
    st.title("phonk remix maker")

    beat_col, vocal_col = st.beta_columns(2)
    beat_url = beat_col.text_input("enter beat youtube url", "https://www.youtube.com/watch?v=jMeDA3UbTFU")
    vocal_url = vocal_col.text_input("enter vocals youtube url", "https://www.youtube.com/watch?v=J-Ectj_BPoo")

    # if st.button("download"):
    download_to_wav(beat_url)
    download_to_wav(vocal_url)

    # beat_dl = multiprocessing.Process(target=download_to_wav, args=(beat_url,))
    # vocal_dl = multiprocessing.Process(target=download_to_wav, args=(vocal_url,))
    # beat_dl.start()
    # vocal_dl.start()
    # beat_dl.join()
    # vocal_dl.join()

    beat_yt = YouTube(beat_url)
    vocal_yt = YouTube(vocal_url)

    beat_col.image(beat_yt.thumbnail_url, width=250)
    vocal_col.image(vocal_yt.thumbnail_url, width=250)

    beat_col.subheader(beat_yt.title)
    vocal_col.subheader(vocal_yt.title)

    beat_wav = "beat.wav"
    beat_col.audio(open(beat_wav, "rb").read(), format="audio/wav")
    beat_col.write(beat_wav)

    vocal_wav = "vocals.wav"
    vocal_col.audio(open(vocal_wav, "rb").read(), format="audio/wav")
    vocal_col.write(vocal_wav)

    beat_bpm = detect_bpm(beat_wav)
    vocal_bpm = detect_bpm(vocal_wav)

    beat_col.write(f"bpm: {beat_bpm}")
    vocal_col.write(f"bpm: {vocal_bpm}")

    beat_beat_times = get_beat_times(beat_wav)
    vocal_beat_times = get_beat_times(vocal_wav)

    # beat_col.write(beat_beat_times)
    # vocal_col.write(vocal_beat_times)

    beat_downbeat_times = get_downbeat_times(beat_wav)
    vocal_downbeat_times = get_downbeat_times(vocal_wav)

    beat_col.write(beat_downbeat_times)
    vocal_col.write(vocal_downbeat_times)

    beat_downbeat_num = beat_col.number_input("choose beat first downbeat", 0)
    vocal_downbeat_num = vocal_col.number_input("choose vocal first downbeat", 0)

    seperate_voice_beat(vocal_wav)
    # vocal_col.write("splitted:")
    splitted_vocal_wav = "splitted/vocals/vocals.wav"
    # vocal_col.audio(open(splitted_vocal_wav, "rb").read(), format="audio/wav")
    stretch_factor = beat_bpm / vocal_bpm

    # vocal_col.write(f"stretching vocal by: {stretch_factor}")
    stretched_vocal = "splitted_stretched_vocal.wav"
    stretch_wav(splitted_vocal_wav, stretched_vocal, stretch_factor)
    # vocal_col.write(stretched_vocal)
    # vocal_col.audio(open(stretched_vocal, "rb").read(), format="audio/wav")
    stretched_vocal_downbeat_times = [x * stretch_factor for x in vocal_downbeat_times]

    delay = beat_downbeat_times[beat_downbeat_num] - stretched_vocal_downbeat_times[vocal_downbeat_num]
    vocal_col.write(f"delay: {delay}")
    delayed_vocal = "delayed_vocal.wav"
    add_delay(stretched_vocal, delayed_vocal, delay)
    # vocal_col.write(delayed_vocal)
    # vocal_col.audio(open(delayed_vocal, "rb").read(), format="audio/wav")

    merged_wav = "merged.wav"
    merge_wav(beat_wav, delayed_vocal, merged_wav)
    st.subheader(merged_wav)
    st.audio(open(merged_wav, "rb").read(), format="audio/wav")
