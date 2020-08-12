import log
from deploy.mysql import MySQLSQLExecute
from deploy.mysql.DataSource import getDS as get_mysql_ds
from deploy.mysql.mysql_config import MysqlConfig
from deploy.oracle import OracleSQLExecute, OraclePooledDBDataSource, OracleConfig
from deploy.transform import ds
from deploy.transform.base_exec import BaseExec
from deploy.transform.oracle2mysql import stage
from deploy.transform.oracle2mysql.sql import SQL_LIST


def start(oraconfig:OracleConfig,mysqlconfig:MysqlConfig):
    mysql_executor = MySQLSQLExecute(ds=get_mysql_ds(**{'user':mysqlconfig.user,'password':mysqlconfig.password,'host':mysqlconfig.host \
        ,'port':mysqlconfig.port,'database':mysqlconfig.database}))
    oracle_executor = OracleSQLExecute(ds=OraclePooledDBDataSource(**{'user':oraconfig.user,'password':oraconfig.password,'host':oraconfig.host,'port':oraconfig.port,'database':oraconfig.service}))
    upgradtor = BaseExec(stage,{ds.MYSQL:mysql_executor,ds.ORACLE:oracle_executor})
    _current_stage,_failures = upgradtor.start(SQL_LIST,stage)
    if _current_stage.value < stage.FINISH_VERIFY.value:
        log.error("Current Stage: %s less than Target Stage %s , means something failed! please check. "%(_current_stage,stage.FINISH_VERIFY))
    else:
        log.info("Current Stage: %s equal to  Target Stage %s , means execute successfully! "%(_current_stage,stage.FINISH_VERIFY))



# 测试用
if __name__ == '__main__':
    mysql_executor = MySQLSQLExecute(ds=get_mysql_ds(**{'user':'root','password':'zxm10@@@','host':'10.72.3.98','port':'3307','database':'usmsc'}))
    oracle_executor = OracleSQLExecute(ds=OraclePooledDBDataSource(**{'user':'sa','password':'zxm10','host':'10.72.3.16','port':'1521','database':'ORCL'}))
    upgradtor = BaseExec(stage,{ds.MYSQL:mysql_executor,ds.ORACLE:oracle_executor})
    _current_stage,_failures = upgradtor.start(SQL_LIST,stage)