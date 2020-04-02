import traceback

import log
from deploy.mysql.DBUtils import exec_stts, safe_close
from parse.outer_parse import simple_parse
from public_module.config import CreateMysqlConfig
from deploy.mysql.DataSource import getDS
from deploy.mysql import DBUtils
from public_module.global_vars import getNotifier

_notifier = None
def exec_warp(config:CreateMysqlConfig,sqlfiles,total=0,curnum=0):
    global _notifier
    try:
        conn = None
        ds = None
        ds = getDS(*(config.user,config.password,config.host,config.port,config.database))
        conn = ds.get_conn()
        # dbexists = DBUtils.isDBExists(conn,config.database)
        # if not dbexists:
        #     with conn.cursor() as cursor:
        #         cursor.execute(DBUtils.SQL_CREATE_DATABASE.format(config.database))
        #     conn.database = config.database
        _notifier = getNotifier()
        notify_progress(1)
        if exec(conn,sqlfiles,total,curnum,config) == 0:
            notify_progress(100)
        else:
            log.error("sql has errors , terminate !")
    except BaseException:
        log.error(traceback.format_exc())
    finally:
        _notifier = None
        safe_close(conn)
        safe_close(ds)


def exec(conn,sqlfiles,total=0,curnum=0,config=None):
    if isinstance(sqlfiles,dict):
        for k,v in sqlfiles.items():
            if exec(conn,v,total,curnum,config) == -1:
                if config:
                    if not config.ignore_error:
                        return -1
        return 0
    elif isinstance(sqlfiles,(tuple,list)):
        for k in sqlfiles:
            if exec(conn,k,total,curnum,config) == -1:
                if config:
                    if not config.ignore_error:
                        return -1
        return 0
    elif isinstance(sqlfiles,str):
        stts = simple_parse(sqlfiles)
        log.debug('exec start {} '.format(sqlfiles))
        if exec_stts(conn,stts,config) == -1 :
            if config:
                if not config.ignore_error:
                    return -1
        cur_num = curnum +1
        notify_progress(cur_num*100/total)
        log.debug('exec end {} '.format(sqlfiles))
        return 0

def notify_progress(value):
    global _notifier
    if _notifier:
        _notifier.notifyProgress(value)