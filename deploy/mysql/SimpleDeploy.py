

import log
from deploy.mysql.DBUtils import exec_stts, safe_close
from parse.outer_parse import simple_parse
from public_module.config import getConfig, MYSQL_CATEGORY
from deploy.mysql.DataSource import getDS
from deploy.mysql import DBUtils
from public_module.global_vars import getNotifier

_notifier = None
def exec_warp(sqlfiles,total=0,curnum=0):
    global _notifier
    try:
        _config = getConfig()
        ds = getDS()
        conn = ds.get_conn()
        dbexists = DBUtils.isDBExists(conn,_config[MYSQL_CATEGORY]['database'])
        if not dbexists:
            with conn.cursor() as cursor:
                cursor.execute(DBUtils.SQL_CREATE_DATABASE.format(_config[MYSQL_CATEGORY]['database']))
            conn.database = _config[MYSQL_CATEGORY]['database']
        _notifier = getNotifier()
        notify_progress(1)
        exec(conn,sqlfiles,total,curnum)
        notify_progress(100)
    finally:
        _notifier = None
        safe_close(conn)
        safe_close(ds)


def exec(conn,sqlfiles,total=0,curnum=0):
    if isinstance(sqlfiles,dict):
        for k,v in sqlfiles.items():
            exec(conn,v,total,curnum)
    elif isinstance(sqlfiles,(tuple,list)):
        for k in sqlfiles:
            exec(conn,k,total,curnum)
    elif isinstance(sqlfiles,str):
        stts = simple_parse(sqlfiles)
        log.debug('exec start {} '.format(sqlfiles))
        exec_stts(conn,stts)
        cur_num = curnum +1
        notify_progress(cur_num*100/total)
        log.debug('exec end {} '.format(sqlfiles))

def notify_progress(value):
    global _notifier
    if _notifier:
        _notifier.notifyProgress(value)