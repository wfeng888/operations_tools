import threading
import time
import traceback

from mysql.connector import InterfaceError

import log
from deploy.mysql.mysql_config import CreateMysqlConfig, MysqlConfig, MasterSlaveConfig
from deploy.until import Sort,TYPE_MYSQL
from deploy.mysql import SimpleDeploy
from deploy.mysql.DataSource import getDS
from deploy.mysql.DBUtils import formatErrorMsg, isDBExists, safe_close, query

SIMPLE_DEPLOY,PARALLEL_DEPLOY = range(2)

def execute_createDB(config:CreateMysqlConfig,mode=SIMPLE_DEPLOY):

    if mode == SIMPLE_DEPLOY:
        log.info('start looking for sqlfile')
        sort = Sort(TYPE_MYSQL,'.SQL')
        sqlfiles,num = sort.list_sqlfile(config.sqlfiledir)
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

def makeReplicate(config:MasterSlaveConfig):
    result = False
    ds = None
    conn = None
    slave_ds = None
    slave_conn = None
    # 先检查一下配置完整性
    stat,_ = config.check_config()
    if not stat:
        log.error('replication config is incomplete. failed to make replication.')
        return result
    log.debug('start make replication.')
    try:
        ds = getDS(config.master_conn_user,config.master_conn_password,config.master_host,config.master_port,'information_schema')
        conn = ds.get_conn()
    #  先检查一下复制用户是否存在，如果存在，看看密码对不对
        sql = "select User,host from mysql.user where user='{username}' and host='%' "
        users = query(conn,sql.format(username=config.repl_user))
        slave_ds = getDS(config.slave_conn_user,config.slave_conn_password,config.slave_host,config.slave_port,'information_schema')
        slave_conn = slave_ds.get_conn()
        if len(users) > 0:
            try:
                _ds = getDS(config.repl_user,config.repl_password,config.master_host,config.master_port,'information_schema')
                _c = _ds.get_conn()
                res = query(_c,'select 1')
                safe_close(_c)
            except BaseException as e:
                log.error(traceback.format_exc())
                #用户存在，但是密码不对，这个处理不了，退出
                log.error('replica user has exists in master, but password is incorrect. stop.')
                return result
        else:
            query(conn,"create user '{user}'@'%' identified by '{password}' ".format(user=config.repl_user,password=config.repl_password))
        query(conn,"grant Replication client,Replication  slave on *.*  to '{user}'@'%'".format(user=config.repl_user))
        query(conn,'flush privileges')
        if config.gtid_enable:
            cmd = "change master to MASTER_HOST='{master_host}',MASTER_USER='{repl_user}',MASTER_PORT={master_port},MASTER_PASSWORD='{repl_password}',MASTER_AUTO_POSITION=1"
            query(slave_conn,cmd.format(master_host=config.master_host,master_port=config.master_port,repl_user=config.repl_user,master_password=config.repl_password))
        else:
            cmd = "change master to MASTER_HOST='{master_host}',MASTER_USER='{repl_user}',MASTER_PORT={master_port},MASTER_PASSWORD='{repl_password}',MASTER_LOG_FILE='{binlog_file}',MASTER_LOG_POS={binlog_pos}"
            query(slave_conn,cmd.format(master_host=config.master_host,master_port=config.master_port,repl_user=config.repl_user,repl_password=config.repl_password, \
                    binlog_file=config.binlog_file,binlog_pos=config.binlog_pos))
        query(slave_conn,'start slave')
        res = query(slave_conn,'show slave status ')[0]
        i = 5
        while(i > 0):
            if 'Yes' == res[10]:
                result = True
                log.info('Slave_IO_State:%s'%res[0])
                break;
            log.error('Last_IO_Errno:%s, Last_IO_Error:%s'%(res[34],res[35]))
            time.sleep(5)
            i -= 1
        log.debug(res)
    except InterfaceError as e:
        log.error('connect to {} failed !'.format(config))
        log.error(formatErrorMsg(e))
    except BaseException as e:
        log.error(traceback.format_exc())
    finally:
        safe_close(conn)
        safe_close(slave_conn)
    return result
