# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

import os
import platform

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, \
     QVBoxLayout, QListWidget, QApplication,QLabel

from config import *
from elevate import elevate
from pwidget import PWidget
from listwidget import *
from utiltool import *
import applescript

class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("音色库管理工具Kontakt Tool by OwenZhang张礼乐  {} - {}".format(osType,cpuType))
        self.dialog = QFileDialog()
        self.list=[]
        self.plistVector=[]
        self.setupUi()

        # dpi = screen.logicalDotsPerInch() * screen.devicePixelRatio()
        # density = dpi / 160.0

        # self.resize(800*density, 600*density)
        # self.setMinimumSize(800,600)
        # self.setMaximumSize(800*density,600*density)

        self.resize(800, 600)
        self.setMinimumSize(800,600)
        self.setMaximumSize(800,600)

        self.getFullLibs()
    #     # 鼠标移动
    # def mouseMoveEvent(self, event):
    #     if event.buttons() == Qt.LeftButton and self._mouse_pos:
    #         self.parent().move(self.mapToGlobal(event.pos() - self._mouse_pos))
    #     event.accept()  # 接受事件,不传递到父控件
    #
    # def mousePressEvent(self, event):
    #     if event.button() == Qt.LeftButton:
    #         self._mouse_pos = event.pos()
    #     event.accept()  # 接受事件,不传递到父控件
    #
    # def mouseReleaseEvent(self, event):
    #     self._mouse_pos = None
    #     event.accept()  # 接受事件,不传递到父控件


    def doDeleteItem(self, item):
        # 根据item得到它对应的行数
        if isWindows:
            row = self.listWidget.indexFromItem(item).row()
            # 删除item

            name=self.list[row]
            item = self.listWidget.takeItem(row)

            realname = item.text()
            if (realname in name):
                print("del WENJIAN:" + name)
                os.remove(name)

            if len(realname)<1:
                baseName=os.path.basename(name)
                realname=baseName.replace(".xml","")

            print("del ReG:" + realname)
            delete_reg(realname)
            del self.list[row]
            # 删除widget
            self.listWidget.removeItemWidget(item)
            del item
        else:
            row = self.listWidget.indexFromItem(item).row()
            # 删除item

            name=self.list[row]
            if os.path.exists(name):
                os.remove(name)
                baseName = os.path.basename(name).split(".")[0]
                print("base"+baseName)
                for x in self.plistVector:
                    if baseName in x:
                        self.plistVector.remove(x)
                        if os.path.exists(x):
                            os.remove(x)
                            print("del:"+x)

            del self.list[row]
            item = self.listWidget.takeItem(row)

            # 删除widget
            self.listWidget.removeItemWidget(item)
            del item
        self.updateTile()

    def updateTile(self):
        self.titleLine.setText('已加载 {} 套音色'.format(self.listWidget.count()))

    def doClearItem(self):
        if(self.listWidget.count()<1):
            return

        msgBox = QMessageBox(self)
        msgBox.resize(360,240)
        msgBox.setWindowTitle('警告Warning')
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText("是否清空所有入库音色？操作不可还原！Clear all banked tones? The operation is irreversible!")
        okButton = msgBox.addButton(self.tr("确定Go on"), QMessageBox.ActionRole)
        okButton.clicked.connect(self.realClear)
        msgBox.exec()

    def realClear(self):
        # 清空所有Item
        if isWindows:
            for _ in range(self.listWidget.count()):
                # 删除item
                # 一直是0的原因是一直从第一行删,删掉第一行后第二行变成了第一行
                # 这个和删除list [] 里的数据是一个道理

                item = self.listWidget.takeItem(0)
                name = self.list[0]
                realname = item.text()


                if(realname in name):
                    print("del WENJIAN:" + name)
                    os.remove(name)

                if len(realname) < 1:
                    baseName = os.path.basename(name)
                    realname = baseName.replace(".xml", "")
                print("del ReG:" + realname)
                delete_reg(realname)

                # 删除widget
                self.listWidget.removeItemWidget(item)
                del item
                del self.list[0]
        else:
            while self.listWidget.count() > 0:
                item = self.listWidget.item(0)
                self.doDeleteItem(item)
            self.plistVector.clear()

        self.listWidget.clear()
        self.list.clear()
        self.updateTile()
    def doVisit(self):
        # QDesktopServices.openUrl(QUrl("mailto:yuenar2@gmail.com"))
        QDesktopServices.openUrl(QUrl("https://tools.pro-music.cn/"))

    def doHelper(self):
        self.sw.setCurrentIndex(2)

    def doDonate(self):
        msgBox = QMessageBox(self)
        msgBox.resize(360,240)
        # msgBox.setText("Alipay支付宝")
        msgBox.setInformativeText("支付宝向我捐赠？Donate by alipay?")
        src = os.fspath(Path(__file__).resolve().parent /"src/alipay.png")
        p = QPixmap(src)
        msgBox.setIconPixmap(p.scaled(256, 256))
        palButton = msgBox.addButton(self.tr("Or Paypal或贝宝？"), QMessageBox.ActionRole)
        palButton.clicked.connect(self.paypal)
        msgBox.exec()

    def paypal(self):
        QDesktopServices.openUrl(QUrl("https://www.paypal.com/paypalme/yuenar"))

    def doFollow(self):
        QDesktopServices.openUrl(QUrl("https://y.qq.com/n/ryqq/singer/0044yxPF1Zultc"))

    def randomData(self):
        self.la

    def setupUi(self):
        mainLay= QVBoxLayout(self)
        layout = QHBoxLayout(self)
        vLay = QVBoxLayout(self)

        # 列表
        self.listWidget = QListWidget(self)
        self.titleLine = QLabel(self)
        self.titleLine.setEnabled(False)
        self.titleLine.resize(378,20)
        self.titleLine.move(13,0)

        # self.titleLine.setText('已加载 {} 套音色'.format(self.listWidget.count()))

        self.listWidget.setFixedWidth(384)
        # self.listWidget.itemSelectionChanged.connect(self.updateTile)
        # self.listWidget.currentItemChanged.connect(self.updateTile)
        # vLay.addWidget(self.titleLine)
        layout.addWidget(self.listWidget)

        # //https://y.qq.com/n/ryqq/singer/0044yxPF1Zultc
        firstPageWidget = PWidget()
        firstPageWidget.importPath.connect(self.import3rdLib)
        layout.addWidget(firstPageWidget)

        mainLay.addLayout(vLay)
        mainLay.addLayout(layout)

        hVl = QHBoxLayout(self)
        # 清空按钮
        self.clearBtn = QPushButton('清空音色Clear libs', self, objectName="OrangeButton", minimumHeight=48 ,clicked=self.doClearItem)
        hVl.addWidget(self.clearBtn)

        fBtn=QPushButton("批量导入Import libs", self,
                                     objectName="OrangeButton", minimumHeight=48 ,clicked=self.open_ni_dir)

        tBtn=QPushButton("捐赠Donate", self,
                                     objectName="OrangeButton", minimumHeight=48 ,clicked=self.doDonate)

        oBtn=QPushButton("关注作者Follow", self,
                                     objectName="OrangeButton", minimumHeight=48 ,clicked=self.doFollow)

        eBtn=QPushButton("访问官网HomePage", self,
                                     objectName="OrangeButton", minimumHeight=48 ,clicked=self.doVisit)

        hVl.addWidget(fBtn)
        hVl.addWidget(tBtn)
        hVl.addWidget(oBtn)
        hVl.addWidget(eBtn)
        mainLay.addLayout(hVl)
        self.setLayout(mainLay)

    def getFullLibs(self):
        if isWindows:

            keyHandle = OpenKey(HKEY_LOCAL_MACHINE, subDir)
            count = QueryInfoKey(keyHandle)[0]  # 获取该目录下所有键的个数(0-下属键个数;1-当前键值个数)
            for i in range(count):
                # 3.穷举每个键，获取键名
                subKeyName = EnumKey(keyHandle, i)

                if "Kontakt Application" not in subKeyName:
                    # print(subKeyName)

                    subDir_2 = r'%s\%s' % (subDir, subKeyName)
                    # 4.根据获取的键名拼接之前的路径作为参数，获取当前键下所属键的控制
                    keyHandle_2 = OpenKey(regRoot, subDir_2)
                    # count2 = QueryInfoKey(keyHandle_2)[1]
                    # for j in range(count2):
                    #     # 5.穷举每个键，获取键名、键值以及数据类型
                    # name, value, type = EnumValue(keyHandle_2, 0)
                    aname=TARGET_WIN_XML_DIR+"\\"+subKeyName+".xml"
                    fullname=aname.replace("\\","/")
                    self.add2listView(fullname)

                    CloseKey(keyHandle_2)  # 读写操作结束后关闭键
            CloseKey(keyHandle)

        else:
            if not os.path.exists(TARGET_PLIST_DIR):
               os.makedirs(TARGET_PLIST_DIR)

            if not os.path.exists(TARGET_XML_DIR):
               os.makedirs(TARGET_XML_DIR)

            list=list_all_files(TARGET_XML_DIR)
            for fullname in list:  # 循环读取每一行，1：是从第二行开始
                if ".xml" in fullname:
                    self.add2listView(fullname)

            plist=list_all_files(TARGET_PLIST_DIR)
            for pullname in plist:  # 循环读取每一行，1：是从第二行开始
                if "com.native-instruments." in pullname:
                    self.plistVector.append(pullname)

    def add2listView(self,fullname):
        n = judge_ktxml(fullname)
        if (len(str(n)) < 1):
            return

        if(fullname in self.list):
            return

        item = QListWidgetItem(self.listWidget)
        item.setSizeHint(QSize(380, 42))
        # widget = ItemWidget('已导入Exist:    {}'.format(n), item, self.listWidget)
        widget = ItemWidget('{}'.format(n), item, self.listWidget)
        widget.setFixedSize(QSize(380, 42))
        # 绑定删除信号
        widget.itemDeleted.connect(self.doDeleteItem)
        self.listWidget.setItemWidget(item, widget)
        self.list.append(fullname)
        self.updateTile()

    def open_ni_dir(self):
        if not os.path.exists(TARGET_PLIST_DIR):
           os.makedirs(TARGET_PLIST_DIR)

        if not os.path.exists(TARGET_XML_DIR):
           os.makedirs(TARGET_XML_DIR)

        lib_dir = self.dialog.getExistingDirectory(self, "选取文件夹", os.getcwd())

        if len(lib_dir)<1:
            return

        list = list_all_files(lib_dir)
        if isWindows :
            for fullname in list:  # 循环读取每一行，1：是从第二行开始
                if ".nicnt" in fullname:
                    # print(line)
                    xml = parse_ncint_win(fullname)
                    # print("parse:" + fullname+"==to=="+xml)
                    self.add2listView(xml)
                    continue
                    # break
        else:
            for fullname in list:  # mac
                if ".nicnt" in fullname:
                    # print(line)
                    xml, pls = parse_ncint_mac(fullname)
                    # print("parse:" + fullname+"==to=="+xml)
                    self.add2listView(xml)
                    self.plistVector.append(pls)
                    continue

    def import3rdLib(self,path):
        if isWindows:
            xml =parse_ncint_win(path)
            self.add2listView(xml)
        else:
            xml, pls = parse_ncint_mac(path)
            # print("parse:" + fullname+"==to=="+xml)
            self.add2listView(xml)
            self.plistVector.append(pls)

