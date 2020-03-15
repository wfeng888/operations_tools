import re
import time

from PyQt5.QtCore import QThread

getCurrentThreadID = QThread.currentThread

def formatDate(format='%Y-%m-%d'):
    return time.strftime(format,time.localtime())

def formatDateTime():
    return formatDate('%Y%m%d%H%M%S')

def isNull(param):
    return not ( param and param.strip() )

def stringNone(param):
    return  param and param.upper() == 'NONE'

def none_null_stringNone(param):
    return isNull(param) or stringNone()

def containString(param):
    re.findall()