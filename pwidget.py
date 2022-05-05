# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

import os
import sys
import random
from pathlib import Path
from utiltool import *
from PyQt5.QtWidgets import QPushButton, QWidget,QFileDialog,QLineEdit, QTextBrowser,QMessageBox
from PyQt5.QtGui import QRegularExpressionValidator,QImage,QPainter,QPixmap,QPen
from PyQt5.QtCore import QFile,QRegularExpression, pyqtSignal as Signal
# from PyQt5.QtUiTools import QUiLoader
from PyQt5 import uic

class PWidget(QWidget):
    importPath = Signal(str)
    def __init__(self):
        super(PWidget, self).__init__()
        self.load_ui()
        self.dialog = QFileDialog()
        self.wpBtn=QPushButton(self.tr("Broswer"), self,
                                     objectName="GreenButton", minimumHeight=32 ,clicked=self.openFolder)
        self.wpBtn.move(250,280)
        self.wpBtn.resize(100,36)

        self.opBtn=QPushButton(self.tr("Take Image"), self,
                                     objectName="GreenButton", minimumHeight=32 ,clicked=self.openPic)
        self.opBtn.move(250,360)
        self.opBtn.resize(100, 36)

        self.rBtn=QPushButton(self.tr("Generate random data "), self,
                                     objectName="GreenButton", minimumHeight=32 ,clicked=self.doRandom)
        self.rBtn.move(20,460)
        self.rBtn.resize(160, 32)

        self.cBtn=QPushButton(self.tr("Mark && Load 3rd Bank "), self,
                                     objectName="GreenButton", minimumHeight=32 ,clicked=self.doCreateNcint)
        self.cBtn.move(190,460)
        self.cBtn.resize(160, 32)

        # hBtn=QPushButton(" ？ ", self,
        #                               objectName="BlueButton",minimumHeight=32 ,clicked=self.doVisit)
        # hBtn.move(350,460)
        # hBtn.resize(330, 32)

        self.ui.label_bf.setText(self.tr("Bank folder："))
        self.ui.label_bn.setText(self.tr("BankName："))
        self.ui.label_sid.setText(self.tr("Snpid："))
        self.ui.label_wp.setText(self.tr("Wallpaper："))
        self.ui.label_com.setText(self.tr("CompyName："))
        self.ui.label_title.setText(self.tr("NICNT Generator"))

        vtor=QRegularExpressionValidator()
        vtor.setRegularExpression(QRegularExpression("[^%&',;=?$\x22]+[a-zA-Z0-9]+$"))

        self.cle=QLineEdit(self)
        self.cle.setPlaceholderText(self.tr("Cannot input Chinese！"))
        self.cle.setMaxLength(128)
        self.cle.move(20,60)
        self.cle.resize(330,36)
        self.cle.setValidator(vtor)

        self.ble=QLineEdit(self)
        self.ble.setPlaceholderText(self.tr("Cannot input Chinese！"))
        self.ble.move(20, 150)
        self.ble.setMaxLength(128)
        self.ble.resize(330,36)
        self.ble.setValidator(vtor)

        self.sle=QLineEdit(self)
        self.sle.setPlaceholderText(self.tr("Cannot input Chinese！"))
        self.sle.setText("a123")

        vtor1=QRegularExpressionValidator()
        vtor1.setRegularExpression(QRegularExpression("[a-zA-Z0-9]+$"))
        self.sle.setValidator(vtor1)
        self.sle.setMaxLength(4)
        self.sle.move(20, 240)
        self.sle.resize(330, 36)

        self.ole=QLineEdit(self)
        self.ole.setPlaceholderText(self.tr("choose a 3rd-bank floder."))
        self.ole.move(20, 320)
        self.ole.resize(330, 36)

        self.wle = QLineEdit(self)
        self.wle.setPlaceholderText(self.tr("choose a wallpaper."))
        self.wle.move(20, 410)
        self.wle.resize(330, 36)

        self.msgBox = QMessageBox()
        self.msgBox.setWindowTitle(self.tr('Warning'))
        self.msgBox.setIcon(QMessageBox.Warning)
        self.msgBox.setInformativeText(self.tr("Please check your input！"))

    def load_ui(self):
        # loader = QUiLoader()
        path = get_path( "src/form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.Truncate and QFile.ReadOnly)
        # self.ui = loader.load(ui_file, self)
        self.ui = uic.loadUi(ui_file, self)
        ui_file.close()

    def openFolder(self):
        lib_dir = self.dialog.getExistingDirectory(self, self.tr("Broswer"), os.getcwd())
        if len(lib_dir) < 1:
            return

        # print(lib_dir)

        self.ole.setText(lib_dir)

    def doRandom(self):
        if len(self.ole.text()) <1:
            self.msgBox.setText(self.tr("choose a 3rd-bank floder！"))
            self.msgBox.show()
            return
        else:
            if(os.path.exists(self.ole.text())):
                baseName=os.path.basename(self.ole.text())
                print("base"+baseName)
                if("-" in baseName):
                    comName=baseName.split("-",1)[0]
                    bName=baseName.split("-",1)[1]
                    self.cle.setText(comName)
                    self.ble.setText(bName)
                elif(" " in baseName):
                    comName=baseName.split(" ",1)[0]
                    bName=baseName.split(" ",1)[1]
                    self.cle.setText(comName)
                    self.ble.setText(bName)
                elif("." in baseName):
                    comName=baseName.split(".",1)[0]
                    bName=baseName.split(".",1)[1]
                    self.cle.setText(comName)
                    self.ble.setText(bName)
                else:
                    self.cle.setText("Kontakt")
                s=len(baseName)
                alpha=s%3
                if(alpha==0):
                    self.sle.setText("d"+str(s))
                elif (alpha == 1):
                    self.sle.setText("e" + str(s))
                else:
                    self.sle.setText(str(random.randint(210,9999)))

    def openPic(self):
        lib_dir = self.dialog.getOpenFileName(self,self.tr("please choose an image file"),os.getcwd(),"Image Files(*.jpg *.png )")
        if len(lib_dir) < 1:
            return

        self.wle.setText(lib_dir[0])

    def doCreateNcint(self):
        if(len(self.cle.text())<1):
            self.msgBox.setText(self.tr("Cannot input null！"))
            self.msgBox.show()
        elif (len(self.ble.text())<1):
            self.msgBox.setText(self.tr("Cannot input null！"))
            self.msgBox.show()
        elif (len(self.sle.text())<1):
            self.msgBox.setText(self.tr("Cannot input null！"))
            self.msgBox.show()
        elif (len(self.ole.text())<1):
            self.msgBox.setText(self.tr("Cannot input null！"))
            self.msgBox.show()
        elif not os.path.exists(self.ole.text()):
            self.msgBox.setText(self.tr("Is not exist！"))
            self.msgBox.show()
        else:
            # print("creating...")
            path= create_nicnt(self.cle.text(),self.ble.text(),self.sle.text(),self.ole.text())
            self.importPath.emit(path)
            outPic = self.ole.text() + "/wallpaper.png"

            if not os.path.exists(self.ole.text()):
                if len(self.ble.text()) < 10:
                    src = get_path( "src/wallpaper1.png")
                elif len(self.ble.text()) < 20:
                    src = get_path(  "src/wallpaper2.png")
                else:
                    src = get_path(  "src/wallpaper.png")
                img=QImage(src)
                pix= QPixmap(340,60)
                p=QPainter(pix)
                p.setPen("#34495E")
                p.drawImage(pix.rect(),img.scaled(340,60))
                p.drawText(35,50,self.ble.text())
                p.end()
            else:
                img=QImage(self.wle.text())
                img.scaled(382,100).save(outPic)

    def setAr(self,flag):
        if flag:
            self.opBtn.move(20, 360)
            self.wpBtn.move(20, 280)
        else:
            self.opBtn.move(250,360)
            self.wpBtn.move(250, 280)
