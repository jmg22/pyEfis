#  Copyright (c) 2013 Neil Domalik
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class Panel_Annunciator(QGraphicsView):
    def __init__(self, parent=None):
        super(Panel_Annunciator, self).__init__(parent)
        self.setStyleSheet("border: 0px")
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.Antialiasing)
        self.setFocusPolicy(Qt.NoFocus)
        self._Mode_Indicator = 0
        self.Warning_State_Label = "null"

    def resizeEvent(self, event):
        self.w = self.width()
        self.h = self.height()
        self.f = QFont()
        self.f.setBold(True)
        self.f.setPixelSize(16)

        dialPen = QPen(QColor(Qt.white))
        dialPen.setWidth(5)

        self.scene = QGraphicsScene(0, 0, self.w, self.h)
        self.scene.addRect(0, 0, self.w, self.h,
                           QPen(QColor(Qt.gray)), QBrush(QColor(Qt.black)))
        self.scene.addRect(1, 1, self.w -2, self.h -2,
                           QPen(QColor(Qt.black)), QBrush(QColor(Qt.transparent)))
        t = self.scene.addText(str(self.Warning_State_Label))
        t.setFont(self.f)
        self.scene.setFont(self.f)
        t.setDefaultTextColor(QColor(Qt.white))
        t.setX((self.w - t.boundingRect().width()) / 2)
        t.setY((self.h - t.boundingRect().height()) / 2)
        self.setScene(self.scene)

    def redraw(self):
        self.scene.clear()
        self.scene.addRect(0, 0, self.w, self.h,
                           self.pcolor, self.bcolor)
        self.scene.addRect(1, 1, self.w -2, self.h -2,
                           QPen(QColor(Qt.black)), QBrush(QColor(Qt.transparent)))
        t = self.scene.addText(str(self.Warning_State_Label))
        t.setFont(self.f)
        self.scene.setFont(self.f)
        t.setDefaultTextColor(QColor(Qt.white))
        t.setX((self.w - t.boundingRect().width()) / 2)
        t.setY(((self.h - t.boundingRect().height()) / 2))
                           
        self.setScene(self.scene)

    def getState(self):
        return self._Mode_Indicator

    def setState(self, Mode):
        if Mode != self._Mode_Indicator:
            if Mode == 0:
                self._Mode_Indicator = 0
                self.bcolor = QBrush(QColor(Qt.black))
                self.pcolor = QPen(QColor(Qt.gray))
            elif Mode == 1:
                self._Mode_Indicator = 1
                self.bcolor = QBrush(QColor(Qt.yellow))
                self.pcolor = QPen(QColor(Qt.gray))
            elif Mode == 2:
                self._Mode_Indicator = 2
                self.bcolor = QBrush(QColor(Qt.red)) 
                self.pcolor = QPen(QColor(Qt.gray))
            elif Mode == 3:
                self._Mode_Indicator = 3
                self.bcolor = QBrush(QColor(Qt.green))
                self.pcolor = QPen(QColor(Qt.gray))
            self.redraw()

    def getWARNING_Name(self):
        return self._Mode_Indicator

    def setWARNING_Name(self, w_Name):
        self.Warning_State_Label = str(w_Name)
        

    panel_annunciator = property(getState, setState, getWARNING_Name, setWARNING_Name)
