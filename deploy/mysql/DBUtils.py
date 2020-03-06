from mysql.connector import Error
from public_module.config import getConfig,MYSQL_GENERAL_CONFIG,MYSQL_CATEGORY
import log
from deploy.mysql.DataSource import getDS

SQL_CREATE_DATABASE = r'create database {}'

def isDBExists(dbname):
    try:
        ds = getDS()
        conn = ds.get_conn()
    except Error as e:
        log.error(e.errno+':'+e.msg)
    else :
        try:
            if conn:
                conn.database = dbname
                return True
        except Error as e:
            log.error(e.errno+':'+e.msg)
    finally:
        if conn:
            conn.close()
        ds.close()
    return False

def isInstanceActive():
    _config = getConfig()
    log.info('check mysql service for {}'.format([k+'='+_config[MYSQL_CATEGORY][k] for k in MYSQL_GENERAL_CONFIG if k != 'password']))
    return isDBExists('mysql')

