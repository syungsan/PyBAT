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

    def __init__(self, color, rect=QRectF(0, 0, 10, 10), parent=None):
        super().__init__(parent)

        self.rect = rect
        self.color = color

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        # ペンとブラシを設定する。
        painter.setPen(QPen(self.color, 1.0))
        painter.setBrush(self.color)

        painter.drawRect(self.boundingRect())

    def boundingRect(self):
        return self.rect


class CrossGraphicsItem(QGraphicsItem):

    def __init__(self, color, size=120, lineWidth=40, parent=None):
        super().__init__(parent)

        self.color = color
        self.size = size
        self.lineWidth = lineWidth

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing)

        # ペンとブラシを設定する。
        painter.setPen(QPen(self.color, 1.0))
        painter.setBrush(self.color)

        # ポリゴンを描画する。
        poly = self.createShape()
        painter.drawPolygon(poly)

    def createShape(self):

        s = self.size
        l = self.lineWidth
        p = (s - l) * 0.5
        q = p + l

        # QPolygonF に格納する。
        polygon = QPolygonF([
            QPointF(p, 0),     # 1
            QPointF(q, 0),    # 2
            QPointF(q, p),   # 3
            QPointF(s, p),   # 4
            QPointF(s, q),  # 5
            QPointF(q, q),  # 6
            QPointF(q, s),  # 7
            QPointF(p, s),   # 8
            QPointF(p, q),   # 9
            QPointF(0, q),    # 10
            QPointF(0, p),     # 11
            QPointF(p, p)     # 12
        ])

        return polygon

    def boundingRect(self):

        '''この図形を囲む矩形を返す。
        '''
        return QRectF(0, 0, self.size, self.size)

    def width(self):
        return self.boundingRect().width()

    def height(self):
        return self.boundingRect().height()


class EllipseGraphicsItem(QGraphicsItem):

    def __init__(self, radius, color, parent=None):
        super().__init__(parent)

        self.edgeList = []

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

    def width(self):
        return self.boundingRect().width()

    def height(self):
        return self.boundingRect().height()


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
        xs = self.center.x() + r * np.sin(theta)  # x 座標
        ys = self.center.y() + r * np.cos(theta)  # y 座標

        # QPolygonF に格納する。
        polygon = QPolygonF()
        [polygon.append(QPointF(x, y)) for x, y in zip(xs, ys)]

        return polygon

    def boundingRect(self):

        '''この図形を囲む矩形を返す。
        '''
        return QRectF(self.center.x() - self.radius, self.center.y() - self.radius, self.radius * 2.0, self.radius * 2.0)

    def width(self):
        return self.boundingRect().width()

    def height(self):
        return self.boundingRect().height()


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
