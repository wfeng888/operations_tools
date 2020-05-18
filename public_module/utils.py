import re
import time
import traceback
from functools import wraps

from PyQt5.QtCore import QThread

import log
from public_module import to_text

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
    if isinstance(param,(tuple,list)):
        for i in param:
            if not none_null_stringNone(i):
                return False
        return True
    elif isinstance(param,dict):
        for k in param.keys():
            if not none_null_stringNone(param[k]):
                return False
        return True
    return isNull(param) or stringNone(param)

def string_true_bool(param):
    return param and (isinstance(param,bool) or str(param).upper() == 'TRUE')

def path_join(basepath,suffixpath,sep='/'):
    if not ( isNull(basepath) and isNull(suffixpath) ):
        if not isNull(basepath):
            basepath = basepath.strip()
            if basepath[-1] == sep:
                basepath = basepath[:-1]
        if not isinstance(suffixpath,(tuple,list)):
            suffixpath = (suffixpath,)
        s = ''
        for i in suffixpath:
            if not isNull(i):
                i = i.strip()
                if i[0] != sep:
                    i = sep + i
                s += i
        return basepath + s


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

def format_exc():
    return traceback.format_exc()

def whichPath(software,sshconnect):
    cmd = 'which ' + software
    nostr = 'no ' + software + ' in'
    stat,data = sshconnect.execute_cmd(cmd,False)
    if stat == 0:
        data = to_text(data)
        for s in data.splitlines():
            i = s.find(nostr)
            if i >= 0 :
                return None
        data = data.replace('\r','').replace('\n','')
        if sshconnect.isLink(data):
            cmd = 'readlink data'
            stat,tdata = sshconnect.execute_cmd(cmd)
            if stat == 0 and tdata:
                return to_text(tdata).replace('\r','').replace('\n','')
        return data
    return None