#!/usr/bin/env python
# coding: utf-8

import numpy as np
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

def simpleMovingAverage(data, window=100):

    unit = np.ones(window) / window
    smas = np.convolve(data, unit, mode="same") # 移動平均
    return smas

def run(fileName, figName, window, vadThreshold, minNoiseLevel):

    rawWAV, frameRate = ReadWavFile(fileName=fileName)
    rawWAV = np.abs(rawWAV)

    smas = simpleMovingAverage(data=rawWAV, window=window)
    smaMax = np.max(smas)
    threshold = smaMax * vadThreshold

    isSilent = False
    noiseLevel = (smaMax - np.min(smas)) * np.mean(smas)

    if noiseLevel < minNoiseLevel:
        startFrame = 0.0
        endFrame = 0.0
        isSilent = True
    else:
        for index, sma in enumerate(smas):
            if sma >= threshold:
                startFrame = index
                break

        for index, sma in enumerate(smas[::-1]):
            if sma >= threshold:
                endFrame = smas.size - index
                break

    startTime = startFrame / frameRate
    endTime = endFrame / frameRate
    interval = endTime - startTime

    times = np.linspace(0, rawWAV.size / frameRate, num=rawWAV.size)

    plt.figure(figsize=(12, 10))

    plt.plot(times, rawWAV, label="Raw WAV")
    plt.plot(times, smas, "r", label="SMA")

    if not isSilent:
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
    vadThreshold = sys.argv[3]

    startTime, endTime, interval = run(fileName=fileName, figName=figName, vadThreshold=vadThreshold)

    print("%f,%f,%f" % (startTime, endTime, interval))