if __name__ == "__main__":
    #   获取操作系统可执行程序的结构，，(’32bit’, ‘WindowsPE’)
    if "Windows" in str(platform.architecture()):
        isWindows = True
        TARGET_XML_DIR=TARGET_WIN_XML_DIR
    else:
        isWindows = False
        TARGET_XML_DIR = TARGET_MAC_XML_DIR

    if isWindows:
        # print(platform.architecture())

        elevate(show_console=False)
        akeyHandle = CreateKey(HKEY_LOCAL_MACHINE, subDir)
        akey1Handle = CreateKey(HKEY_CURRENT_USER, subDir)
        CloseKey(akeyHandle)
        CloseKey(akey1Handle)
    else:
	    elevate()
    	# elevate(graphical=False)
        # if os.geteuid() != 0:
        #     # print(platform.architecture())
        #
        #     # elevate(show_console=False)
        # # elevate(graphical=True)
        #     # applescript.AppleScript('display dialog "程序需要完整磁盘权限，App need full disk access." giving up after 2').run()
        #     # webbrowser.open('x-apple.systempreferences:com.apple.preference.security?Privacy')
        #     # print("This program must be run as root.Or aborting.")
        #     # cmd = os.fspath(Path(__file__).resolve().parent / "src/run.sh")
        #     # os.system(cmd)
        #     # os.system("open -a Terminal .")
        #     applescript.AppleScript('display dialog "程序需要输入用户密码，App need input user password." giving up after 2').run()
        #     applescript.AppleScript('''tell application "Terminal"
        #                                     activate
        #                                     set newTab to do script "sudo /Applications/kontakt-tool.app/Contents/MacOS/kontakt-tool"
        #                                  end tell
        #                             '''
        #                             ).run()
        #     sys.exit(-1)

    # #   计算机的网络名称，’acer-PC’
    # print(platform.node())
    #
    # # 获取操作系统名称及版本号，’Windows-7-6.1.7601-SP1′
    # print(platform.platform())
    osType=platform.platform().split("-")[0]
    # 计算机处理器信息，’Intel64 Family 6 Model 42 Stepping 7, GenuineIntel’
    cpuType=platform.processor().split(" ")[0]

    # # 获取操作系统中Python的构建日期
    # print(platform.python_build())
    #
    # #  获取系统中python解释器的信息
    # print(platform.python_compiler())

    app = QApplication([])
    window = QWidget()
    screen = QApplication.primaryScreen()

    app.setStyleSheet(StyleSheet)
    window = Widget()

    window.show()
    window.move((1920-1080)*0.5,100)
    # window.test()
    # window.getFullLibs()
    # window.open_ni_dir()
    sys.exit(app.exec())



