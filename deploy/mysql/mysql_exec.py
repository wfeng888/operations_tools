import traceback

from mysql.connector import InterfaceError

import log
from deploy.mysql.mysql_config import CreateMysqlConfig, MysqlConfig
from deploy.until import Sort,TYPE_MYSQL
from deploy.mysql import SimpleDeploy
from deploy.mysql.DataSource import getDS
from deploy.mysql.DBUtils import formatErrorMsg, isDBExists, safe_close

SIMPLE_DEPLOY,PARALLEL_DEPLOY = range(2)

def execute_createDB(config:CreateMysqlConfig,mode=SIMPLE_DEPLOY):

    if mode == SIMPLE_DEPLOY:
        log.info('start looking for sqlfile')
        sort = Sort(TYPE_MYSQL,'.SQL')
        sqlfiles,num = sort.list_sqlfile_new(config.sqlfiledir)
        log.info('has get all sorted sqlfile')
        SimpleDeploy.exec_warp(config,sqlfiles,num)
        log.info('finished create db ')




def isInstanceActive(config:MysqlConfig):
    log.info('check mysql service for {}'.format(config))
    try:
        ds = None
        conn = None
        ds = getDS(*(config.user,config.password,config.host,config.port,config.database))
        conn = ds.get_conn()
        return isDBExists(conn,'mysql')
    except InterfaceError as e:
        log.error('connect to {} failed !'.format(config))
        log.error(formatErrorMsg(e))
    except BaseException as e:
        log.error(traceback.format_exc())
    finally:
        safe_close(conn)