# This Python file uses the following encoding: utf-8
# -*- coding: utf-8 -*-

import bs4
import xmltodict
import os,sys
import  images
from config import *
from biplist import *
from PySide6.QtCore import QUrl,QDir,QCoreApplication

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
        d = xmltodict.parse(adata)
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
        # url = os.path.dirname(os.path.abspath(__file__))
        url = os.path.dirname(sys.argv[0])
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
    url = os.path.dirname(sys.argv[0])
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