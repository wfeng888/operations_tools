import traceback

from mysql.connector import Error

import log
from parse.outer_parse import simple_parse
from public_module.config import getConfig, MYSQL_CATEGORY
from deploy.mysql.DataSource import getDS
from deploy.mysql import DBUtils
from public_module.global_vars import getNotifier

def exec_stts(statements):
    _config = getConfig()
    try:
        ds = getDS()
        dbexists =  DBUtils.isDBExists(ds,_config[MYSQL_CATEGORY]['database'])
        conn = ds.get_conn()
        with conn.cursor() as cursor:
            if not dbexists:
                cursor.execute(DBUtils.SQL_CREATE_DATABASE.format(_config[MYSQL_CATEGORY]['database']))
                conn.database = _config[MYSQL_CATEGORY]['database']
            for stt in statements:
                try:
                    log.debug('exec statement:{}'.format(stt))
                    cursor.execute(stt)
                except Error as e:
                    log.error('error_num:%d,error_msg:%s .when execute statement:%s' %(e.errno,e.msg,stt))
                except BaseException as e:
                    log.error(traceback.format_exc())
    finally:
        conn.close()
        ds.close()


_notifier = None
def exec_warp(sqlfiles,total=0,curnum=0):
    global _notifier
    try:
        _notifier = getNotifier()
        notify_progress(1)
        exec(sqlfiles,total,curnum)
        notify_progress(100)
    finally:
        _notifier = None


def exec(sqlfiles,total=0,curnum=0):
    if isinstance(sqlfiles,dict):
        for k,v in sqlfiles.items():
            exec(v,total,curnum)
    elif isinstance(sqlfiles,(tuple,list)):
        for k in sqlfiles:
            exec(k,total,curnum)
    elif isinstance(sqlfiles,str):
        stts = simple_parse(sqlfiles)
        log.debug('exec start {} '.format(sqlfiles))
        exec_stts(stts)
        cur_num = curnum +1
        notify_progress(cur_num*100/total)
        log.debug('exec end {} '.format(sqlfiles))

def notify_progress(value):
    global _notifier
    if _notifier:
        _notifier.notifyProgress(value)