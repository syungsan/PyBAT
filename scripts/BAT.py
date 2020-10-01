#!/usr/bin/env python
# coding: utf-8

# Build Command

# Mac
# rm -rf dist/ build/
# ./venv/bin/python setup.py py2app --packages=PIL

# Windows
# del /s dist build
# .\venv\python -m PyInstaller .\BAT.py --noconsole --onefile --icon=.\data\Thesquid.ink-Free-Flat-Sample-Support.ico

import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from datetime import datetime
import threading
import glob
import shutil
import time

import record
import sma
import excel
import mfcc
import item

APPLICATION_NAME = "BAT"
VERSION_NUMBER = "0.9.1"

INPUT_DIALOG_SIZE = [320, 170]
WINDOW_SIZE = [1280, 720]

KIND_OF_TEST_STRINGS = ["Test1", "Test2", "Test3"]
ANALIZE_METHOD_STRINGS = ["SMA", "MFCC"]
DEFAULT_ANALYZE_METHOD = "SMA"
DEFAULT_IS_MAKE_FIGURE = False

WORDS = [["い", "は", "も", "へ", "こ", "や", "う"],
         ["つ", "さ", "ひ", "く", "え", "し", "み"],
         ["け", "お", "め", "", "ぬ", "と", "て"],
         ["ら", "せ", "て", "", "り", "か", "む"],
         ["そ", "ち", "ふ", "ち", "す", "ろ", "ね"],
         ["の", "よ", "ま", "あ", "ゆ", "き", "れ"]]

READS = ["か", "は", "き", "せ", "つ", "と", "こ", "ふ",
         "け", "し", "ら", "れ", "え", "そ", "お", "よ",
         "ね", "ゆ", "ひ", "む", "さ", "や", "も", "み",
         "ち", "う", "す", "の", "ま", "て", "ろ", "い"]

EXCEPTION = [3, 10, 16, 17, 18, 23, 24, 25, 31, 38]

BOX_POSITIONS = [7, 35, 21, 19, 41, 15, 0, 13, 34, 33, 8, 12, 15, 39, 36, 39, 9, 1, 30, 30, 11, 39, 39, 27, 40, 41, 19, 20, 2, 7, 9, 5]
ELLIPSE_POSITIONS = [11, 33, 6, 7, 4, 41, 32, 32, 5, 22, 12, 14, 21, 12, 4, 2, 28, 13, 20, 6, 34, 36, 20, 22, 0, 2, 37, 9, 40, 22, 20, 27]
STAR_POSITIONS = [36, 6, 8, 34, 36, 35, 21, 1, 37, 7, 27, 28, 32, 8, 41, 13, 11, 28, 26, 14, 30, 0, 28, 1, 12, 36, 0, 41, 4, 26, 21, 28]
RED_NUMBERS = [0, 2, 2, 0, 0, 2, 0, 0, 2, 1, 2, 2, 1, 1, 2, 0, 0, 2, 2, 2, 0, 2, 0, 2, 2, 1, 1, 0, 2, 1, 0, 0]

X_PADDING_MARGIN_RATIO = 0.01
Y_PADDING_MARGIN_RATIO = 0.01

# 中央の段差
CENTER_SPAN_RATIO = 0.1

WORD_FONT_SIZE_RATIO = 0.6

CROSS_SIZE_RATIO = 3.0
BOX_SIZE_RATIO = 1.5
ELLIPSE_SIZE_RATIO = 1.7
STAR_SIZE_RATIO = 2.0

PROGRESS_LIMIT = 100

MFCC_VAD_THRESHOLD = 3.0
SMA_WINDOW_SIZE = 100
SMA_VAD_THRESHOLD = 0.1
SMA_MIN_NOISE_LEVEL = 1.0

DEFAULT_USER_NAME = "Test"

if os.name == "nt":

    DEFAULT_FONT_NAME = "Meiryo"
    DEFAULT_LOG_LOCATION = os.getcwd().replace("\\scripts", "") + "\\log"

    if not os.path.exists(DEFAULT_LOG_LOCATION):
        os.mkdir(DEFAULT_LOG_LOCATION)
else:
    DEFAULT_FONT_NAME = "Hiragino Sans"
    DEFAULT_LOG_LOCATION = os.path.expanduser("~") + "/Documents"


class TitleScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.name = "TitleScene"

        self.titleLabel = QGraphicsSimpleTextItem()
        self.titleLabel.setText(APPLICATION_NAME)
        self.titleLabel.setPen(QPen(Qt.black, 1))
        self.titleLabel.setBrush(Qt.black)
        self.addItem(self.titleLabel)

        self.versionNumberLabel = QGraphicsSimpleTextItem()
        self.versionNumberLabel.setText("Ver " + str(VERSION_NUMBER))
        self.versionNumberLabel.setPen(QPen(Qt.black, 1))
        self.versionNumberLabel.setBrush(Qt.black)
        self.addItem(self.versionNumberLabel)

        self.analyzeMethodLabel = QGraphicsSimpleTextItem()
        self.analyzeMethodLabel.setText("Analyze Method")
        self.analyzeMethodLabel.setPen(QPen(Qt.black, 1))
        self.analyzeMethodLabel.setBrush(Qt.black)
        self.addItem(self.analyzeMethodLabel)

        self.analyzeMethodRadioButtons = []
        self.group = QButtonGroup()

        for analyzeMethodString in ANALIZE_METHOD_STRINGS:

            analyzeMethodRadioButton = QRadioButton(analyzeMethodString)
            analyzeMethodRadioButton.setCheckable(True)

            analyzeMethodRadioButton.setFocusPolicy(Qt.NoFocus)
            analyzeMethodRadioButton.toggled.connect(self.onClickedAnalyzeingMethodRadioButton)

            self.group.addButton(analyzeMethodRadioButton)
            self.addWidget(analyzeMethodRadioButton)
            self.analyzeMethodRadioButtons.append(analyzeMethodRadioButton)

            if analyzeMethodRadioButton.text() == DEFAULT_ANALYZE_METHOD:
                analyzeMethodRadioButton.setChecked(True)

        self.testButtons = []

        for kindOfTestString in KIND_OF_TEST_STRINGS:

            testButton = QPushButton(kindOfTestString)
            testButton.clicked.connect(self.onClickedTestButton)
            self.addWidget(testButton)
            self.testButtons.append(testButton)

        self.toolInfoLabel = QGraphicsSimpleTextItem()
        self.toolInfoLabel.setText("Powered by Python.")
        self.toolInfoLabel.setPen(QPen(Qt.black, 1))
        self.toolInfoLabel.setBrush(Qt.black)
        self.addItem(self.toolInfoLabel)

        self.copyrightLabel = QGraphicsSimpleTextItem()
        self.copyrightLabel.setText("Copyright © 2020 Shimane University. All Right Reserved.")
        self.copyrightLabel.setPen(QPen(Qt.black, 1))
        self.copyrightLabel.setBrush(Qt.black)
        self.addItem(self.copyrightLabel)

        self.makeFigCheckBox = QCheckBox("Make Figure")
        self.makeFigCheckBox.stateChanged.connect(self.makeFigCheckBoxChangedAction)
        self.makeFigCheckBox.setChecked(DEFAULT_IS_MAKE_FIGURE)
        self.addWidget(self.makeFigCheckBox)

    def setPosAndSize(self, frameSize):

        self.setSceneRect(0, 0, frameSize.width(), frameSize.height())

        aspectRatio = 16 / 9

        if self.width() / self.height() >= aspectRatio:
            unitRatio = self.height() * (1 / 9)
        else:
            unitRatio = self.width() * (1 / 16)

        self.titleLabel.setFont(QFont(DEFAULT_FONT_NAME, int(unitRatio * 1.0)))
        self.titleLabel.setPos((self.width() - self.titleLabel.boundingRect().width()) * 0.5, (self.height() - self.titleLabel.boundingRect().height()) * 0.1)

        self.versionNumberLabel.setFont(QFont(DEFAULT_FONT_NAME, int(unitRatio * 0.2)))
        self.versionNumberLabel.setPos(self.titleLabel.x() + self.titleLabel.boundingRect().width() - self.versionNumberLabel.boundingRect().width(), self.titleLabel.y() + self.titleLabel.boundingRect().height())

        self.analyzeMethodLabel.setFont(QFont(DEFAULT_FONT_NAME, int(unitRatio * 0.2)))
        self.analyzeMethodLabel.setPos((self.width() - self.analyzeMethodLabel.boundingRect().width()) * 0.5, (self.height() - self.analyzeMethodLabel.boundingRect().height()) * 0.4)

        for index, analyzeMethodRadioButton in enumerate(self.analyzeMethodRadioButtons):

            analyzeMethodRadioButtonFontSize = int(unitRatio * 0.2)
            analyzeMethodRadioButton.setFont(QFont(DEFAULT_FONT_NAME, analyzeMethodRadioButtonFontSize))

            analyzeMethodRadioButtonWidth = analyzeMethodRadioButtonFontSize * 5
            analyzeMethodRadioButtonHeight = int(analyzeMethodRadioButtonFontSize * 1.4)

            analyzeMethodRadioButton.setMaximumWidth(analyzeMethodRadioButtonWidth)
            analyzeMethodRadioButton.setMaximumHeight(analyzeMethodRadioButtonHeight)
            analyzeMethodRadioButton.setGeometry(0, 0, analyzeMethodRadioButtonWidth, analyzeMethodRadioButtonHeight)

            analyzeMethodRadioButton.move(int((self.width() - analyzeMethodRadioButton.width()) * 0.5), int(self.height() * 0.4 + (self.height() * 0.2 - analyzeMethodRadioButton.height()) * 0.2 * (index + 1)))

        for index, testButton in enumerate(self.testButtons):

            testButtonFontSize = int(unitRatio * 0.2)
            testButton.setFont(QFont(DEFAULT_FONT_NAME, testButtonFontSize))

            testButtonWidth = len(KIND_OF_TEST_STRINGS[index]) * testButtonFontSize
            testButtonHeight = testButtonFontSize * 2

            testButton.setMaximumWidth(testButtonWidth)
            testButton.setMaximumHeight(testButtonHeight)
            testButton.setGeometry(0, 0, testButtonWidth, testButtonHeight)

            testButton.move(int(self.width() * 0.15 + (self.width() * 0.7 - testButton.width()) * 0.25 * (index + 1)), int((self.height() - testButton.height()) * 0.7))

        self.toolInfoLabel.setFont(QFont(DEFAULT_FONT_NAME, int(unitRatio * 0.2)))
        self.toolInfoLabel.setPos((self.width() - self.toolInfoLabel.boundingRect().width()) * 0.5, (self.height() - self.toolInfoLabel.boundingRect().height()) * 0.85)

        self.copyrightLabel.setFont(QFont(DEFAULT_FONT_NAME, int(unitRatio * 0.2)))
        self.copyrightLabel.setPos((self.width() - self.copyrightLabel.boundingRect().width()) * 0.5, (self.height() - self.copyrightLabel.boundingRect().height()) * 0.9)

        makeFigCheckBoxFontSize = int(unitRatio * 0.2)
        self.makeFigCheckBox.setFont(QFont(DEFAULT_FONT_NAME, makeFigCheckBoxFontSize))

        makeFigCheckBoxWidth = makeFigCheckBoxFontSize * 9
        makeFigCheckBoxHeight = int(makeFigCheckBoxFontSize * 1.4)

        self.makeFigCheckBox.setMaximumWidth(makeFigCheckBoxWidth)
        self.makeFigCheckBox.setMaximumHeight(makeFigCheckBoxHeight)
        self.makeFigCheckBox.setGeometry(0, 0, makeFigCheckBoxWidth, makeFigCheckBoxHeight)

        self.makeFigCheckBox.move(int((self.width() - self.makeFigCheckBox.width()) * 0.5), int((self.height() - self.makeFigCheckBox.height()) * 0.55))

    def onClickedAnalyzeingMethodRadioButton(self):

        analyzeMethodRadioButton = self.sender()

        if analyzeMethodRadioButton is None or not isinstance(analyzeMethodRadioButton, QRadioButton):
            return

        if analyzeMethodRadioButton.isChecked():
            self.parent().analyzeMethod = analyzeMethodRadioButton.text()

    def onClickedTestButton(self):
        self.parent().sceneManager(mode=self.sender().text())

    def makeFigCheckBoxChangedAction(self, state):

        if (Qt.Checked == state):
            self.parent().isMakeFig = True
        else:
            self.parent().isMakeFig = False


