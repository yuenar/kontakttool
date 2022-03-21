# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

import stat
import re
import os,sys
from pathlib import Path

isWindows= False
cpuType = "Intel"
osType = "Mac"
bankCounts=0

StyleSheet = """
/*这里是通用设置，所有按钮都有效，不过后面的可以覆盖这个*/
QLineEdit {
    border: transparent;
    color: #5B6164;
    background-color: #CBD1D5;
}
QWidget{
    font-family: "STFangsong";
}
QLabel{
    outline: none;
    color:#5B6164;
    font: bold italic 14px
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
    font: bold 
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
    background-color: #5B6164;
    /*限制最小最大尺寸*/
    min-width: 36px;
    max-width: 36px;
    min-height: 36px;
    max-height: 36px;
    border-radius: 18px; /*圆形*/
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