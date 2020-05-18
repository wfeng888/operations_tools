import os
import traceback
from pathlib import Path
import re
from re import RegexFlag

# stat_type = {'DDL':1,'DDLS':1,'TABLE':2,'TABLES':2,'VIEW':3,'VIEWS':3,'PROCEDURE':2,'PROCEDURES':2,'FUNCTION':3,'FUNCTIONS':3,'DML':99,'DMLS':99}
import log

TYPE_MYSQL,TYPE_ES,TYPE_ORACLE = range(3)
REGEX_MYSQL = REGEX_ORACLE = [
    (r'(\s)*([0-9]+(\.)*)+(\s)*',lambda x: [int(i) for i in x.split('.')]),
    (r'(\s)*table',lambda x: 1),
    (r'(\s)*view',lambda x: 2),
    (r'(\s)*proc',lambda x: 3),
    (r'(\s)*func',lambda x: 4),
    (r'(\s)*trig',lambda x: 5),
    (r'(\s)*ddl',lambda x: 20),
    (r'(\s\S)*data(\s\S)*',lambda x: 90),
    (r'(\s\S)*dml(\s\S)*',lambda x: 91)
]
REGEX_ES = [
    (r'(\s)*([0-9]+(\.)*)+(\s)*',lambda x: [int(i) for i in x.split('.')]),
    (r'(\s)*template',lambda x: 1),
    (r'(\s)*index',lambda x: 2)
]
REGEX = {
    TYPE_MYSQL:REGEX_MYSQL,
    TYPE_ORACLE:TYPE_ORACLE,
    TYPE_ES:REGEX_ES
}

class Sort(object):


    def __init__(self,type,suffix):
        self._regex = REGEX[type]
        self._suffix = suffix

    def _getValue(self,target):
        cons = 1;
        for pat,oper in self._regex:
            m = re.match(pat,target,RegexFlag.IGNORECASE)
            if m:
                if callable(oper):
                    return oper(m.group())
                return oper
        return cons

    def _compact(self,param):
        v = self._getValue(param)
        if not isinstance(param,(tuple,list)):
            param = [param]
        if not isinstance(v,(tuple,list)):
            v = [v]
        param.extend(v)
        return param

    def _gt(self,p1,p2):
        p1 = self._compact(p1)
        p2 = self._compact(p2)
        minsize = min(len(p1),len(p2))
        for i in range(1,minsize):
            if p1[i] > p2[i]:
                return True
            elif p1[i] < p2[i]:
                return False
        return True if minsize < len(p1) or len(p1) == len(p2) and p1[0] > p2[0] else False

    def _partition(self,arr,low,high):
        i = high
        tmp = arr[high]
        for j in range(low , high):
            cur = arr[j]
            if self._gt(cur , tmp):
                arr[i] = arr[j]
                i = j
        arr[i] = tmp
        return i

    def _quickSort(self,arr,low,high):
        if low < high:
            pi = self._partition(arr,low,high)
            self._quickSort(arr, low, pi-1)
            self._quickSort(arr, pi+1, high)

    def _sort(self,objs):
        self._quickSort(objs,0,len(objs)-1)
        return objs


    def valid(self,filepath):
        return True if Path(filepath).is_dir() or os.path.splitext(filepath)[1].upper() == self._suffix else False


    def list_sqlfile(self,filepath):
        base = Path(filepath)
        if base.exists():
            if base.is_dir():
                curlist = {}
                num =  0
                curdir = os.path.split(filepath)[1]
                subfiles = self._sort([i for i in os.listdir(filepath) if self.valid(os.path.join(filepath,i))])
                curfiles = []
                for i in subfiles:
                    if os.path.isdir(os.path.join(filepath,i)):
                        s = self.list_sqlfile(os.path.join(filepath,i))
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
                if os.path.splitext(filepath)[1].upper() == self._suffix:
                    return filepath,1


def safe_doing(func,*args):
    try:
        func(*args)
    except BaseException as e:
        log.error(traceback.format_exc())