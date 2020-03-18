import re
import time
import traceback
from functools import wraps

from PyQt5.QtCore import QThread

import log

getCurrentThreadID = QThread.currentThread

def formatDate(format='%Y-%m-%d'):
    return time.strftime(format,time.localtime())

def formatDateTime():
    return formatDate('%Y%m%d%H%M%S')

def isNull(param):
    return not ( param and str(param).strip() )

def stringNone(param):
    return  param and str(param).upper() == 'NONE'

def none_null_stringNone(param):
    return isNull(param) or stringNone(param)

def string_true_bool(param):
    return param and (isinstance(param,bool) or str(param).upper() == 'TRUE')

def path_join(basepath,suffixpath,sep='/'):
    if not ( isNull(basepath) and isNull(suffixpath) ):
        if not isNull(basepath):
            basepath = basepath.strip()
            if basepath[-1] == sep:
                basepath = basepath[:-1]
        if not isNull(suffixpath):
            suffixpath = suffixpath.strip()
            if suffixpath[0] != sep:
                suffixpath = sep + suffixpath
        return basepath + suffixpath


def containString(param):
    re.findall()

def record_log(func):
    @wraps(func)
    def  wrapper(*args,**kwargs):
        log.debug('begin')
        log.debug('call function %s.%s  params: args:%s,kwargs:%s'
              % (func.__qualname__,func.__name__,args,kwargs) )
        r = func(*args,**kwargs)
        log.debug('type(r):%s,r.__class__:%s' % (type(r),r.__class__) )
        log.debug('the end')
        return r
    return wrapper


def safe_doing(func,*args):
    try:
        func(*args)
    except BaseException as e:
        print(traceback.format_exc())