class RecordingThread(QThread):

    recordSignal = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self):
        self.recordSignal.emit()
        self.finished.emit()


class TestScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.wordItems = []

        self.makeBaseLayer()
        self.makeWordGrid()
        self.makeItem()

        self.name = "TestScene"
        self.mode = ""

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(int(1 / 60 * 1000))

        self.logDir = ""
        self.wavPath = ""

        self.recTime = 0.0
        self.recordThread = RecordingThread()
        self.recordThread.recordSignal.connect(self.thread)

        self.showWordIndex = 0

    def setLogDir(self, logDir):

        self.logDir = logDir
        dataDir = "%s/wavs" % self.logDir

        if not os.path.isdir(dataDir):
            os.mkdir(dataDir)

    def thread(self):
        thread = threading.Thread(target=self.record)
        thread.start()

    def record(self):
        record.recording(self.wavPath, self.recTime)

    def makeBaseLayer(self):

        self.baseLayer = item.BoxGraphicsItem(rect=QRectF(0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1]), color=Qt.white)
        self.addItem(self.baseLayer)

    def makeWordGrid(self):

        for i in range(len(WORDS)):
            for j in range(len(WORDS[i])):

                wordItem = item.TextGraphicsSimpleTextItem(text=WORDS[i][j], size=10.5, fontType=DEFAULT_FONT_NAME)

                self.addItem(wordItem)
                self.wordItems.append(wordItem)
                wordItem.hide()

    def makeItem(self):

        self.crossItem = item.CrossGraphicsItem(size=30, lineWidth=3.0, color=Qt.black)
        self.addItem(self.crossItem)

        self.boxItem = item.BoxGraphicsItem(rect=QRectF(0, 0, 10.5, 10.5), color=Qt.black)
        self.addItem(self.boxItem)
        self.boxItem.hide()

        self.ellipseItem = item.EllipseGraphicsItem(radius=5.25, color=Qt.black)
        self.addItem(self.ellipseItem)
        self.ellipseItem.hide()

        self.starItem = item.StarGraphicsItem(center=QPointF(5.25, 5.25), radius=5.25, color=Qt.black)
        self.addItem(self.starItem)
        self.starItem.hide()

    def setPosAndSize(self, frameSize):

        self.setSceneRect(0, 0, frameSize.width(), frameSize.height())

        aspectRatio = 16 / 9

        if self.width() / self.height() >= aspectRatio:
            unitRatio = self.height() * (1 / 9)
        else:
            unitRatio = self.width() * (1 / 16)

        self.baseLayer.rect = self.sceneRect()

        xPaddingMargin = self.baseLayer.rect.width() * X_PADDING_MARGIN_RATIO
        yPaddingMargin = self.baseLayer.rect.height() * Y_PADDING_MARGIN_RATIO

        wordFontSize = unitRatio * WORD_FONT_SIZE_RATIO

        centerSpan = self.baseLayer.rect.height() * CENTER_SPAN_RATIO
        yOneLength = (self.baseLayer.rect.height() - (yPaddingMargin * 2.0) - centerSpan) / len(WORDS)

        yPos = 0

        k = 0
        for i in range(len(WORDS)):

            if i == 0:
                yPos = 0
            elif i != len(WORDS) / 2:
                yPos += yOneLength
            else:
                yPos += yOneLength + centerSpan

            xOneLength = (self.baseLayer.rect.width() - (xPaddingMargin * 2.0)) / len(WORDS[i])

            for j in range(len(WORDS[i])):

                self.wordItems[k].setFont(QFont(DEFAULT_FONT_NAME, int(wordFontSize)))

                self.wordItems[k].setPos(xOneLength * j + xPaddingMargin - (self.wordItems[k].width() * 0.5) + (xOneLength * 0.5),
                                yPos + yPaddingMargin - (self.wordItems[k].height() * 0.5) + (yOneLength * 0.5))

                k += 1

        self.crossItem.size = wordFontSize * CROSS_SIZE_RATIO
        self.crossItem.lineWidth = wordFontSize * 0.3
        self.crossItem.setPos((self.baseLayer.rect.width() - self.crossItem.width()) * 0.5, (self.baseLayer.rect.height() - self.crossItem.height()) * 0.5)

        self.boxItem.rect = QRectF(0, 0, wordFontSize * BOX_SIZE_RATIO, wordFontSize * BOX_SIZE_RATIO)

        self.ellipseItem.radius = wordFontSize * ELLIPSE_SIZE_RATIO * 0.5

        self.starItem.center = QPointF(wordFontSize * STAR_SIZE_RATIO * 0.5, wordFontSize * STAR_SIZE_RATIO * 0.5)
        self.starItem.radius = wordFontSize * STAR_SIZE_RATIO * 0.5

        self.boxItem.setPos(self.wordItems[BOX_POSITIONS[self.showWordIndex]].x() - ((self.boxItem.rect.width() - self.wordItems[BOX_POSITIONS[self.showWordIndex]].width()) * 0.5), self.wordItems[BOX_POSITIONS[self.showWordIndex]].y() - ((self.boxItem.rect.height() - self.wordItems[BOX_POSITIONS[self.showWordIndex]].height()) * 0.5))
        self.ellipseItem.setPos(self.wordItems[ELLIPSE_POSITIONS[self.showWordIndex]].x() - ((self.ellipseItem.width() - self.wordItems[ELLIPSE_POSITIONS[self.showWordIndex]].width()) * 0.5), self.wordItems[ELLIPSE_POSITIONS[self.showWordIndex]].y() - ((self.ellipseItem.height() - self.wordItems[ELLIPSE_POSITIONS[self.showWordIndex]].height()) * 0.5))
        self.starItem.setPos(self.wordItems[STAR_POSITIONS[self.showWordIndex]].x() - ((self.starItem.width() - self.wordItems[STAR_POSITIONS[self.showWordIndex]].width()) * 0.5), self.wordItems[STAR_POSITIONS[self.showWordIndex]].y() - ((self.starItem.height() - self.wordItems[STAR_POSITIONS[self.showWordIndex]].height()) * 0.5))

    def changeProcess(self):

        if self.timer.isActive():
            self.timer.stop()

        self.scheduleTimer = 0
        self.showWordIndex = 0
        self.showCount = 0

        if self.process == "Start":
            for wordItem in self.wordItems:
                wordItem.hide()

        if self.process == "Test":
            if self.mode == "Test2":
                for wordItem in self.wordItems:
                    wordItem.show()

        if self.process == "End":
            for wordItem in self.wordItems:
                wordItem.hide()

        if self.process == "Result":
            self.parent().sceneManager(mode="Result")
        else:
            self.timer.start()

    def update(self):

        if self.process == "Start":
            self.start()

        elif self.process == "Test":

            if self.mode == "Test1":
                self.test1()
            elif self.mode == "Test2":
                self.test2()
            elif self.mode == "Test3":
                self.test3()

        elif self.process == "End":
            self.end()

    def start(self):

        if self.scheduleTimer >= 300:

            self.process = "Test"
            self.changeProcess()
        else:
            self.scheduleTimer += 1

    def test1(self):

        if self.scheduleTimer == 0:

            self.recordThread.start()

            k = 0
            for i in range(len(WORDS)):
                for j in range(len(WORDS[i])):

                    if READS[self.showWordIndex] == WORDS[i][j] and not k in EXCEPTION:

                        self.wordItems[k].show()
                        self.showCount = k

                        self.wavPath = "%s/wavs/test1_%s_%s.wav" % (self.logDir, "%02d" % self.showWordIndex, READS[self.showWordIndex])
                        self.recTime = 3.5

                        self.boxItem.setPos(self.wordItems[BOX_POSITIONS[self.showWordIndex]].x() - ((self.boxItem.rect.width() - self.wordItems[BOX_POSITIONS[self.showWordIndex]].width()) * 0.5), self.wordItems[BOX_POSITIONS[self.showWordIndex]].y() - ((self.boxItem.rect.height() - self.wordItems[BOX_POSITIONS[self.showWordIndex]].height()) * 0.5))
                        self.ellipseItem.setPos(self.wordItems[ELLIPSE_POSITIONS[self.showWordIndex]].x() - ((self.ellipseItem.width() - self.wordItems[ELLIPSE_POSITIONS[self.showWordIndex]].width()) * 0.5), self.wordItems[ELLIPSE_POSITIONS[self.showWordIndex]].y() - ((self.ellipseItem.height() - self.wordItems[ELLIPSE_POSITIONS[self.showWordIndex]].height()) * 0.5))
                        self.starItem.setPos(self.wordItems[STAR_POSITIONS[self.showWordIndex]].x() - ((self.starItem.width() - self.wordItems[STAR_POSITIONS[self.showWordIndex]].width()) * 0.5), self.wordItems[STAR_POSITIONS[self.showWordIndex]].y() - ((self.starItem.height() - self.wordItems[STAR_POSITIONS[self.showWordIndex]].height()) * 0.5))

                        self.boxItem.color = Qt.black
                        self.ellipseItem.color = Qt.black
                        self.starItem.color = Qt.black

                        self.boxItem.show()
                        self.ellipseItem.show()
                        self.starItem.show()

                        if RED_NUMBERS[self.showWordIndex] == 0:
                            self.boxItem.color = Qt.red

                        elif RED_NUMBERS[self.showWordIndex] == 1:
                            self.ellipseItem.color = Qt.red

                        elif RED_NUMBERS[self.showWordIndex] == 2:
                            self.starItem.color = Qt.red

                    k += 1

            self.showWordIndex += 1

        if self.scheduleTimer == 120:

            self.wordItems[self.showCount].hide()

            self.boxItem.hide()
            self.ellipseItem.hide()
            self.starItem.hide()

            self.showCount = 0

        self.scheduleTimer += 1

        if self.scheduleTimer > 210:

            if self.showWordIndex >= len(READS):
                self.process = "End"
                self.changeProcess()
            else:
                self.scheduleTimer = 0

    def test2(self):

        if self.scheduleTimer == 0:

            self.recordThread.start()

            k = 0
            for i in range(len(WORDS)):
                for j in range(len(WORDS[i])):

                    if READS[self.showWordIndex] == WORDS[i][j] and not k in EXCEPTION:

                        self.showCount = k
                        self.wavPath = "%s/wavs/test2_%s_%s.wav" % (self.logDir, "%02d" % self.showWordIndex, READS[self.showWordIndex])
                        self.recTime = 3.5

                    k += 1

            self.showWordIndex += 1

        if self.scheduleTimer > 0 and self.scheduleTimer <= 32:

            redValue = int(8 * self.scheduleTimer - 1)
            self.wordItems[self.showCount].setPen(QPen(QColor(redValue, 0, 0, 255), 1.0))
            self.wordItems[self.showCount].setBrush(QColor(redValue, 0, 0, 255))

        if self.scheduleTimer == 120:

            self.wordItems[self.showCount].setPen(QPen(Qt.black, 1.0))
            self.wordItems[self.showCount].setBrush(Qt.black)
            self.showCount = 0

        self.scheduleTimer += 1

        if self.scheduleTimer > 210:

            if self.showWordIndex >= len(READS):
                self.process = "End"
                self.changeProcess()
            else:
                self.scheduleTimer = 0

    def test3(self):

        if self.scheduleTimer == 0:

            self.recordThread.start()

            k = 0
            for i in range(len(WORDS)):
                for j in range(len(WORDS[i])):

                    if READS[self.showWordIndex] == WORDS[i][j] and not k in EXCEPTION:

                        self.wordItems[k].show()
                        self.showCount = k

                        self.wavPath = "%s/wavs/test3_%s_%s.wav" % (self.logDir, "%02d" % self.showWordIndex, READS[self.showWordIndex])
                        self.recTime = 3.5

                    k += 1

            self.showWordIndex += 1

        if self.scheduleTimer == 30:

            self.wordItems[self.showCount].hide()
            self.showCount = 0

        self.scheduleTimer += 1

        if self.scheduleTimer > 210:

            if self.showWordIndex >= len(READS):
                self.process = "End"
                self.changeProcess()
            else:
                self.scheduleTimer = 0

    def end(self):

        if self.scheduleTimer >= 300:
            self.process = "Result"
            self.changeProcess()
        else:
            self.scheduleTimer += 1


class ResultScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.name = "ResultScene"

        self.titleLabel = QGraphicsSimpleTextItem()
        self.titleLabel.setText("Now Analyzing ...")
        self.titleLabel.setPen(QPen(Qt.black, 1))
        self.titleLabel.setBrush(Qt.black)
        self.addItem(self.titleLabel)

    def setParam(self, logDir, analyzeMethod, isMakeFig, mode):

        self.analyzeThread = AnalyzeThread(logDir=logDir, analyzeMethod=analyzeMethod, isMakeFig=isMakeFig, mode=mode, parent=self)
        self.analyzeThread.countChanged.connect(self.parent().onCountChanged)
        self.analyzeThread.finished.connect(self.analyzeFinish)

    def setPosAndSize(self, frameSize):

        self.setSceneRect(0, 0, frameSize.width(), frameSize.height())

        aspectRatio = 16 / 9

        if self.width() / self.height() >= aspectRatio:
            unitRatio = self.height() * (1 / 9)
        else:
            unitRatio = self.width() * (1 / 16)

        self.titleLabel.setFont(QFont(DEFAULT_FONT_NAME, int(unitRatio * 0.7)))
        self.titleLabel.setPos((self.width() - self.titleLabel.boundingRect().width()) * 0.5, (self.height() - self.titleLabel.boundingRect().height()) * 0.2)

    def analyzeFinish(self):

        time.sleep(3)
        self.parent().sceneManager(mode="Title")


