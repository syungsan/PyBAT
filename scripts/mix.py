#!/usr/bin/env python
# coding: utf-8

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import wave
import gc
import python_speech_features as psf
from scipy import interpolate
import scipy.ndimage


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

def getMfcc(sigs, rate):

    mfccs = psf.mfcc(sigs, rate)
    deltas = psf.delta(mfccs, 2)
    mfccFeatures = np.c_[mfccs, deltas]

    return mfccFeatures

def getVadFluctuation(mfccPowers, deltaPowers, filterWidth=10):

    mfccPowers[mfccPowers < 0] = 0
    deltaPowers = np.abs(deltaPowers)

    y = mfccPowers * deltaPowers
    y = scipy.ndimage.gaussian_filter(y, filterWidth)

    return y

def run(fileName, figName, smaThresholdRate=0.1, smaWindowSize=100, minNoiseLevel=1.0):

    isSilent = False

    wavs, frameRate = ReadWavFile(fileName=fileName)

    powers = wavs ** 2 # 信号のパワー
    mfccs = getMfcc(wavs, frameRate)

    dataLength = len(mfccs)
    mfccPowers = mfccs[:, 0]
    deltaPowers = mfccs[:, 13]

    # Voice active detection
    x_observed = np.arange(0, dataLength, 1)  # 時間軸
    y_observed = getVadFluctuation(mfccPowers, deltaPowers)

    method = lambda x, y: interpolate.interp1d(x, y, kind="cubic")
    fitted_curve = method(x_observed, y_observed)

    x_latents = np.linspace(min(x_observed), max(x_observed), len(powers))
    fitted_curves = fitted_curve(x_latents).tolist()

    vads = fitted_curves * powers
    smas = simpleMovingAverage(datas=vads, window=smaWindowSize)

    smaMax = np.max(smas)
    threshold = smaMax * smaThresholdRate # 閾値

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

        times = np.linspace(0, vads.size / frameRate, num=vads.size)

        plt.figure(figsize=(12, 10))
        plt.plot(times, vads, label="MixPower")
        plt.plot(times, smas, "r", label="SMA")

        if not isSilent:

            # plt.axhline(y=meanDb, xmin=0, xmax=1, color="gray", linewidth=2)
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

    startTime, endTime, interval = run(fileName=fileName, figName=figName)

    print("%f,%f,%f" % (startTime, endTime, interval))
