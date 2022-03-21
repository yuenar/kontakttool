# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

from PySide6.QtCore import QSize, Signal as pyqtSignal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, \
    QListWidgetItem

class ItemWidget(QWidget):
    itemDeleted = pyqtSignal(QListWidgetItem)

    def __init__(self, text, item, *args, **kwargs):
        super(ItemWidget, self).__init__(*args, **kwargs)
        self._item = item  # 保留list item的对象引用
        self.setObjectName("IWidget")

        layout = QHBoxLayout(self)
        # self.setFixedSize(QSize(380, 50))
        layout.setContentsMargins(0, 0, 0, 0)
        line=QLineEdit(text, self)
        line.setFixedSize(QSize(340, 40))
        line.setReadOnly(True)
        layout.addWidget(line)
        btn=QPushButton('x ', self, clicked=self.doDeleteItem)
        btn.setFixedSize(QSize(40, 40))
        layout.addWidget(btn)

    def doDeleteItem(self):
        self.itemDeleted.emit(self._item)

    def sizeHint(self):
        # 决定item的高度
        return QSize(200, 50)