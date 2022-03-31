# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

import bs4
import xmltodict
import os,sys

from config import *
from biplist import *

from winreg import *
# 1.连接注册表根键，以HKEY_LOCAL_MACHINE为例
regRoot = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
regUser = ConnectRegistry(None, HKEY_CURRENT_USER)

# 功能说明： 用户运行程序后自动检测认证状态：
#  1. 检测到有注册文件时，注册文件中的注册码和DES+base64加密的注册码比较，若一致，则通过认证，进入主程序。
#  2. 未检测到注册文件或者注册文件中的注册码与DES+base64加密的注册码不一致,则提醒用户输入注册码或重新获取注册码。
#     重新获取注册码会将程序运行后显示的机器码 161k8Z  发送给指定管理员，管理员经过编码生成注册码给回用户，同时生成注册文件。

import uuid
import base64
import zlib
from passlib.hash import sha256_crypt

import wmi
import base64
import pyDes


class RegisterClass:
    def __init__(self):
        self.Des_Key = "miuzhang"  # Key,需八位
        self.Des_IV = "\x11\2\x2a\3\1\x27\2\0"  # 自定IV向量

    # 获取硬件信息，输出macode
    # 1、CPU序列号（ID）  2、本地连接 无线局域网 以太网的MAC  3.硬盘序列号（唯一） 4.主板序列号（唯一）
    global s
    s = wmi.WMI()

    # cpu序列号
    def get_CPU_info(self):
        cpu = []
        cp = s.Win32_Processor()
        for u in cp:
            cpu.append(
                {
                    "Name": u.Name,
                    "Serial Number": u.ProcessorId,
                    "CoreNum": u.NumberOfCores
                }
            )
        return cpu

    # 硬盘序列号
    def get_disk_info(self):
        disk = []
        for pd in s.Win32_DiskDrive():
            disk.append(
                {
                    "Serial": s.Win32_PhysicalMedia()[0].SerialNumber.lstrip().rstrip(),  # 获取硬盘序列号，调用另外一个win32 API
                    "ID": pd.deviceid,
                    "Caption": pd.Caption,
                    "size": str(int(float(pd.Size) / 1024 / 1024 / 1024))
                }
            )
        return disk

    # mac地址（包括虚拟机的）
    def get_network_info(self):
        network = []
        for nw in s.Win32_NetworkAdapterConfiguration():
            if nw.MacAddress != None:
                network.append(
                    {
                        "MAC": nw.MacAddress,
                        "ip": nw.IPAddress
                    }
                )
        return network

    # 主板序列号
    def get_mainboard_info(self):
        mainboard = []
        for board_id in s.Win32_BaseBoard():
            mainboard.append(board_id.SerialNumber.strip().strip('.'))
        return mainboard

    #  由于机器码太长，故选取机器码字符串部分字符
    #  E0:DB:55:B5:9C:16BFEBFBFF00040651W3P0VKEL6W8T1Z1.CN762063BN00A8
    #  1 61 k 8Z
    #     machinecode_str = ""
    #     machinecode_str = machinecode_str+a[0]['MAC']+b[0]['Serial Number']+c[0]['Serial']+d[0]
    def getCombinNumber(self):
        a = self.get_network_info()
        b = self.get_CPU_info()
        c = self.get_disk_info()
        d = self.get_mainboard_info()
        machinecode_str = ""
        machinecode_str = machinecode_str + a[0]['MAC'] + b[0]['Serial Number'] + c[0]['Serial'] + d[0]
        selectindex = [15, 30, 32, 38, 43, 46]
        macode = ""
        for i in selectindex:
            macode = macode + machinecode_str[i]
        ###   print(macode)
        return macode


    def DesEncrypt(self, str):
        k = pyDes.des(self.Des_Key, pyDes.CBC, self.Des_IV, pad=None, padmode=pyDes.PAD_PKCS5)
        encryptStr = k.encrypt(str)
        string = base64.b64encode(encryptStr)
        # print(string)
        return string  # 转base64编码返回

    def DesDecrypt(self, string):
        string = base64.b64decode(string)
        k = pyDes.des(self.Des_Key, pyDes.CBC, self.Des_IV, pad=None, padmode=pyDes.PAD_PKCS5)
        decryptStr = k.decrypt(string)
        # print(decryptStr)
        return decryptStr

    # #des+base64解码
    # def DesDecrypt(self,tr):
    #     k = des(self.Des_Key, CBC, self.Des_IV, pad=None, padmode=PAD_PKCS5)
    #     DecryptStr = k.decrypt(tr)
    #     return base64.b64decode(DecryptStr) #转base64解码返回

    # 获取注册码，验证成功后生成注册文件
    def regist(self,key_decrypted):
        # key = input('please input your register code: ')
        # 由于输入类似“12”这种不符合base64规则的字符串会引起异常，所以需要增加输入判断
        idcode = self.getCombinNumber()
        content = self.DesEncrypt(idcode)
        # # key_decrypted = bytes(key, encoding='utf-8')
        # key_decrypted = bytes(key, encoding='utf-8')
        print(content)
        if content != 0 and key_decrypted != 0:
            if content != key_decrypted:
                print("wrong register code, please check and input your register code again:")
                # self.regist()
            elif content == key_decrypted:
                print("register succeed.")
                if isWindows:
                    self.regist_win(key_decrypted)
                else:
                    self.regist_mac(key_decrypted)

                return True
            else:
                return False
        else:
            return False
        # else:
        #     self.regist()
        #     return False

    def regist_win(self,key):

        keys=str(key, encoding='utf-8')
        # 读写文件要加判断
        f = "kontakt-tool.re"
        full_new_re = os.path.join(TARGET_WIN_XML_DIR, f)

        with open(full_new_re, 'w') as f:
            f.write(keys)
            f.close()
            print("regist_win:" + keys)

    def regist_mac(self,key):
        print("regist_mac:"+key)
        f = "kontakt-tool.re"
        full_new_re = os.path.join(TARGET_MAC_XML_DIR, f)

        with open(full_new_re, 'w') as f:
            f.write(key)
            f.close()


    # 打开程序先调用注册文件，比较注册文件中注册码与此时获取的硬件信息编码后是否一致
    def checkAuthored(self):
        ontent = self.getCombinNumber()
        tent = bytes(ontent, encoding='utf-8')
        content = self.Encrypted(tent)
        if isWindows:
            f = "kontakt-tool.re"
            rePath = os.path.join(TARGET_WIN_XML_DIR, f)
        else:
            f = "kontakt-tool.re"
            rePath = os.path.join(TARGET_MAC_XML_DIR, f)


        # 读写文件要加判断
        try:
            # fc = open(rePath, 'x')
            # if fc:
            #     print("first using.")
            #     fc.write(ontent)
            #     fc.close()


            f = open(rePath, 'r')
            if f:
                key = f.read()
                if key:
                    key_decrypted = bytes(key, encoding='utf-8')  # 注册文件中注册码
                    ###              print('key_decrypted:',key_decrypted)
                    ###              print('content:',content)
                    if key_decrypted:
                        if key_decrypted == content:
                            print("register succeed.")
                            ##      checkAuthoredResult = 1  # 注册文件与机器码一致
                        else:
                            ##        checkAuthoredResult = -1 # 注册文件与机器码不一致
                            print('未找到注册文件，', '请重新输入注册码，', '或发送', ontent, '至17695797270', '重新获取注册码')
                            self.regist()
                    else:
                        ##       checkAuthoredResult = -2     # 注册文件的注册码不能被解析
                        self.regist()
                        print('未找到注册文件，', '请重新输入注册码，', '或发送', ontent, '至17695797270', '重新获取注册码')
                else:
                    ##         checkAuthoredResult = -3         # 注册文件中不能被读取
                    self.regist()
                    print('未找到注册文件，', '请重新输入注册码，', '或发送', ontent, '至17695797270', '重新获取注册码')
            else:
                self.regist()
        except:
            print('请发送', ontent, '至17695797270', '获取注册码')
            ##  checkAuthoredResult = 0                      # 未找到注册文件，请重新输入注册码登录
            self.regist()
    ##    print(checkAuthoredResult)
    ##   return checkAuthoredResult

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

