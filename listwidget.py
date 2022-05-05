# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

from PySide6.QtCore import QSize, Signal as pyqtSignal,QRect
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, \
    QListWidgetItem,QLabel
from PySide6.QtGui import QPixmap, QImage,QPainter,QBrush,QPen

from config import *
from utiltool import *

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
            ps=judge_plist(text)
            if not os.path.exists(ps):
                pic=ps.replace(".png",".jpg")
                if not os.path.exists(pic):
                    # line = QLineEdit(text, self)
                    # line.setFixedSize(QSize(340, 60))
                    # line.setReadOnly(True)
                    # layout.addWidget(line)

                    lab = QLabel(self)
                    lab.setFixedSize(QSize(340, 60))
                    if len(text) < 10:
                        src = os.fspath(Path(__file__).resolve().parent / "src/wallpaper1.png")
                    elif len(text) < 20:
                        src = os.fspath(Path(__file__).resolve().parent / "src/wallpaper2.png")
                    else:
                        src = os.fspath(Path(__file__).resolve().parent / "src/wallpaper.png")
                    img = QImage(src)
                    apix = QPixmap(340, 60)
                    p = QPainter(apix)
                    p.setPen("#34495E")
                    p.drawImage(apix.rect(), img.scaled(340, 60))
                    p.drawText(35, 50, text)
                    p.end()
                    apix.save(ps)
                    lab.setPixmap(apix)
                    layout.addWidget(lab)

                else:
                    # print("jpg path:" + pic)
                    lab = QLabel(self)
                    lab.setFixedSize(QSize(340, 60))
                    img = QImage(pic)
                    rect = QRect(0,0,340, 60)
                    pi = QPixmap(510, 60)
                    pt = QPainter(pi)
                    pt.setPen("#34495E")
                    pt.setRenderHint(QPainter.Antialiasing)
                    pt.fillRect(QRect(0, 0, 510, 60), QBrush("#CBD1D5"))
                    pt.drawImage(rect, img.scaled(340,60))
                    pt.drawText(35, 50, text)
                    pt.end()
                    lab.setPixmap(pi)
                    layout.addWidget(lab)
            else:
                # print("png path:" + ps)
                pic=ps
                lab = QLabel(self)
                lab.setFixedSize(QSize(340, 60))
                img = QImage(pic)
                rect = QRect(0,0,340, 60)
                pi = QPixmap(510, 60)
                pt = QPainter(pi)
                pt.setPen("#34495E")
                pt.setRenderHint(QPainter.Antialiasing)
                pt.fillRect(QRect(0, 0, 510, 60), QBrush("#CBD1D5"))
                pt.drawImage(rect, img.scaled(340,60))
                pt.drawText(35, 50, text)
                pt.end()
                lab.setPixmap(pi)
                layout.addWidget(lab)
        else:
            lab = QLabel(self)
            lab.setFixedSize(QSize(340, 60))
            bpath=path+"/MST_artwork.png"
            ipath=path+"/MST_logo.png"
            # wpath=path+"/wallpaper.png"
            img1=QImage(bpath)
            img2=QImage(ipath)
            rect =QRect(0,0,340,60)
            pix = QPixmap(510, 60)
            pt =QPainter(pix)
            pt.setPen("#FFFFFF")
            pt.setRenderHint(QPainter.Antialiasing)
            pt.fillRect(QRect(0,0,510, 60), QBrush("#CBD1D5"))
            pt.drawImage(rect,img1.scaled(340,60))
            pt.drawImage(rect,img2.scaled(340,60))
            pt.drawText(35, 50, text)
            pt.end()
            # pt.save(wpath)
            lab.setPixmap(pix)
            layout.addWidget(lab)

        btn=QPushButton('x ', self, clicked=self.doDeleteItem)
        btn.setFixedSize(QSize(60, 60))
        layout.addWidget(btn)

    def doDeleteItem(self):
        self.itemDeleted.emit(self._item)

    def sizeHint(self):
        # 决定item的高度
        return QSize(200, 50)