import log
from public_module.config import getConfig, MYSQL_CATEGORY, MYSQL_CREATEDB_SQL_DIRECTORY_CONFIG, MYSQL_GENERAL_CONFIG, \
     CreateMysqlConfig
from deploy.until import list_sqlfile_new
from deploy.mysql import SimpleDeploy
from deploy.mysql.DataSource import getDS
from deploy.mysql.DBUtils import formatErrorMsg, isDBExists, safe_close

SIMPLE_DEPLOY,PARALLEL_DEPLOY = range(2)

def execute_createDB(config:CreateMysqlConfig,mode=SIMPLE_DEPLOY):

    if mode == SIMPLE_DEPLOY:
        log.info('start looking for sqlfile')
        sqlfiles,num = list_sqlfile_new(config.sqlfiledir)
        log.info('has get all sorted sqlfile')
        SimpleDeploy.exec_warp(config,sqlfiles,num)
        log.info('finished create db ')




def isInstanceActive():
    _config = getConfig()
    log.info('check mysql service for {}'.format([k+'='+_config[MYSQL_CATEGORY][k] for k in MYSQL_GENERAL_CONFIG if k != 'password']))
    try:
        ds = getDS()
        conn = ds.get_conn()
        return isDBExists(conn,'mysql')
    except BaseException as e:
        log.error(formatErrorMsg(e))
    finally:
        safe_close(conn)