#!/usr/bin/env python
# coding: utf-8

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plot

import numpy as np
import python_speech_features as psf
import scipy
import scipy.io
import scipy.io.wavfile
import scipy.ndimage
import scipy.signal


def getMfcc(fileName):
    (rate, sig) = scipy.io.wavfile.read(fileName)
    mfcc = psf.mfcc(sig, rate)
    delta = psf.delta(mfcc, 2)
    deltaDelta = psf.delta(delta, 2)
    mfccFeature = np.c_[mfcc, delta, deltaDelta]
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


def run(fileName, figName):

    # defines
    vadThreshold = 2 # 3

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

    # plot data
    mfccHeatmap = mfcc[:, np.arange(1, 13)].T

    # max len
    xlim = [0, dataLength]

    plot.style.use('classic')
    plot.figure(figsize=(12, 10))
    # heatmap
    plot.subplot(5, 1, 1)
    plot.xlim(xlim)
    #plot.heatmap(heatmap)
    plot.pcolor(mfccHeatmap, cmap=plot.cm.Blues)

    # power, delta
    plot.subplot(5, 1, 2)
    plot.xlim(xlim)
    plot.plot(mfccPower)
    plot.plot(deltaPower)

    # vad
    plot.subplot(5, 1, 3)
    plot.xlim(xlim)
    plot.plot(vad)
    sx = np.where(vadPeekMin == 1)[0]
    sy = vad[sx]
    plot.scatter(sx, sy, c="blue")
    sx = np.where(vadPeekMax == 1)[0]
    sy = vad[sx]
    plot.scatter(sx, sy, c="red")
    yline = [vadThreshold] * dataLength
    plot.plot(yline)

    # mora
    plot.subplot(5, 1, 4)
    plot.xlim(xlim)
    plot.plot(mora)
    sx = np.where(moraPeekMin == 1)[0]
    sy = mora[sx]
    plot.scatter(sx, sy, c="blue")
    sx = np.where(moraPeekMax == 1)[0]
    sy = mora[sx]
    plot.scatter(sx, sy, c="red")

    # vad
    plot.subplot(5, 1, 5)
    plot.xlim(xlim)
    plot.plot(vadSection)
    sx = np.where(moraPositions == 1)[0]
    sy = np.ones(len(sx))
    plot.scatter(sx, sy)
    #vadSection
    #moraPositions

    plot.savefig(figName)

    calcIntervals = []
    for i in range(len(vadSection)):

        if vadSection[i] == 1:
            calcIntervals.append(i)

    startTime = 0.0
    endTime = 0.0
    interval = 0.0

    if len(calcIntervals) > 0:

        startTime = calcIntervals[0] / 100.0
        endTime = calcIntervals[-1] / 100.0
        interval = endTime - startTime

    return startTime, endTime, interval


if __name__ == "__main__":

    import os
    import sys

    # scriptフォルダをパスに追加
    sd = os.path.dirname(__file__)
    sys.path.append(sd)

    import record as rec

    if not os.path.isdir("../temp"):
        os.mkdir("../temp")

    rec.recording("../temp/sample.wav", 5.0)
    run("../temp/sample.wav", "../temp/fig.png")

"""
python analize.py
"""
