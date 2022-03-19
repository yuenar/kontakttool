# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

import os
import platform
import re
import stat
import sys
from pathlib import Path

import bs4
import xmltodict
from PySide6.QtCore import QSize, Signal as pyqtSignal
from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLineEdit, QPushButton, \
    QListWidgetItem, QVBoxLayout, QListWidget, QApplication
from biplist import *
import webbrowser
from elevate import elevate
from pwidget import PWidget
import applescript

isWindows= False
cpuType="Intel"
osType="Mac"

# from winreg import *
# # 1.连接注册表根键，以HKEY_LOCAL_MACHINE为例
# regRoot = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
# regUser = ConnectRegistry(None, HKEY_CURRENT_USER)


# 2.获取指定目录下所有键的控制(可用于遍历)

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
        btn=QPushButton('X ', self, clicked=self.doDeleteItem)
        btn.setFixedSize(QSize(40, 40))
        layout.addWidget(btn)

    def doDeleteItem(self):
        self.itemDeleted.emit(self._item)

    def sizeHint(self):
        # 决定item的高度
        return QSize(200, 50)

StyleSheet = """
/*这里是通用设置，所有按钮都有效，不过后面的可以覆盖这个*/
QLineEdit {
    border: transparent;
    color: #030303;
    background-color: #CBD1D5;
}
QLabel{
    outline: none;
    color:#292421;
}

QListView {
    outline: none;
}

#listWidget::item {
    background-color: #ffffff;
    color: #000000;
    border: transparent;
    border-bottom: 1px solid #dbdbdb;
    padding: 8px;
}

#listWidget::item:hover {
    background-color: #f5f5f5;
}

#listWidget::item:selected {
    border-left: 5px solid #5B6164;
}
QPushButton {
    border: none; /*去掉边框*/
    background-color: #CBD1D5;
    color:#FFFAFA;
}
/*
QPushButton#xxx
或者
#xx
都表示通过设置的objectName来指定
*/
QPushButton#RedButton {
    background-color: #f44336; /*背景颜色*/
}
#RedButton:hover {
    background-color: #e57373; /*鼠标悬停时背景颜色*/
}
/*注意pressed一定要放在hover的后面，否则没有效果*/
#RedButton:pressed {
    background-color: #ffcdd2; /*鼠标按下不放时背景颜色*/
}
QPushButton:pressed {
    background-color: #5B6164;
}
#GreenButton {
    background-color: #5B6164;
    border-radius: 5px; /*圆角*/
}
#GreenButton:hover {
    background-color: #CBD2D2;
    color:#292421;
}
#GreenButton:pressed {
    background-color: #CAD1D5;
}
#BlueButton {
    background-color: #2196f3;
    /*限制最小最大尺寸*/
    min-width: 96px;
    max-width: 96px;
    min-height: 96px;
    max-height: 96px;
    border-radius: 48px; /*圆形*/
}
#BlueButton:hover {
    background-color: #64b5f6;
}
#BlueButton:pressed {
    background-color: #bbdefb;
}
#OrangeButton {
    max-height: 48px;
    border-top-right-radius: 20px; /*右上角圆角*/
    border-bottom-left-radius: 20px; /*左下角圆角*/
    background-color: #5B6164;
}
#OrangeButton:hover {
    background-color: #CBD2D2;
    color:#292421;
}
#OrangeButton:pressed {
    background-color: #CAD1D5;
}
/*根据文字内容来区分按钮,同理还可以根据其它属性来区分*/
QPushButton[text="purple button"] {
    color: white; /*文字颜色*/
    background-color: #9c27b0;
}
"""

TARGET_XML_DIR = ""
TARGET_PLIST_DIR = "/Library/Preferences"
subDir = r'SOFTWARE\Native Instruments'
TARGET_MAC_XML_DIR = "/Library/Application Support/Native Instruments/Service Center"
TARGET_WIN_XML_DIR = "C:\\Program Files\\Common Files\\Native Instruments\\Service Center"
TARGET_PLIST_PATH = "/Library/Preferences/com.native-instruments."
# TARGET_PLIST_DIR = "/Volumes/misc/test/Preferences"
# TARGET_XML_DIR = "/Volumes/misc/test/Service Center"

RD, WD, XD = 4, 2, 1
BNS = [RD, WD, XD]
MDS = [
    [stat.S_IRUSR, stat.S_IRGRP, stat.S_IROTH],
    [stat.S_IWUSR, stat.S_IWGRP, stat.S_IWOTH],
    [stat.S_IXUSR, stat.S_IXGRP, stat.S_IXOTH]
]

def chmod(path, mode):
    if isinstance(mode, int):
        mode = str(mode)
    if not re.match("^[0-7]{1,3}$", mode):
        raise Exception("mode does not conform to ^[0-7]{1,3}$ pattern")
    mode = "{0:0>3}".format(mode)
    mode_num = 0
    for midx, m in enumerate(mode):
        for bnidx, bn in enumerate(BNS):
            if (int(m) & bn) > 0:
                mode_num += MDS[bnidx][midx]
    os.chmod(path, mode_num)

