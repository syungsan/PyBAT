#!/usr/bin/env python
# coding: utf-8

# Windows Build Command
# .\venv\python -m PyInstaller .\script\BAT.py --noconsole --onefile --icon=.\data\Thesquid.ink-Free-Flat-Sample-Support.ico

import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from datetime import datetime
import threading
import glob
import shutil


APPLICATION_NAME = "BAT"
VERSION_NUMBER = "0.8.1"

START_MODE = "Start1"

INPUT_DIALOG_SIZE = [320, 240]
WINDOW_SIZE = [1280, 720]

# Path
# BASE_ABSOLUTE_PATH = os.path.dirname(os.path.realpath(__file__)) + "/../"

import script.item as itm
import script.record as rec
import script.mfcc as mfcc
import script.excel as xl


class TitleScene(QGraphicsScene):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.name = "TitleScene"
        self.mode = "Wait"

        titleLabel = QGraphicsSimpleTextItem()
        titleLabel.setText(APPLICATION_NAME)
        titleLabel.setFont(QFont("ＭＳ ゴシック", 80))
        titleLabel.setPen(QPen(Qt.black, 1))
        titleLabel.setBrush(Qt.black)

        versionNumberLabel = QGraphicsSimpleTextItem()
        versionNumberLabel.setText("Ver " + str(VERSION_NUMBER))
        versionNumberLabel.setFont(QFont("ＭＳ ゴシック", 20))
        versionNumberLabel.setPen(QPen(Qt.black, 1))
        versionNumberLabel.setBrush(Qt.black)
        versionNumberLabel.setPos(titleLabel.boundingRect().right() - versionNumberLabel.boundingRect().width(), titleLabel.boundingRect().bottom())

        self.addItem(titleLabel)
        self.addItem(versionNumberLabel)

        startButton = QPushButton("START")
        startButtonWidth = startButton.fontMetrics().boundingRect("START").width() + 20
        startButton.setMaximumWidth(startButtonWidth)
        startButton.move((titleLabel.boundingRect().width() - startButton.frameGeometry().width()) * 0.5, titleLabel.boundingRect().bottom() + 200)

        startButton.clicked.connect(lambda: self.onClickStartButton())
        self.addWidget(startButton)

    def onClickStartButton(self):
        self.mode = "Next"


class RecordingThread(QThread):

    recordSignal = pyqtSignal()

    def __init__(self, parent=None):
        QThread.__init__(self, parent)

    def run(self):
        self.recordSignal.emit()
        self.finished.emit()


