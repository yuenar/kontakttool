# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

from PySide6.QtCore import QSize, Signal as pyqtSignal,QRect
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, \
    QListWidgetItem,QLabel
from PySide6.QtGui import QPixmap, QImage,QPainter,QBrush

from config import *

class ItemWidget(QWidget):
    itemDeleted = pyqtSignal(QListWidgetItem)

    def __init__(self, text, item, *args, **kwargs):
        super(ItemWidget, self).__init__(*args, **kwargs)
        self._item = item  # 保留list item的对象引用
        self.setObjectName("IWidget")

        layout = QHBoxLayout(self)
        # self.setFixedSize(QSize(380, 50))
        layout.setContentsMargins(0, 0, 0, 0)

        path=TARGET_MAC_ICON_DIR.replace("owenzhang",text)
        if not os.path.exists(path):
            line=QLineEdit(text, self)
            line.setFixedSize(QSize(340, 40))
            line.setReadOnly(True)
            layout.addWidget(line)
        else:
            lab = QLabel(self)
            lab.setFixedSize(QSize(340, 40))
            bpath=path+"/MST_artwork.png"
            ipath=path+"/MST_logo.png"
            # wpath=path+"/wallpaper.png"
            img1=QImage(bpath)
            img2=QImage(ipath)
            rect =QRect(img1.rect())
            pix = QPixmap(510, 60)
            pt =QPainter(pix)
            pt.setRenderHint(QPainter.Antialiasing)
            pt.fillRect(QRect(0,0,510, 60), QBrush("#CBD1D5"))
            pt.drawImage(rect,img1)
            pt.drawImage(rect,img2)
            pt.end()
            # pt.save(wpath)
            lab.setPixmap(pix)
            layout.addWidget(lab)

        btn=QPushButton('x ', self, clicked=self.doDeleteItem)
        btn.setFixedSize(QSize(40, 40))
        layout.addWidget(btn)

    def doDeleteItem(self):
        self.itemDeleted.emit(self._item)

    def sizeHint(self):
        # 决定item的高度
        return QSize(200, 50)