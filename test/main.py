import os
from pathlib import Path

from deploy.until import list_sqlfile, _sort, valid
from deploy.mysql import  SimpleDeploy
import time






def list_sqlfile_new(filepath):
    base = Path(filepath)
    if base.exists():
        if base.is_dir():
            curlist = {}
            num = 0
            curdir = os.path.split(filepath)[1]
            subfiles = _sort([i for i in os.listdir(filepath) if valid(os.path.join(filepath,i))])
            curfiles = []
            for i in subfiles:
                if os.path.isdir(os.path.join(filepath,i)):
                    s = list_sqlfile_new(os.path.join(filepath,i))
                    if s[0]:
                        num = num+s[1]
                        curfiles.append(s[0])
                else:
                    curfiles.append(os.path.join(filepath,i))
                    num = num + 1
            if curfiles:
                curlist[curdir] = curfiles
                return curlist,num
            else:
                return None,0
        else:
            if os.path.splitext(filepath)[1].upper() == '.SQL':
                return filepath,1
    return None,0

if '__main__' == __name__:
    sqlfiles,num = list_sqlfile_new('C:/Users/ZNV/Desktop/znvdb/DCVS-DB/master/DCVS-DB/1.0')
    print(num)
    print(sqlfiles)
    # SimpleDeploy.exec(sqlfiles)
    # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # v = ['1.0.2','1.0']
    # sort(v)
    # for i in  range(3,4):
    #     print(i)