class TestScene(QGraphicsScene):

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

    BASE_FRAME_PADDING_MARGIN = 20

    X_PADDING_MARGIN_RATIO = 0.05
    Y_PADDING_MARGIN_RATIO = 0.01

    WORD_GRID_FONT_SIZE = 50.0

    wordItems = []
    datas = []

    def __init__(self, parent=None):
        super().__init__(parent)

        self.makeBaseLayer()
        self.makeWordGrid()
        self.makeItem()

        self.name = "TestScene"
        self.mode = START_MODE
        self.isModeChange = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(1000 / 60)

        self.timer.start()

        self.logDir = ""

        self.wavPath = ""
        self.recTime = 0.0

        self.recordThread = RecordingThread()
        self.recordThread.recordSignal.connect(self.thread)

    def thread(self):
        thread = threading.Thread(target=self.record)
        thread.start()

    def record(self):
        rec.recording(self.wavPath, self.recTime)

    def makeBaseLayer(self):

        self.baseFrame = QRectF(0, 0, WINDOW_SIZE[0] - self.BASE_FRAME_PADDING_MARGIN, WINDOW_SIZE[1] - self.BASE_FRAME_PADDING_MARGIN)

        baseLayer = itm.BoxGraphicsItem(rect=(0, 0, WINDOW_SIZE[0] - 20, WINDOW_SIZE[1] - 20), color=Qt.white)
        self.addItem(baseLayer)

    def makeWordGrid(self):

        x_padding_margin = self.baseFrame.width() * self.X_PADDING_MARGIN_RATIO
        y_padding_margin = self.baseFrame.height() * self.Y_PADDING_MARGIN_RATIO

        for i in range(len(self.WORDS)):
            for j in range(len(self.WORDS[i])):

                wordItem = itm.TextGraphicsSimpleTextItem(self.WORDS[i][j], self.WORD_GRID_FONT_SIZE)
                self.addItem(wordItem)

                x_one_length = (self.baseFrame.width() - (x_padding_margin * 2.0)) / len(self.WORDS[i])
                y_one_length = (self.baseFrame.height() - (y_padding_margin * 2.0)) / len(self.WORDS)

                wordItem.setPos(x_one_length * j + x_padding_margin - (wordItem.width() * 0.5) + (x_one_length * 0.5),
                                y_one_length * i + y_padding_margin - (wordItem.height() * 0.5) + (y_one_length * 0.5))

                self.wordItems.append(wordItem)
                wordItem.hide()

    def makeItem(self):

        crossItem = itm.CrossGraphicsItem(size=(120, 120), lineWidth=10, color=Qt.black)
        self.addItem(crossItem)
        crossItem.setPos((self.baseFrame.width() - crossItem.width()) * 0.5, (self.baseFrame.height() - crossItem.height()) * 0.5)

        self.boxItem = itm.BoxGraphicsItem(rect=(0, 0, self.WORD_GRID_FONT_SIZE, self.WORD_GRID_FONT_SIZE), color=Qt.black)
        self.addItem(self.boxItem)
        self.boxItem.hide()

        self.ellipseItem = itm.EllipseGraphicsItem(radius=(self.WORD_GRID_FONT_SIZE * 0.5), color=Qt.black)
        self.addItem(self.ellipseItem)
        self.ellipseItem.hide()

        self.starItem = itm.StarGraphicsItem(center=(self.WORD_GRID_FONT_SIZE * 0.5, self.WORD_GRID_FONT_SIZE * 0.5), radius=self.WORD_GRID_FONT_SIZE * 0.5, color=Qt.black)
        self.addItem(self.starItem)
        self.starItem.hide()

    def update(self):

        if self.isModeChange == False:
            self.modeChange()

        if self.mode == "Start1" or self.mode == "Start2":
            self.start()

        elif self.mode == "End1" or self.mode == "End2":
            self.end()

        elif self.mode == "Test1":
            self.test1()

        elif self.mode == "Test2":
            self.test2()

    def modeChange(self):

        self.scheduleTimer = 0
        self.showWordIndex = 0
        self.showCount = 0

        if self.mode == "Start1" or self.mode == "Start2":
            for wordItem in self.wordItems:
                wordItem.hide()

        if self.mode == "Test2":
            for wordItem in self.wordItems:
                wordItem.show()

        if self.mode == "End1" or self.mode == "End2":
            for wordItem in self.wordItems:
                wordItem.hide()

        self.isModeChange = True

    def start(self):

        if self.scheduleTimer > 300:

            if self.mode == "Start1":
                self.mode = "Test1"

            if self.mode == "Start2":
                self.mode = "Test2"

            self.isModeChange = False

        self.scheduleTimer += 1

    def end(self):

        if self.scheduleTimer > 300:

            if self.mode == "End1":
                self.mode = "Start2"

            if self.mode == "End2":
                self.mode = "Result"

            self.isModeChange = False

        self.scheduleTimer += 1

    def test1(self):

        if self.scheduleTimer == 0:

            self.recordThread.start()

            dataDir = self.logDir + "/wavs"
            if not os.path.isdir(dataDir):
                os.mkdir(dataDir)

            count = 0
            for i in range(len(self.WORDS)):
                for j in range(len(self.WORDS[i])):

                    if self.READS[self.showWordIndex] == self.WORDS[i][j] and not count in self.EXCEPTION:
                        self.wordItems[count].show()
                        self.showCount = count

                        self.wavPath = dataDir + "/test1_%s_%s.wav" % ("%02d" % self.showWordIndex, self.READS[self.showWordIndex])
                        self.recTime = 3.5

                        self.boxItem.color = Qt.black
                        self.ellipseItem.color = Qt.black
                        self.starItem.color = Qt.black

                        self.boxItem.show()
                        self.ellipseItem.show()
                        self.starItem.show()

                        self.boxItem.setPos(self.wordItems[self.BOX_POSITIONS[self.showWordIndex]].x(), self.wordItems[self.BOX_POSITIONS[self.showWordIndex]].y())
                        self.ellipseItem.setPos(self.wordItems[self.ELLIPSE_POSITIONS[self.showWordIndex]].x(), self.wordItems[self.ELLIPSE_POSITIONS[self.showWordIndex]].y())
                        self.starItem.setPos(self.wordItems[self.STAR_POSITIONS[self.showWordIndex]].x(), self.wordItems[self.STAR_POSITIONS[self.showWordIndex]].y())

                        if self.RED_NUMBERS[self.showWordIndex] == 0:
                            self.boxItem.color = Qt.red

                        elif self.RED_NUMBERS[self.showWordIndex] == 1:
                            self.ellipseItem.color = Qt.red

                        elif self.RED_NUMBERS[self.showWordIndex] == 2:
                            self.starItem.color = Qt.red

                    count += 1

            self.showWordIndex += 1

        self.scheduleTimer += 1

        if self.scheduleTimer == 120:

            self.wordItems[self.showCount].hide()

            self.boxItem.hide()
            self.ellipseItem.hide()
            self.starItem.hide()

            self.showCount = 0

        if self.scheduleTimer > 210:

            if self.showWordIndex >= len(self.READS):
                self.mode = "End1"
                self.isModeChange = False
            else:
                self.scheduleTimer = 0

    def test2(self):

        if self.scheduleTimer == 0:

            self.recordThread.start()

            dataDir = self.logDir + "/wavs"
            if not os.path.isdir(dataDir):
                os.mkdir(dataDir)

            count = 0
            for i in range(len(self.WORDS)):
                for j in range(len(self.WORDS[i])):

                    if self.READS[self.showWordIndex] == self.WORDS[i][j] and not count in self.EXCEPTION:

                        self.wordItems[count].setPen(QPen(Qt.red, 1.0))
                        self.wordItems[count].setBrush(Qt.red)
                        self.showCount = count

                        self.wavPath = dataDir + "/test2_%s_%s.wav" % ("%02d" % self.showWordIndex, self.READS[self.showWordIndex])
                        self.recTime = 3.5

                    count += 1

            self.showWordIndex += 1

        self.scheduleTimer += 1

        if self.scheduleTimer == 120:

            self.wordItems[self.showCount].setPen(QPen(Qt.black, 1.0))
            self.wordItems[self.showCount].setBrush(Qt.black)
            self.showCount = 0

        if self.scheduleTimer > 210:

            if self.showWordIndex >= len(self.READS):
                self.mode = "End2"
                self.isModeChange = False
            else:
                self.scheduleTimer = 0


