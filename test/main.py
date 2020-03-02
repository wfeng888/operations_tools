from deploy.until import list_sqlfile
import re
from re import RegexFlag
import deploy.config
from deploy.mysql import  SimpleDeploy
import time

if '__main__' == __name__:

    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    sqlfiles = list_sqlfile('C:/Users/ZNV/Desktop/znvdb/DCVS-DB/master/DCVS-DB/1.0')
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    SimpleDeploy.exec(sqlfiles)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # v = ['1.0.2','1.0']
    # sort(v)
    # for i in  range(3,4):
    #     print(i)