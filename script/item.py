#!/usr/bin/env python
# coding: utf-8

import sys

import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class TextGraphicsSimpleTextItem(QGraphicsSimpleTextItem):

    def __init__(self, text, size, fontType="ＭＳ ゴシック", parent=None):
        super().__init__(parent)

        self.setText(text)
        self.setFont(QFont(fontType, size))
        self.setPen(QPen(Qt.black, 1.0))
        self.setBrush(Qt.black)

    def width(self):
        return self.boundingRect().width()

    def height(self):
        return self.boundingRect().height()


class BoxGraphicsItem(QGraphicsItem):

    def __init__(self, rect, color, parent=None):
        super().__init__(parent)

        self.rect = rect
        self.color = color

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        # ペンとブラシを設定する。
        painter.setPen(QPen(self.color, 1.0))
        painter.setBrush(self.color)

        painter.drawRect(self.rect[0], self.rect[1], self.rect[2], self.rect[3])

    def boundingRect(self):
        return QRectF(self.rect[0], self.rect[1], self.rect[2], self.rect[3])


class EllipseGraphicsItem(QGraphicsItem):

    edgeList = []

    def __init__(self, radius, color, parent=None):
        super().__init__(parent)

        self.radius = radius
        self.color = color

    def boundingRect(self): # 手直しの必要あり
        return QRectF(0.0, 0.0, self.radius * 2.0, self.radius * 2.0)

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        # ペンとブラシを設定する。
        painter.setPen(QPen(self.color, 1.0))
        painter.setBrush(self.color)

        painter.drawRoundedRect(0.0, 0.0, self.radius * 2.0, self.radius * 2.0, self.radius, self.radius)

    def shape(self):
        path = QPainterPath()
        path.addEllipse(0.0, 0.0, self.radius * 2.0, self.radius * 2.0)
        return path

    def addEdge(self, edge):
        self.edgeList.append(edge)
        edge.adjust()

    def edges(self):
        return self.edgeList


class CrossGraphicsItem(QGraphicsItem): # サイズを可変にする

    def __init__(self, size, lineWidth, color, parent=None):
        super().__init__(parent)

        self.size = size
        self.lineWidth = lineWidth
        self.color = color
        # まだ製作途中でポリゴンのサイズを動的に変更できるようにする

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        # ペンとブラシを設定する。
        painter.setPen(QPen(self.color, 1.0))
        painter.setBrush(self.color)

        # ポリゴンを描画する。
        poly = self.createShape()
        painter.drawPolygon(poly)

    def createShape(self):

        # QPolygonF に格納する。
        polygon = QPolygonF([
            QPointF(40, 0),     # 1
            QPointF(80, 0),    # 2
            QPointF(80, 40),   # 3
            QPointF(120, 40),   # 4
            QPointF(120, 80),  # 5
            QPointF(80, 80),  # 6
            QPointF(80, 120),  # 7
            QPointF(40, 120),   # 8
            QPointF(40, 80),   # 9
            QPointF(0, 80),    # 10
            QPointF(0, 40),     # 11
            QPointF(40, 40)     # 12
        ])

        return polygon

    def boundingRect(self):

        '''この図形を囲む矩形を返す。
        '''
        return QRectF(0, 0, 120, 120)

    def width(self):
        return 120

    def height(self):
        return 120


class StarGraphicsItem(QGraphicsItem):

    def __init__(self, center, radius, color, parent=None):
        super().__init__(parent)

        self.center = center
        self.radius = radius
        self.color = color

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        # ペンとブラシを設定する。
        painter.setPen(QPen(self.color, 1.0))
        painter.setBrush(self.color)

        # ポリゴンを描画する。
        poly = self.createShape()
        painter.drawPolygon(poly)

    def createShape(self):

        '''星を表すポリゴンを生成する。
        '''
        # 点を生成する。
        num_points = 11
        r = self.radius * np.where(np.arange(num_points) % 2.0 == 0.0, 0.5, 1.0)  # 半径
        theta = np.linspace(0.0, 2.0 * np.pi, num_points)  # 角度
        xs = self.center[0] + r * np.sin(theta)  # x 座標
        ys = self.center[1] + r * np.cos(theta)  # y 座標

        # QPolygonF に格納する。
        polygon = QPolygonF()
        [polygon.append(QPointF(x, y)) for x, y in zip(xs, ys)]

        return polygon

    def boundingRect(self):

        '''この図形を囲む矩形を返す。
        '''
        return QRectF(self.center[0] - self.radius,
                      self.center[1] - self.radius,
                      self.radius * 2.0, self.radius * 2.0)


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGeometry(100, 100, 500, 500)

        # シーンを作成する。
        starItem = StarGraphicsItem(center=(100, 100), radius=100, color=Qt.yellow)
        boxItem = BoxGraphicsItem(rect=(0, 0, 200, 200), color=Qt.blue)
        ellipseItem = EllipseGraphicsItem(radius=100, color=Qt.green)
        clossItem = CrossGraphicsItem(120, 40, Qt.black)
        textItem = TextGraphicsSimpleTextItem("あ", 200)

        self.scene = QGraphicsScene()
        self.scene.addItem(starItem)
        self.scene.addItem(boxItem)
        self.scene.addItem(ellipseItem)
        self.scene.addItem(clossItem)
        self.scene.addItem(textItem)

        # QGraphicsView
        graphicView = QGraphicsView()
        graphicView.setScene(self.scene)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(graphicView)
        central_widget.setLayout(layout)

        boxItem.setPos(-100, -100)
        starItem.setPos(100, 100)
        ellipseItem.setPos(-100, 100)
        clossItem.setPos(100, -100)

        # textItem.hide() # <=>show


if __name__ == '__main__':

    app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.show()
    sys.exit(app.exec_())