class ResultScene(QGraphicsScene):

    test1_datas = []
    test2_datas = []

    def __init__(self, logDir, parent=None):
        super().__init__(parent)

        self.name = "ResultScene"
        self.logDir = logDir

        self.analize()

        self.distinationPath = "%s/result.xlsx" % self.logDir
        dataPath = "../data/result_template.xlsx"

        if not os.path.isfile(self.distinationPath):
            shutil.copy(dataPath, self.distinationPath)

        # self.get_excel()
        self.set_excel()

    def analize(self):

        wavDirPath = "%s/wavs" % self.logDir
        if os.path.isdir(wavDirPath):

            wavPaths = glob.glob("%s/*.wav" % wavDirPath)
            for wavPath in wavPaths:

                root, ext = os.path.splitext(wavPath)
                baseName = os.path.basename(root)

                print("Analizing %s.wav" % baseName)

                figDir = "%s/figs" % self.logDir
                if not os.path.isdir(figDir):
                    os.mkdir(figDir)

                startTime, endTime, interval = mfcc.run(wavPath, "%s/%s.png" % (figDir, baseName))

                datas = [startTime, endTime, interval]

                if "test1" in baseName:
                    self.test1_datas.append(datas)

                elif "test2" in baseName:
                    self.test2_datas.append(datas)
    '''
    def get_excel(self):

        test1_results = xl.get_list_2d(self.distinationPath, "VAD解析結果", 3, 34, 2, 4)
        test2_results = xl.get_list_2d(self.distinationPath, "VAD解析結果", 3, 34, 7, 9)

        print(test1_results)
        print(test2_results)
    '''

    def set_excel(self):

        # print(self.test1_datas)
        # print(self.test2_datas)

        xl.over_write_list_2d(self.distinationPath, "VAD解析結果", self.test1_datas, 3, 2)
        xl.over_write_list_2d(self.distinationPath, "VAD解析結果", self.test2_datas, 3, 7)


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        # ウインドウサイズを設定
        self.resize(WINDOW_SIZE[0], WINDOW_SIZE[1])

        # デスクトップのスクリーンサイズ取得
        desktop = qApp.desktop()
        geometry = desktop.screenGeometry()

        # ウインドウサイズ(枠込)を取得
        framesize = self.frameSize()

        self.setGeometry(0, 0, WINDOW_SIZE[0], WINDOW_SIZE[1])

        # ウインドウの位置を指定
        self.move((geometry.width() - framesize.width()) * 0.5, (geometry.height() - framesize.height()) * 0.5)

        self.setWindowTitle(APPLICATION_NAME + " Ver." + str(VERSION_NUMBER))

        self.scene = TitleScene()

        # QGraphicsView
        self.graphicView = QGraphicsView()
        self.graphicView.setCacheMode(QGraphicsView.CacheBackground)
        self.graphicView.setScene(self.scene)

        self.setCentralWidget(self.graphicView)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(1000 / 60)

        self.timer.start()

    def initLogDir(self, userName, dirName):

        datatime = datetime.now().strftime("%Y%m%d_%H%M%S") # .strftime("%Y/%m/%d %H:%M:%S")
        self.logDir = "%s/%s_%s" % (dirName, userName, datatime)
        os.makedirs(self.logDir)

    def sceneManager(self):

        if self.scene.name == "TitleScene" and self.scene.mode == "Next":

            self.scene = TestScene()
            self.scene.logDir = self.logDir
            self.graphicView.setScene(self.scene)

        if self.scene.name == "TestScene" and self.scene.mode == "Result":

            self.scene = ResultScene(self.logDir)
            self.graphicView.setScene(self.scene)

    def update(self):
        self.sceneManager()

    def keyPressEvent(self, event):

        key = event.key()
        if key == Qt.Key_Escape:

            # Windowの破棄命令
            print("Destroy Window")
            self.close()

        super(MainWindow, self).keyPressEvent(event)

    def callInputDialog(self):

        # self.hide()
        self.inputDlg = InputDialog(self)
        self.inputDlg.show()