def list_all_files(rootdir):
    import os
    _files = []
    list = os.listdir(rootdir) #列出文件夹下所有的目录与文件
    for i in range(0,len(list)):
           path = os.path.join(rootdir,list[i])
           if os.path.isdir(path):
              _files.extend(list_all_files(path))
           if os.path.isfile(path):
              _files.append(path)
    return _files

def parse_ncint_mac(path):
    # f = open(path, "r", encoding='unicode_escape')
    f = open(path, "r", encoding="ISO-8859-1")
    baseName=os.path.basename(path)
    libName=baseName.replace(".nicnt", ".")

    lines = f.readlines()  # 读取全部内容 ，并以列表方式返回
    newXML='<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'

    for line in lines[1:] : #循环读取每一行，1：是从第二行开始
        if "</ProductHints>" in line:
            newXML+=line
            # print("find:==============="+line)
            f.close()
            break
        else:
            newXML += line

    f = libName + "xml"
    full_new_xml = os.path.join(TARGET_XML_DIR, f)
    # 以只写模式打开我们的文本文件以写入替换的内容
    with open(full_new_xml, 'w', encoding='UTF-8') as file:
        # 在我们的文本文件中写入替换的数据
        file.write(newXML)
    chmod(full_new_xml, "755")
    # print("xml:"+newXML)
    d = xmltodict.parse(newXML)
    spath = path.replace(baseName,"").replace("/Volumes/","").replace("/",":")
    # # spath=
    if('HU'in d["ProductHints"]["Product"]["ProductSpecific"]):
        hu=d["ProductHints"]["Product"]["ProductSpecific"]['HU']
    else:
        hu=''
    if('JDX'in d["ProductHints"]["Product"]["ProductSpecific"]):
        jdx=d["ProductHints"]["Product"]["ProductSpecific"]['JDX']
    else:
        jdx=''

    if('UPID'in d["ProductHints"]["Product"]):
        upid=d["ProductHints"]["Product"]['UPID']
    else:
        upid=''

    pls = create_plist(d["ProductHints"]["Product"]['Name'], d["ProductHints"]["Product"]['RegKey'], hu, upid, spath,jdx, d["ProductHints"]["Product"]['SNPID'])

    return full_new_xml,pls
	
def parse_ncint_win(path):
    # f = open(path, "r", encoding='unicode_escape')
    f = open(path, "r", encoding="ISO-8859-1")
    baseName=os.path.basename(path)
    libName=baseName.replace(".nicnt", ".")
    rName=baseName.replace(".nicnt", "")

    lines = f.readlines()  # 读取全部内容 ，并以列表方式返回
    newXML='<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'

    for line in lines[1:] : #循环读取每一行，1：是从第二行开始
        if "</ProductHints>" in line:
            newXML+=line
            # print("find:==============="+line)
            f.close()
            break
        else:
            newXML += line

    f = libName + "xml"
    full_new_xml = os.path.join(TARGET_XML_DIR, f)
    # 以只写模式打开我们的文本文件以写入替换的内容
    with open(full_new_xml, 'w', encoding='UTF-8') as file:
        # 在我们的文本文件中写入替换的数据
        file.write(newXML)
    chmod(full_new_xml, "755")
    # print("xml:"+newXML)
    d = xmltodict.parse(newXML)
    spath = path.replace(baseName,"").replace("/Volumes/","").replace("/",":")
    # # spath=
    if('HU'in d["ProductHints"]["Product"]["ProductSpecific"]):
        hu=d["ProductHints"]["Product"]["ProductSpecific"]['HU']
    else:
        hu=''
    if('JDX'in d["ProductHints"]["Product"]["ProductSpecific"]):
        jdx=d["ProductHints"]["Product"]["ProductSpecific"]['JDX']
    else:
        jdx=''

    if('UPID'in d["ProductHints"]["Product"]):
        upid=d["ProductHints"]["Product"]['UPID']
    else:
        upid=''

    create_reg(rName, hu, upid, spath,jdx)
    return full_new_xml


def create_reg(libName, HU,UPID,path,JDX):
    if len(libName)<1:
        return

    front=path.split("::")[0]
    back=path.split("::")[1]
    p=front+":\\"+back.replace(":","\\")
    # keyHandle = OpenKey(regRoot, subDir)
    keyHandle = OpenKey(HKEY_LOCAL_MACHINE, subDir)
    shellkey = CreateKey(keyHandle, str(libName))

    subDir_2 = r'%s\%s' % (subDir, libName)
    key = OpenKey(HKEY_LOCAL_MACHINE, subDir_2, 0, KEY_WRITE)
    SetValueEx(key, "ContentDir", 0, REG_SZ, p)
    SetValueEx(key, "ContentVersion", 0, REG_SZ, "1.0.0")
    SetValueEx(key, "HU", 0, REG_SZ, HU)
    SetValueEx(key, "JDX", 0, REG_SZ, JDX)
    SetValueEx(key, "UPID", 0, REG_SZ, UPID)
    SetValueEx(key, "Visibility", 0, REG_DWORD, 3)
    CloseKey(key)
    CloseKey(shellkey)
    CloseKey(keyHandle)