def list_all_files(rootdir):

    _files = []
    list = os.listdir(rootdir)  # 列出文件夹下所有的目录与文件
    for i in range(0, len(list)):
        path = os.path.join(rootdir, list[i])
        if os.path.isdir(path):
            _files.extend(list_all_files(path))
        if os.path.isfile(path):
            _files.append(path)
    return _files


def parse_ncint_mac(path):
    # f = open(path, "r", encoding='unicode_escape')
    f = open(path, "r", encoding="ISO-8859-1")
    baseName = os.path.basename(path)
    libName = baseName.replace(".nicnt", ".")

    lines = f.readlines()  # 读取全部内容 ，并以列表方式返回
    newXML = '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'

    for line in lines[1:]:  # 循环读取每一行，1：是从第二行开始
        if "</ProductHints>" in line:
            newXML += line
            # print("find:==============="+line)
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
    # print("create xml:"+newXML)
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


def parse_ncint_win(path):
    # f = open(path, "r", encoding='unicode_escape')
    f = open(path, "r", encoding="ISO-8859-1")
    baseName = os.path.basename(path)
    libName = baseName.replace(".nicnt", ".")
    rName = baseName.replace(".nicnt", "")

    lines = f.readlines()  # 读取全部内容 ，并以列表方式返回
    newXML = '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>\n'

    for line in lines[1:]:  # 循环读取每一行，1：是从第二行开始
        if "</ProductHints>" in line:
            newXML += line
            # print("find:==============="+line)
            f.close()
            break
        else:
            newXML += line

    f = libName + "xml"
    full_new_xml = os.path.join(TARGET_WIN_XML_DIR, f)
    # 以只写模式打开我们的文本文件以写入替换的内容
    with open(full_new_xml, 'w', encoding='UTF-8') as file:
        # 在我们的文本文件中写入替换的数据
        file.write(newXML)
    chmod(full_new_xml, "755")
    print("new xml:"+newXML)
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

    create_reg(rName, hu, upid, spath, jdx)
    return full_new_xml


def create_reg(libName, HU, UPID, path, JDX):
    if len(libName) < 1:
        return

    front = path.split("::")[0]
    back = path.split("::")[1]
    p = front + ":\\" + back.replace(":", "\\")
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
    if key2 == "":
        currentkey = key1
    else:
        currentkey = key1 + "\\" + key2

    open_key = OpenKey(key0, currentkey, 0, KEY_ALL_ACCESS)
    infokey = QueryInfoKey(open_key)
    for x in range(0, infokey[0]):
        # NOTE:: This code is to delete the key and all subkeys.
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
            deleteSubkey(key0, currentkey, subkey)
            # no extra delete here since each call
            # to deleteSubkey will try to delete itself when its empty.

    DeleteKey(open_key, "")
    open_key.Close()
    print("Removed %s" % (currentkey))
    return


def delete_reg(libName):
    if len(libName) < 1:
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


def create_plist(libName, RegKey, HU, UPID, path, JDX, snpid):
    f = "com.native-instruments." + libName + ".plist"
    full_new_plist = os.path.join(TARGET_PLIST_DIR, f)
    src = os.fspath(Path(__file__).resolve().parent / "src/Source.plist")
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