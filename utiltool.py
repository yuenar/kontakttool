# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

import bs4
import xmltodict
import os,sys
import  images
from config import *
from biplist import *
from PyQt5.QtCore import QUrl,QDir,QCoreApplication
# import wmi
# from winreg import *
# # 1.连接注册表根键，以HKEY_LOCAL_MACHINE为例
# regRoot = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
# regUser = ConnectRegistry(None, HKEY_CURRENT_USER)

# 功能说明： 用户运行程序后自动检测认证状态：
#  1. 检测到有注册文件时，注册文件中的注册码和DES+base64加密的注册码比较，若一致，则通过认证，进入主程序。
#  2. 未检测到注册文件或者注册文件中的注册码与DES+base64加密的注册码不一致,则提醒用户输入注册码或重新获取注册码。
#     重新获取注册码会将程序运行后显示的机器码 161k8Z  发送给指定管理员，管理员经过编码生成注册码给回用户，同时生成注册文件。

import uuid
import base64
import zlib
from passlib.hash import sha256_crypt

from PyQt5.QtCore import QCoreApplication
import base64
import pyDes


class RegisterClass:
    def __init__(self):
        self.Des_Key = "miuzhang"  # Key,需八位
        self.Des_IV = "\x11\2\x2a\3\1\x27\2\0"  # 自定IV向量

    # # 获取硬件信息，输出macode
    # # 1、CPU序列号（ID）  2、本地连接 无线局域网 以太网的MAC  3.硬盘序列号（唯一） 4.主板序列号（唯一）
    # global s
    # s = wmi.WMI()
    #
    # # cpu序列号
    # def get_CPU_info(self):
    #     cpu = []
    #     cp = s.Win32_Processor()
    #     for u in cp:
    #         cpu.append(
    #             {
    #                 "Name": u.Name,
    #                 "Serial Number": u.ProcessorId,
    #                 "CoreNum": u.NumberOfCores
    #             }
    #         )
    #     return cpu
    #
    # # 硬盘序列号
    # def get_disk_info(self):
    #     disk = []
    #     for pd in s.Win32_DiskDrive():
    #         disk.append(
    #             {
    #                 "Serial": s.Win32_PhysicalMedia()[0].SerialNumber.lstrip().rstrip(),  # 获取硬盘序列号，调用另外一个win32 API
    #                 "ID": pd.deviceid,
    #                 "Caption": pd.Caption,
    #                 "size": str(int(float(pd.Size) / 1024 / 1024 / 1024))
    #             }
    #         )
    #     return disk
    #
    # # mac地址（包括虚拟机的）
    # def get_network_info(self):
    #     network = []
    #     for nw in s.Win32_NetworkAdapterConfiguration():
    #         if nw.MacAddress != None:
    #             network.append(
    #                 {
    #                     "MAC": nw.MacAddress,
    #                     "ip": nw.IPAddress
    #                 }
    #             )
    #     return network
    #
    # # 主板序列号
    # def get_mainboard_info(self):
    #     mainboard = []
    #     for board_id in s.Win32_BaseBoard():
    #         mainboard.append(board_id.SerialNumber.strip().strip('.'))
    #     return mainboard
    #
    # #  由于机器码太长，故选取机器码字符串部分字符
    # #  E0:DB:55:B5:9C:16BFEBFBFF00040651W3P0VKEL6W8T1Z1.CN762063BN00A8
    # #  1 61 k 8Z
    # #     machinecode_str = ""
    # #     machinecode_str = machinecode_str+a[0]['MAC']+b[0]['Serial Number']+c[0]['Serial']+d[0]
    # def getCombinNumber(self):
    #     a = self.get_network_info()
    #     b = self.get_CPU_info()
    #     c = self.get_disk_info()
    #     d = self.get_mainboard_info()
    #     machinecode_str = ""
    #     machinecode_str = machinecode_str + a[0]['MAC'] + b[0]['Serial Number'] + c[0]['Serial'] + d[0]
    #     selectindex = [15, 30, 32, 38, 43, 46]
    #     macode = ""
    #     for i in selectindex:
    #         macode = macode + machinecode_str[i]
    #     ###   #print(macode)
    #     return macode


    def DesEncrypt(self, str):
        k = pyDes.des(self.Des_Key, pyDes.CBC, self.Des_IV, pad=None, padmode=pyDes.PAD_PKCS5)
        encryptStr = k.encrypt(str)
        string = base64.b64encode(encryptStr)
        # #print(string)
        return string  # 转base64编码返回

    def DesDecrypt(self, string):
        string = base64.b64decode(string)
        k = pyDes.des(self.Des_Key, pyDes.CBC, self.Des_IV, pad=None, padmode=pyDes.PAD_PKCS5)
        decryptStr = k.decrypt(string)
        # #print(decryptStr)
        return decryptStr

    # #des+base64解码
    # def DesDecrypt(self,tr):
    #     k = des(self.Des_Key, CBC, self.Des_IV, pad=None, padmode=PAD_PKCS5)
    #     DecryptStr = k.decrypt(tr)
    #     return base64.b64decode(DecryptStr) #转base64解码返回