def deleteSubkey(key0, key1, key2=""):
    if key2=="":
        currentkey = key1
    else:
        currentkey = key1+ "\\" +key2

    open_key = OpenKey(key0, currentkey, 0, KEY_ALL_ACCESS)
    infokey = QueryInfoKey(open_key)
    for x in range(0, infokey[0]):
        #NOTE:: This code is to delete the key and all subkeys.
        #  If you just want to walk through them, then 
        #  you should pass x to EnumKey. subkey = EnumKey(open_key, x)
        #  Deleting the subkey will change the SubKey count used by EnumKey. 
        #  We must always pass 0 to EnumKey so we 
        #  always get back the new first SubKey.
        subkey = EnumKey(open_key, 0)
        try:
            DeleteKey(open_key, subkey)
            print("Removed %s\\%s " % (currentkey, subkey))
        except:
            deleteSubkey( key0, currentkey, subkey )
            # no extra delete here since each call 
            #to deleteSubkey will try to delete itself when its empty.

    DeleteKey(open_key,"")
    open_key.Close()
    print("Removed %s" % (currentkey))
    return


def delete_reg(libName):
    if len(libName)<1:
        return

    Parentkey = OpenKey(HKEY_LOCAL_MACHINE, subDir, 0, KEY_ALL_ACCESS)

    try:
        deleteSubkey(Parentkey, libName, '')
    except Exception as e:
        print(e)


    uParentkey = OpenKey(HKEY_CURRENT_USER, subDir, 0, KEY_ALL_ACCESS)
    try:
        deleteSubkey(uParentkey, libName, '')
    except Exception as e:
        print(e)

    CloseKey(Parentkey)
    CloseKey(uParentkey)


def create_plist(libName, RegKey, HU,UPID,path,JDX, snpid):
    f = "com.native-instruments."+libName+".plist"
    full_new_plist = os.path.join(TARGET_PLIST_DIR, f)
    src = os.fspath(Path(__file__).resolve().parent /"src/Source.plist")
    plist = readPlist(src)
    plist['Name'] = libName
    plist['RegKey'] = RegKey
    plist['SNPID'] = snpid
    plist['UPID'] = UPID
    plist['HU'] = HU
    plist['JDX'] = JDX
    plist['ContentDir'] = path

    writePlist(plist, full_new_plist)
    chmod(full_new_plist, "755")
    # print("===dst plist:" + full_new_plist)
    return full_new_plist

def judge_ktxml(apath):
    if not os.path.isfile(apath):
        return ""

    if "NativeAccess" in apath:
        return ""

    baseName = os.path.basename(apath)
    if(len(baseName)<5):
        return


    p = apath.replace("\\", "/")
    f = open(p, "r", encoding="UTF-8")
    adata = f.read()

    if isWindows:
        d = xmltodict.parse(adata)
        if "Plugin" in d["ProductHints"]["Product"]["Type"]:
            return ""
        else:
            return baseName.replace(".xml" , "")
    else:
	    d = bs4.BeautifulSoup(adata , 'xml')
	    # print(d.Type)

	    if "Content" in str(d.Type):
	        return baseName.replace(".xml" , "")
	    elif "3rdparty" in str(d.Type):
	        return baseName.replace(".xml" , "")
	    else:
	        return ""



class Widget(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("康泰克助手Kontakt Tool by OwenZhang张礼乐  {} - {}".format(osType,cpuType))
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
    def doEmail(self):
        QDesktopServices.openUrl(QUrl("mailto:yuenar2@gmail.com"))

    # def doHelper(self):
    #     self.sw.setCurrentIndex(2)

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

    def setupUi(self):
        mainLay= QVBoxLayout(self)
        layout = QHBoxLayout(self)

        # 列表
        self.listWidget = QListWidget(self)
        self.listWidget.setFixedWidth(400)
        layout.addWidget(self.listWidget)

        # //https://y.qq.com/n/ryqq/singer/0044yxPF1Zultc
        firstPageWidget = PWidget()
        firstPageWidget.importPath.connect(self.import3rdLib)
        layout.addWidget(firstPageWidget)
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

        eBtn=QPushButton("写邮件Email", self,
                                     objectName="OrangeButton", minimumHeight=48 ,clicked=self.doEmail)

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
                    print(fullname)
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

        # print(self.list)
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
        else:
            for fullname in list:  # mac
                if ".nicnt" in fullname:
                    # print(line)
                    xml, pls = parse_ncint_mac(fullname)
                    # print("parse:" + fullname+"==to=="+xml)
                    self.add2listView(xml)
                    self.plistVector.append(pls)

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



