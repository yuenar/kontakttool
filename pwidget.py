# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys

from PySide6.QtWidgets import QPushButton, QWidget,QFileDialog,QLineEdit, QTextBrowser,QMessageBox
from PySide6.QtGui import QRegularExpressionValidator,QImage
from PySide6.QtCore import QFile,QRegularExpression, Signal
from PySide6.QtUiTools import QUiLoader

def create_nicnt(compyName,libName,snpid,path):
    if os.path.isdir(path):
        src = os.fspath(Path(__file__).resolve().parent /"src/Source.nicnt")
        fullname=libName+".nicnt"
        fullpath=os.path.join(path,fullname)

        fp3 = open(src, "r", encoding="ISO-8859-1")
        fp4 = open(fullpath, "w")

        for s in fp3.readlines():  # 先读出来
            fp4.write(s.replace("libName", libName).replace("sid",snpid).replace("compName",compyName))  # 替换 并写入

        fp3.close()
        fp4.close()
        # print("done")
        return fullpath

class PWidget(QWidget):
    importPath = Signal(str)
    def __init__(self):
        super(PWidget, self).__init__()
        self.load_ui()
        self.dialog = QFileDialog()
        wpBtn=QPushButton("打开Broswer", self,
                                     objectName="GreenButton", minimumHeight=32 ,clicked=self.openFolder)
        wpBtn.move(250,280)
        wpBtn.resize(100,36)


        opBtn=QPushButton("选图Take Image", self,
                                     objectName="GreenButton", minimumHeight=32 ,clicked=self.openPic)
        opBtn.move(250,360)
        opBtn.resize(100, 36)

        cBtn=QPushButton("生成并导入库Create .nicnt && Export to Library ", self,
                                     objectName="GreenButton", minimumHeight=32 ,clicked=self.doCreateNcint)
        cBtn.move(20,460)
        cBtn.resize(330, 32)

        vtor=QRegularExpressionValidator()
        vtor.setRegularExpression(QRegularExpression("[^%&',;=?$\x22]+[a-zA-Z0-9]+$"))

        self.cle=QLineEdit(self)
        self.cle.setPlaceholderText("不支持输入中文！Cannot input Chinese！")
        self.cle.setMaxLength(128)
        self.cle.move(20,60)
        self.cle.resize(330,36)
        self.cle.setValidator(vtor)

        self.ble=QLineEdit(self)
        self.ble.setPlaceholderText("不支持输入中文！Cannot input Chinese！")
        self.ble.move(20, 150)
        self.ble.setMaxLength(128)
        self.ble.resize(330,36)
        self.ble.setValidator(vtor)

        self.sle=QLineEdit(self)
        self.sle.setPlaceholderText("最多输入4位字符！Enter up to 4 characters！")
        self.sle.setText("a123")

        vtor1=QRegularExpressionValidator()
        vtor1.setRegularExpression(QRegularExpression("[a-zA-Z0-9]+$"))
        self.sle.setValidator(vtor1)
        self.sle.setMaxLength(4)
        self.sle.move(20, 240)
        self.sle.resize(330, 36)

        self.ole=QLineEdit(self)
        self.ole.setPlaceholderText("选择输出路径，choose a floder.")
        self.ole.move(20, 320)
        self.ole.resize(330, 36)

        self.wle = QLineEdit(self)
        self.wle.setPlaceholderText("选择一张图片做背景，choose a wallpaper.")
        self.wle.move(20, 410)
        self.wle.resize(330, 36)

        self.msgBox = QMessageBox()
        self.msgBox.setWindowTitle('警告Warning')
        self.msgBox.setIcon(QMessageBox.Warning)
        self.msgBox.setInformativeText("请检查输入Please check your input！")

    def load_ui(self):
        loader = QUiLoader()
        path = os.fspath(Path(__file__).resolve().parent /"src/form.ui")
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        loader.load(ui_file, self)
        ui_file.close()

    def openFolder(self):
        lib_dir = self.dialog.getExistingDirectory(self, "选取文件夹", os.getcwd())
        if len(lib_dir) < 1:
            return

        # print(lib_dir)

        self.ole.setText(lib_dir)

    def openPic(self):
        lib_dir = self.dialog.getOpenFileName(self,"please choose an image file",os.getcwd(),"Image Files(*.jpg *.png )")
        if len(lib_dir) < 1:
            return

        self.wle.setText(lib_dir[0])

    def doCreateNcint(self):
        if(len(self.cle.text())<1):
            self.msgBox.setText("公司名不得为空Cannot input null！")
            self.msgBox.show()
        elif (len(self.ble.text())<1):
            self.msgBox.setText("音色名不得为空Cannot input null！")
            self.msgBox.show()
        elif (len(self.sle.text())<1):
            self.msgBox.setText("音色id不得为空Cannot input null！")
            self.msgBox.show()
        elif (len(self.ole.text())<1):
            self.msgBox.setText("路径不得为空Cannot input null！")
            self.msgBox.show()
        elif not os.path.exists(self.ole.text()):
            self.msgBox.setText("路径不存在Is not exist！")
            self.msgBox.show()
        else:
            # print("creating...")
            path= create_nicnt(self.cle.text(),self.ble.text(),self.sle.text(),self.ole.text())
            self.importPath.emit(path)
            outPic = self.ole.text() + "/wallpaper.png"

            if not os.path.exists(self.wle.text()):
                src=os.fspath(Path(__file__).resolve().parent /"src/wallpaper.png")
                img=QImage(src)
                img.scaled(382, 100).save(outPic)
            else:
                img=QImage(self.wle.text())
                img.scaled(382,100).save(outPic)