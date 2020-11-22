#!/usr/bin/env python
# coding: utf-8

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import gc

import numpy as np
import python_speech_features as psf
import scipy
import scipy.io
import scipy.io.wavfile
import scipy.ndimage
import scipy.signal


# python_speech_featuresのmfccメソッド
# ========================================================================
# def mfcc(signal,samplerate=16000,winlen=0.025,winstep=0.01,numcep=13,
#                  nfilt=26,nfft=512,lowfreq=0,highfreq=None,preemph=0.97,
#      ceplifter=22,appendEnergy=True)
# ========================================================================
# Defaultでウィンドウレンジ25msおよびシフト幅10ms（解像度1/100秒）

# ここでのΔ量とは
# 隣接スペクトルの差分 ×
# 回帰係数 〇
# であり子音の特徴を捉えるのに有効

def getMfcc(fileName):
    (rate, sig) = scipy.io.wavfile.read(fileName)
    mfcc = psf.mfcc(sig, rate)
    delta = psf.delta(mfcc, 2)
    # deltaDelta = psf.delta(delta, 2)
    # mfccFeature = np.c_[mfcc, delta, deltaDelta]
    mfccFeature = np.c_[mfcc, delta]
    return mfccFeature


def getVadFluctuation(mfccPower, deltaPower, filterWidth=10):
    mfccPower[mfccPower < 0] = 0
    deltaPower = np.abs(deltaPower)
    y = mfccPower * deltaPower
    y = scipy.ndimage.gaussian_filter(y, filterWidth)
    minId = scipy.signal.argrelmin(y, order=1)
    minPeek = np.zeros(len(y))
    minPeek[minId] = 1
    maxId = scipy.signal.argrelmax(y, order=1)
    maxPeek = np.zeros(len(y))
    maxPeek[maxId] = 1
    return y, minPeek, maxPeek


def getMoraFlactuation(mfccPower, deltaPower, filterWidth=4):
    y = mfccPower * deltaPower
    y = scipy.ndimage.gaussian_filter(deltaPower, filterWidth)
    minId = scipy.signal.argrelmin(y, order=1)
    minPeek = np.zeros(len(y))
    minPeek[minId] = 1
    maxId = scipy.signal.argrelmax(y, order=1)
    maxPeek = np.zeros(len(y))
    maxPeek[maxId] = 1
    return y, minPeek, maxPeek


def run(fileName, figName, vadThreshold):

    # defines
    # vadThreshold = 2 # 3

    # MFCC取得
    mfcc = getMfcc(fileName)
    dataLength = len(mfcc)
    mfccPower = mfcc[:, 0]
    deltaPower = mfcc[:, 13]

    # Voice active detection
    vad, vadPeekMin, vadPeekMax = getVadFluctuation(mfccPower, deltaPower)

    # mora
    mora, moraPeekMin, moraPeekMax = getMoraFlactuation(mfccPower, deltaPower)

    # voice active detection
    vadSection = np.zeros(dataLength)
    vadSection[vad >= vadThreshold] = 1
    moraPositions = np.zeros(dataLength)
    moraPositions[np.where(moraPeekMax == 1)] = 1
    moraPositions[vad <= vadThreshold] = 0

    if figName != "":

        # plot data
        mfccHeatmap = mfcc[:, np.arange(1, 13)].T

        # max len
        xlim = [0, dataLength]

        plt.style.use('classic')
        plt.figure(figsize=(12, 10))
        # heatmap
        plt.subplot(5, 1, 1)
        plt.xlim(xlim)
        # plot.heatmap(heatmap)
        plt.pcolor(mfccHeatmap, cmap=plt.cm.Blues)

        # power, delta
        plt.subplot(5, 1, 2)
        plt.xlim(xlim)
        plt.plot(mfccPower)
        plt.plot(deltaPower)

        # vad
        plt.subplot(5, 1, 3)
        plt.xlim(xlim)
        plt.plot(vad)
        sx = np.where(vadPeekMin == 1)[0]
        sy = vad[sx]
        plt.scatter(sx, sy, c="blue")
        sx = np.where(vadPeekMax == 1)[0]
        sy = vad[sx]
        plt.scatter(sx, sy, c="red")
        yline = [vadThreshold] * dataLength
        plt.plot(yline)

        # mora
        plt.subplot(5, 1, 4)
        plt.xlim(xlim)
        plt.plot(mora)
        sx = np.where(moraPeekMin == 1)[0]
        sy = mora[sx]
        plt.scatter(sx, sy, c="blue")
        sx = np.where(moraPeekMax == 1)[0]
        sy = mora[sx]
        plt.scatter(sx, sy, c="red")

        # vad
        plt.subplot(5, 1, 5)
        plt.xlim(xlim)
        plt.plot(vadSection)
        sx = np.where(moraPositions == 1)[0]
        sy = np.ones(len(sx))
        plt.scatter(sx, sy)
        # vadSection
        # moraPositions

        plt.savefig(figName)

        # ■■■ 追加 ■■■
        plt.cla()
        plt.clf()
        plt.close()
        gc.collect()

    calcIntervals = []
    for i in range(len(vadSection)):

        if vadSection[i] == 1:
            calcIntervals.append(i)

    if len(calcIntervals) > 0:

        startTime = calcIntervals[0] / 100.0
        endTime = calcIntervals[-1] / 100.0
        interval = endTime - startTime

    else:
        startTime = "Input Low"
        endTime = "Input Low"
        interval = "Input Low"

    return startTime, endTime, interval


if __name__ == "__main__":

    import sys

    fileName = sys.argv[1]
    figName = sys.argv[2]
    vadThreshold = sys.argv[3]

    startTime, endTime, interval = run(fileName=fileName, figName=figName, vadThreshold=vadThreshold)

    print("%f,%f,%f" % (startTime, endTime, interval))

"""
python mfcc.py
"""
