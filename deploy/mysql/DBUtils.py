from mysql.connector import Error

import log
from  deploy.mysql.DataSource import DATASOURCE

SQL_CREATE_DATABASE = r'create database {}'

def isDBExists(dbname):
    try:
        conn = DATASOURCE.get_conn()
    except Error as e:
        log.error(e.errno+':'+e.msg)
    else :
        try:
            conn.database = dbname
            return True
        except Error as e:
            log.error(e.errno+':'+e.msg)
    finally:
        conn.close()
    return False

def isInstanceActive():
    return isDBExists('mysql')

