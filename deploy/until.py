import os
from pathlib import Path
import re
from re import RegexFlag

# stat_type = {'DDL':1,'DDLS':1,'TABLE':2,'TABLES':2,'VIEW':3,'VIEWS':3,'PROCEDURE':2,'PROCEDURES':2,'FUNCTION':3,'FUNCTIONS':3,'DML':99,'DMLS':99}


REGEX = [
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

def _getValue(target):
    cons = 1;
    for pat,oper in REGEX:
        m = re.match(pat,target,RegexFlag.IGNORECASE)
        if m:
            if callable(oper):
                return oper(m.group())
            return oper
    return cons

def _compact(param):
    v = _getValue(param)
    if not isinstance(param,(tuple,list)):
        param = [param]
    if not isinstance(v,(tuple,list)):
        v = [v]
    param.extend(v)
    return param

def _gt(p1,p2):
    p1 = _compact(p1)
    p2 = _compact(p2)
    minsize = min(len(p1),len(p2))
    for i in range(1,minsize):
        if p1[i] > p2[i]:
            return True
        elif p1[i] < p2[i]:
            return False
    return True if minsize < len(p1) or len(p1) == len(p2) and p1[0] > p2[0] else False

def _partition(arr,low,high):
    i = high
    tmp = arr[high]
    for j in range(low , high):
        cur = arr[j]
        if _gt(cur , tmp):
            arr[i] = arr[j]
            i = j
    arr[i] = tmp
    return i

def _quickSort(arr,low,high):
    if low < high:
        pi = _partition(arr,low,high)
        _quickSort(arr, low, pi-1)
        _quickSort(arr, pi+1, high)

def _sort(objs):
    _quickSort(objs,0,len(objs)-1)
    return objs

def valid(filepath):
    return True if Path(filepath).is_dir() or os.path.splitext(filepath)[1].upper() == '.SQL' else False


def list_sqlfile(filepath):
    base = Path(filepath)
    if base.exists():
        if base.is_dir():
            curlist = {}
            curdir = os.path.split(filepath)[1]
            subfiles = _sort([i for i in os.listdir(filepath) if valid(os.path.join(filepath,i))])
            subfiles = list(list_sqlfile(os.path.join(filepath,i)) for i in subfiles)
            filterfiles = [i for i in subfiles if i]
            if filterfiles:
                curlist[curdir] = filterfiles
            return curlist
        else:
            if os.path.splitext(filepath)[1].upper() == '.SQL':
                return (filepath,)





def list_sqlfile_new(filepath):
    base = Path(filepath)
    if base.exists():
        if base.is_dir():
            curlist = {}
            num =  0
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

