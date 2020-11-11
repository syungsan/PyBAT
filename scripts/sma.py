#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import wave
import gc


def ReadWavFile(fileName):

    try:
        wr = wave.open(fileName, "r")
    except FileNotFoundError: #ファイルが存在しなかった場合
        print("[Error 404] No such file or directory: " + fileName)
        return 0

    framerate = wr.getframerate()

    data = wr.readframes(wr.getnframes())
    wr.close()

    x = np.frombuffer(data, dtype="int16") / float((2 ^ 15))
    return x, framerate

def simpleMovingAverage(datas, window):

    unit = np.ones(window) / window
    smas = np.convolve(datas, unit, mode="same") # 移動平均

    return smas

def run(fileName, figName, thresholdRate=0.1, windowSize=100, minNoiseLevel=1.0):

    isSilent = False

    wavs, frameRate = ReadWavFile(fileName=fileName)
    powers = wavs ** 2 # 信号のパワー

    smas = simpleMovingAverage(datas=powers, window=windowSize)

    smaMax = np.max(smas)
    threshold = smaMax * thresholdRate # 閾値

    # 平均音量（db）
    meanDb = 10 * np.log10(np.mean(powers))

    if meanDb < minNoiseLevel:

        startTime = "Input Low"
        endTime = "Input Low"
        interval = "Input Low"

        isSilent = True
    else:
        upIdx = [i for i, v in enumerate(smas > threshold) if v]
        predStart, predEnd = upIdx[0], upIdx[-1]

        startTime = predStart / frameRate
        endTime = predEnd / frameRate
        interval = endTime - startTime

    if figName != "":

        times = np.linspace(0, powers.size / frameRate, num=powers.size)

        plt.figure(figsize=(12, 10))
        plt.plot(times, powers, label="Power")
        plt.plot(times, smas, "r", label="SMA")

        if not isSilent:

            plt.axhline(y=meanDb, xmin=0, xmax=1, color="gray", linewidth=2)
            plt.axhline(y=threshold, xmin=0, xmax=1, color="pink", linewidth=2)
            plt.axvline(ymin=0, ymax=1, x=startTime, color="green", linewidth=2)
            plt.axvline(ymin=0, ymax=1, x=endTime, color="yellow", linewidth=2)

        plt.legend()
        plt.savefig(figName)
        # plt.show()

        # ■■■ 追加 ■■■
        plt.cla()
        plt.clf()
        plt.close()
        gc.collect()

    return startTime, endTime, interval


if __name__ == "__main__":

    import sys

    fileName = sys.argv[1]
    figName = sys.argv[2]
    thresholdRate = sys.argv[3]

    startTime, endTime, interval = run(fileName=fileName, figName=figName, vadThreshold=thresholdRate)

    print("%f,%f,%f" % (startTime, endTime, interval))