class AnalyzeThread(QThread):

    """
    Runs a counter thread.
    """
    countChanged = pyqtSignal(int)

    def __init__(self, logDir, analyzeMethod, isMakeFig, mode, parent=None):
        super().__init__(parent)

        self.logDir = logDir
        self.analyzeMethod = analyzeMethod
        self.isMakeFig = isMakeFig
        self.mode = mode

    def run(self):

        test1Datas = []
        test2Datas = []
        test3Datas = []

        testDatas = {"test1": test1Datas, "test2": test2Datas, "test3": test3Datas}
        cellRecordPosition = { "test1": [3, 2], "test2": [3, 7], "test3": [3, 12] }
        analyzeMethodCell = { "test1": "D35", "test2": "I35", "test3": "N35" }

        distinationPath = "%s/result.xlsx" % self.logDir
        dataPath = "../data/result_template.xlsx"

        if not os.path.isfile(distinationPath):
            shutil.copy(dataPath, distinationPath)

        progressCount = 0
        progressDeff = int(PROGRESS_LIMIT / (len(READS) + 1))

        wavDirPath = "%s/wavs" % self.logDir
        if os.path.isdir(wavDirPath):

            wavPaths = glob.glob("%s/*.wav" % wavDirPath)
            for wavPath in wavPaths:

                root, ext = os.path.splitext(wavPath)
                baseName = os.path.basename(root)

                if self.mode.lower() in baseName:
                    print("Analyzing %s.wav" % baseName)

                    if self.isMakeFig:
                        figDir = "%s/figs" % self.logDir
                        if not os.path.isdir(figDir):
                            os.mkdir(figDir)

                    if self.analyzeMethod == "MFCC":

                        if self.isMakeFig:
                            figName = "%s/%s_mfcc.png" % (figDir, baseName)
                        else:
                            figName = ""

                        startTime, endTime, interval = mfcc.run(fileName=wavPath, figName=figName, vadThreshold=MFCC_VAD_THRESHOLD)
                        excel.over_write_one_value(filePath=distinationPath, sheetName="VAD", value="MFCC", cell=analyzeMethodCell[self.mode.lower()])

                    if self.analyzeMethod == "SMA":

                        if self.isMakeFig:
                            figName = "%s/%s_sma.png" % (figDir, baseName)
                        else:
                            figName = ""

                        startTime, endTime, interval = sma.run(fileName=wavPath, figName=figName, window=SMA_WINDOW_SIZE, vadThreshold=SMA_VAD_THRESHOLD, minNoiseLevel=SMA_MIN_NOISE_LEVEL)
                        excel.over_write_one_value(filePath=distinationPath, sheetName="VAD", value="SMA", cell=analyzeMethodCell[self.mode.lower()])

                    datas = [startTime, endTime, interval]
                    testDatas[self.mode.lower()].append(datas)

                progressCount += progressDeff
                self.countChanged.emit(progressCount)

            excel.over_write_list_2d(filePath=distinationPath, sheetName="VAD", l_2d=testDatas[self.mode.lower()], start_row=cellRecordPosition[self.mode.lower()][0], start_col=cellRecordPosition[self.mode.lower()][1])

        progressCount = PROGRESS_LIMIT
        self.countChanged.emit(progressCount)


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.dirName = ""
        self.userName = ""
        self.analyzeMethod = DEFAULT_ANALYZE_METHOD
        self.isMakeFig = DEFAULT_IS_MAKE_FIGURE

        # ウインドウサイズを設定
        self.resize(WINDOW_SIZE[0], WINDOW_SIZE[1])

        # デスクトップのスクリーンサイズ取得
        desktop = qApp.desktop()
        geometry = desktop.screenGeometry()

        self.setGeometry(0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1])

        # ウインドウの位置を指定
        self.move(int((geometry.width() - self.width()) * 0.5), int((geometry.height() - self.height()) * 0.5))

        self.setWindowTitle(APPLICATION_NAME + " Ver." + str(VERSION_NUMBER))

        self.setWindowIcon(QIcon("../data/Thesquid.ink-Free-Flat-Sample-Support.ico"))

        # QGraphicsView
        self.graphicView = QGraphicsView()
        self.graphicView.setCacheMode(QGraphicsView.CacheBackground)

        self.graphicView.horizontalScrollBar().blockSignals(True)
        self.graphicView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.graphicView.verticalScrollBar().blockSignals(True)
        self.graphicView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setCentralWidget(self.graphicView)

        self.progress = QProgressBar(self)
        self.progress.setGeometry(0, 0, int(self.width() * 0.3), int(self.height() * 0.03))
        self.progress.setMaximum(PROGRESS_LIMIT)

        # self.titleScene = TitleScene(parent=self)
        # self.testScene = TestScene(parent=self)
        # self.resultScene = ResultScene(parent=self)

        self.sceneManager(mode="Title")

    def initLogDir(self):

        datatime = datetime.now().strftime("%Y.%m.%d_%H.%M.%S") # .strftime("%Y/%m/%d %H:%M:%S")
        self.logDir = "%s/%s_Ver%s_%s_%s" % (self.dirName, APPLICATION_NAME, VERSION_NUMBER, self.userName, datatime)

        if not os.path.exists(self.logDir):
            os.makedirs(self.logDir)

    def sceneManager(self, mode):

        if mode == "Test1" or mode == "Test2" or mode == "Test3":

            self.testScene = TestScene(parent=self)
            self.testScene.setPosAndSize(frameSize=self.geometry().size())
            self.testScene.mode = mode
            self.testScene.setLogDir(logDir=self.logDir)
            self.graphicView.setScene(self.testScene)

            self.testScene.process = "Start"
            self.testScene.changeProcess()

        if mode == "Result":

            resultScene = ResultScene(parent=self)
            resultScene.setPosAndSize(frameSize=self.geometry().size())
            resultScene.setParam(logDir=self.logDir, analyzeMethod=self.analyzeMethod, isMakeFig=self.isMakeFig, mode=self.testScene.mode)
            self.graphicView.setScene(resultScene)

            self.progress.setGeometry(int((self.width() - self.progress.width()) * 0.52), int((self.height() - self.progress.height()) * 0.6), self.progress.width(), self.progress.height())
            self.progress.setValue(0)
            self.progress.show()

            resultScene.analyzeThread.start()
            
        if mode == "Title":

            titleScene = TitleScene(parent=self)
            self.progress.hide()
            titleScene.setPosAndSize(frameSize=self.geometry().size())
            self.graphicView.setScene(titleScene)

    def keyPressEvent(self, event):

        key = event.key()
        if key == Qt.Key_Escape:

            # Windowの破棄命令
            print("Destroy Window")
            self.close()

        super(MainWindow, self).keyPressEvent(event)

    def callInputDialog(self):

        # self.hide()
        self.inputDlg = InputDialog(parent=self)
        self.inputDlg.show()

    def resizeEvent(self, event):

        self.graphicView.scene().setPosAndSize(frameSize=event.size())

        self.progress.setGeometry(0, 0, int(self.width() * 0.3), int(self.height() * 0.03))
        self.progress.setGeometry(int((self.width() - self.progress.width()) * 0.5), int((self.height() - self.progress.height()) * 0.6), self.progress.width(), self.progress.height())

    def onCountChanged(self, value):
        self.progress.setValue(value)


