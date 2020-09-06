#!/usr/bin/env python
# coding: utf-8

import pyaudio  # 録音機能を使うためのライブラリ
import wave     # wavファイルを扱うためのライブラリ


# RECORD_SECONDS = 5.0 # 録音する時間の長さ（秒）
iDeviceIndex = 0 # 録音デバイスのインデックス番号

# 基本情報の設定
FORMAT = pyaudio.paInt16 # 音声のフォーマット
CHANNELS = 1             # モノラル
RATE = 16000            # サンプルレート
CHUNK = 2**11            # データ点数


def recording(fileName, recordSeconds):

    audio = pyaudio.PyAudio() # pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        input_device_index=iDeviceIndex, # 録音デバイスのインデックス番号
                        frames_per_buffer=CHUNK)

    #--------------録音開始---------------

    print("recording...")
    frames = []
    for i in range(0, int(RATE / CHUNK * recordSeconds)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("finished recording")

    #--------------録音終了---------------

    stream.stop_stream()
    stream.close()
    audio.terminate()

    waveFile = wave.open(fileName, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()


if __name__ == "__main__":

    import os
    import sys

    # scriptフォルダをパスに追加
    sd = os.path.dirname(__file__)
    sys.path.append(sd)

    if not os.path.isdir("../temp"):
        os.mkdir("../temp")

    recording("../temp/record.wav", 5.0)