class InputDialog(QDialog):

    def __init__(self, parent):
        super(InputDialog, self).__init__(parent)

        # ensure this window gets garbage-collected when closed
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.resize(INPUT_DIALOG_SIZE[0], INPUT_DIALOG_SIZE[1])

        desktop = qApp.desktop()
        geometry = desktop.screenGeometry()

        framesize = self.frameSize()

        self.setGeometry(0, 0, framesize.width(), framesize.height())
        self.move((geometry.width() - framesize.width()) * 0.5, (geometry.height() - framesize.height()) * 0.5)

        self.initUI()

    def initUI(self):

        self.okButton = QPushButton("OK", self)
        self.okButton.move(20, 20)
        self.okButton.clicked.connect(self.closeAndReturn)

        self.nameLineEdit = QLineEdit(self)
        self.nameLineEdit.move(130, 22)

        self.selectDirButton = QPushButton('...', self)
        self.selectDirButton.move(240, 50)
        self.selectDirButton.clicked.connect(self.selectDir)

        self.dirLineEdit = QLineEdit(self)
        self.dirLineEdit.setGeometry(0, 0, 200, self.dirLineEdit.height())

        self.dirLineEdit.move(20, 50)

        self.firstDirName = os.path.expanduser("~") + "/Documents"

        self.dirLineEdit.setText(self.firstDirName)

        # self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle('Name Input')

    def selectDir(self):

        selectDirName = QFileDialog.getExistingDirectory(self, "Select Directory", self.firstDirName)

        if selectDirName != "":
            self.dirLineEdit.setText(selectDirName)

    def closeAndReturn(self):

        self.accept()
        self.parent().show()

        userName = self.nameLineEdit.text()
        dirName = self.dirLineEdit.text()

        self.parent().initLogDir(userName, dirName)

    def closeEvent(self, event):

        self.reject()
        self.parent().close()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    # mainWindow.show()

    mainWindow.callInputDialog()
    sys.exit(app.exec_())
