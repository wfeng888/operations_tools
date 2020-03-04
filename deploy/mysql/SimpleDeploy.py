from mysql.connector import Error

import log
from parse.outer_parse import simple_parse
from public_module.config import CONFIG, MYSQL_CATEGORY
from deploy.mysql.DataSource import DATASOURCE
from deploy.mysql import DBUtils
import time

def exec_stts(statements):
    dbexists =  DBUtils.isDBExists(CONFIG[MYSQL_CATEGORY]['database'])
    try:
        conn = DATASOURCE.get_conn()
        with conn.cursor() as cursor:
            if not dbexists:
                cursor.execute(DBUtils.SQL_CREATE_DATABASE.format(CONFIG[MYSQL_CATEGORY]['database']))
                conn.database = CONFIG[MYSQL_CATEGORY]['database']
            for stt in statements:
                try:
                    log.debug('exec statement:{}'.format(stt))
                    cursor.execute(stt)
                except Error as e:
                    log.error('error_num:%d,error_msg:%s .when execute statement:%s' %(e.errno,e.msg,stt))
    finally:
        conn.close()


def exec(sqlfiles):
    if isinstance(sqlfiles,dict):
        for k,v in sqlfiles.items():
            exec(v)
    elif isinstance(sqlfiles,(tuple,list)):
        for k in sqlfiles:
            exec(k)
    elif isinstance(sqlfiles,str):
        stts = simple_parse(sqlfiles)
        log.debug('exec start {} '.format(sqlfiles))
        exec_stts(stts)
        log.debug('exec end {} '.format(sqlfiles))

