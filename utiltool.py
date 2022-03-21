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