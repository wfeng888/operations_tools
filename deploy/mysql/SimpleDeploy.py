from mysql.connector import Error

from parse.outer_parse import simple_parse
from public_module.config import CONFIG
from deploy.mysql.DataSource import DATASOURCE
from deploy.mysql import DBUtils
import time

def exec_stts(statements):
    dbexists =  DBUtils.isDBExists(CONFIG.database)
    try:
        conn = DATASOURCE.get_conn()
        with conn.cursor() as cursor:
            if not dbexists:
                cursor.execute(DBUtils.SQL_CREATE_DATABASE.format(CONFIG.database))
                conn.database = CONFIG.database
            for stt in statements:
                try:
                    cursor.execute(stt)
                except Error as e:
                    print('error_num:%d,error_msg:%s' %(e.errno,e.msg))
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
        print('exec start %s ' % sqlfiles)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        exec_stts(stts)
        print('exec end %s ' % sqlfiles)