def get_path(p):
    s=p.replace("src","images")
    path=":/"+s
    #print("======"+path)
    return path



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
        d = xml2dict.parse(adata)
        if "Plugin" in d["ProductHints"]["Product"]["Type"]:
            return ""
        else:
            return baseName.replace(".xml" , "")
    else:
	    d = bs4.BeautifulSoup(adata , 'xml')
	    # #print(d.Type)

	    if "Content" in str(d.Type):
	        return baseName.replace(".xml" , "")
	    elif "3rdparty" in str(d.Type):
	        return baseName.replace(".xml" , "")
	    else:
	        return ""

def judge_plist(apath):
    list=list_all_files(TARGET_PLIST_DIR,True)
    picPath=""
    for fullname in list:  # mac
        if apath in fullname:
            # #print(line)
            plist= readPlist(fullname)
            picPath="/Volumes/"+plist['ContentDir'].replace(":","/")+"wallpaper.png"
            break


    return picPath

def create_nicnt(compyName,libName,snpid,path):
    if os.path.isdir(path):
        url = os.path.dirname(os.path.abspath(__file__))
        src=os.path.join(url,"src/Source.nicnt")
        fullname=libName+".nicnt"
        fullpath=os.path.join(path,fullname)

        fp3 = open(src, "r", encoding="ISO-8859-1")
        fp4 = open(fullpath, "w")

        for s in fp3.readlines():  # 先读出来
            fp4.write(s.replace("libName", libName).replace("sid",snpid).replace("compName",compyName))  # 替换 并写入

        fp3.close()
        fp4.close()
        # #print("done")
        return fullpath

def list_all_files(rootdir,is_iter):

    _files = []
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isdir(path) and is_iter :
            _files.extend(list_all_files(path,True))
        if os.path.isfile(path):
            _files.append(path)
    return _files

def list_dir_files(rootdir):

    _files = []
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isfile(path):
            _files.append(path)
    return _files


def parse_ncint_mac(path):
    # f = open(path, "r", encoding='unicode_escape')
    f = open(path, "r", encoding="ISO-8859-1")
    baseName = os.path.basename(path)
    libName = baseName.replace(".nicnt", ".")

    lines = f.readlines()  # 读取全部内容 ，并以列表方式返回

    if(len(lines)<2):
        return "",""

    newXML = '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'

    for line in lines[1:]:  # 循环读取每一行，1：是从第二行开始
        if "</ProductHints>" in line:
            newXML += line
            # #print("find:==============="+line)
            f.close()
            break
        else:
            newXML += line

    f = libName + "xml"
    full_new_xml = os.path.join(TARGET_MAC_XML_DIR, f)
    # 以只写模式打开我们的文本文件以写入替换的内容
    with open(full_new_xml, 'w', encoding='UTF-8') as file:
        # 在我们的文本文件中写入替换的数据
        file.write(newXML)
    chmod(full_new_xml, "755")
    # #print("create xml:"+newXML)
    d = xmltodict.parse(newXML)
    spath = path.replace(baseName, "").replace("/Volumes/", "").replace("/", ":")
    # # spath=
    if ('HU' in d["ProductHints"]["Product"]["ProductSpecific"]):
        hu = d["ProductHints"]["Product"]["ProductSpecific"]['HU']
    else:
        hu = ''
    if ('JDX' in d["ProductHints"]["Product"]["ProductSpecific"]):
        jdx = d["ProductHints"]["Product"]["ProductSpecific"]['JDX']
    else:
        jdx = ''

    if ('UPID' in d["ProductHints"]["Product"]):
        upid = d["ProductHints"]["Product"]['UPID']
    else:
        upid = ''

    pls = create_plist(d["ProductHints"]["Product"]['Name'], d["ProductHints"]["Product"]['RegKey'], hu, upid, spath,
                       jdx, d["ProductHints"]["Product"]['SNPID'])

    return full_new_xml, pls

def create_plist(libName, RegKey, HU, UPID, path, JDX, snpid):
    f = "com.native-instruments." + libName + ".plist"
    full_new_plist = os.path.join(TARGET_PLIST_DIR, f)
    # src = get_path( "src/Source.plist")
    url = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(url, "src/Source.plist")
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
    # #print("===dst plist:" + full_new_plist)
    return full_new_plist