# エディットエリアのクリックイベントに対応したQLineEdit
class cQLineEdit(QLineEdit):

    clicked = pyqtSignal()
    def __init__(self, widget):
        super().__init__(widget)

    def mousePressEvent(self, QMouseEvent):
        self.clicked.emit()


# 最初のユーザ設定のためのダイアログ
class InputDialog(QDialog):

    def __init__(self, parent=None):
        super(InputDialog, self).__init__(parent)

        # ensure this window gets garbage-collected when closed
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.resize(INPUT_DIALOG_SIZE[0], INPUT_DIALOG_SIZE[1])

        # ディスプレイのサイズ取得
        desktop = qApp.desktop()
        screenGeometry = desktop.screenGeometry()

        # ダイアログをスクリーンの真ん中に表示
        self.setGeometry(0, 0, self.frameSize().width(), self.frameSize().height())
        self.move(int((screenGeometry.width() - self.frameSize().width()) * 0.5), int((screenGeometry.height() - self.frameSize().height()) * 0.5))

        self.initUI()

    def initUI(self):

        self.setWindowIcon(QIcon("../data/Thesquid.ink-Free-Flat-Sample-Support.ico"))

        # 各ウェジットのフォーカスがOnかOffかのコールバック
        QApplication.instance().focusChanged.connect(self.on_focusChanged)

        nameLabel = QLabel("Name :", self)
        nameLabel.move(20, 15)

        # ユーザネーム入力フォーム
        self.nameLineEdit = cQLineEdit(self)
        self.nameLineEdit.move(20, 30)
        self.nameLineEdit.setText(DEFAULT_USER_NAME)
        self.nameLineEdit.setStyleSheet("color: lightgray;")
        self.nameLineEdit.clicked.connect(self.handleNameLineTextClicked)
        self.nameLineEdit.textChanged.connect(self.handleNameLineTextChanged)

        dirLabel = QLabel("Log Location :", self)
        dirLabel.move(20, 60)

        # logのロケーション入力フォーム
        self.dirLineEdit = QLineEdit(self)
        self.dirLineEdit.setGeometry(0, 0, 200, 21)
        self.dirLineEdit.move(20, 75)
        self.dirLineEdit.setStyleSheet("color: lightgray;")

        # ディレクトリ選択ダイアログ
        selectDirButton = QPushButton("...", self)
        selectDirButton.move(225, 74)
        selectDirButton.clicked.connect(self.onClickedSlectDirButton)

        """ Windowsの場合Documentsフォルダの場所が変更されていても追従する
        if os.name == "nt":

            import ctypes.wintypes
            CSIDL_PERSONAL = 5       # My Documents
            SHGFP_TYPE_CURRENT = 0   # Get current, not default value

            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

            self.firstDirName = buf.value
        """

        # OSごとで異なるデフォルトLog保存フォルダ
        self.firstDirName = DEFAULT_LOG_LOCATION
        self.dirLineEdit.setText(self.firstDirName.replace("\\", "/"))

        # 次のメインウィンドウに進むためのサブミットボタン
        self.okButton = QPushButton("OK", self)
        self.okButton.move(120, 130)
        self.okButton.clicked.connect(self.onClickedOKButton)
        self.okButton.setEnabled(False)

        self.setWindowTitle("Input Name")

        # 各種設定が完成しているかどうかのフラグ
        self.isNameSet = False
        self.isDirSet = False

    # ネーム入力フォームがクリックされたら
    def handleNameLineTextClicked(self):

        if not self.isNameSet:
            self.nameLineEdit.setStyleSheet("color: black;")
            self.isNameSet = True
            self.checkSettingCompleted()

    # 各種ウェジットのフォーカス状態監視
    def on_focusChanged(self, old, now):

        # if self.nameLineEdit == old:
        #     self.nameLineEdit.setStyleSheet("color: black;")
        #     self.isNameSet = True
        #     self.checkSettingCompleted()

        if self.dirLineEdit == now:
            self.dirLineEdit.setStyleSheet("color: black;")
            self.isDirSet = True
            self.checkSettingCompleted()

    # ネーム入力フォームが変更されたら
    def handleNameLineTextChanged(self):

        if not self.isNameSet:
            self.nameLineEdit.setStyleSheet("color: black;")
            self.isNameSet = True
            self.checkSettingCompleted()

    # 名前とLogの場所が両方入力されたかどうかのチェック
    def checkSettingCompleted(self):

        if self.isNameSet and self.isDirSet:
            self.okButton.setEnabled(True)

    # フォルダ選択ダイアログを開く
    def onClickedSlectDirButton(self):

        selectDirName = QFileDialog.getExistingDirectory(self, "Select Directory", self.firstDirName)

        if selectDirName != "":
            self.dirLineEdit.setText(selectDirName)
            
            self.dirLineEdit.setStyleSheet("color: black;")
            self.isDirSet = True
            self.checkSettingCompleted()

    # サブミットボタンを押したときの処理
    def onClickedOKButton(self):

        # 設定したLogのパスに無理がある場合の例外処理
        try:
            if not os.path.exists(self.dirLineEdit.text()):
                os.mkdir(self.dirLineEdit.text())
        except Exception as e:
            # print(e)
            QMessageBox.warning(self, "Input error", "Error in the specification of log location !", QMessageBox.Ok)
        else:
            # 名前が空の場合の条件分岐
            if self.nameLineEdit.text() != "":

                self.accept()
                self.parent().show()

                self.parent().userName = self.nameLineEdit.text()
                self.parent().dirName = self.dirLineEdit.text()
                self.parent().initLogDir()
            else:
                QMessageBox.warning(self, "Input error", "Name is Empty !", QMessageBox.Ok)

    # ダイアログがバツボタンで閉じられたときの処理
    def closeEvent(self, event):

        self.reject()
        self.parent().close()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    # mainWindow.show()

    mainWindow.callInputDialog()
    sys.exit(app.exec_())
