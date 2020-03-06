import log
from public_module.config import getConfig,MYSQL_CATEGORY,MYSQL_CREATEDB_SQL_DIRECTORY_CONFIG
from deploy.until import list_sqlfile
from deploy.mysql import SimpleDeploy
SIMPLE_DEPLOY,PARALLEL_DEPLOY = range(2)

def execute_createDB(mode=SIMPLE_DEPLOY):
    if mode == SIMPLE_DEPLOY:
        log.info('start looking for sqlfile')
        sqlfiles = list_sqlfile(getConfig()[MYSQL_CATEGORY][MYSQL_CREATEDB_SQL_DIRECTORY_CONFIG])
        log.info('has get all sorted sqlfile')
        SimpleDeploy.exec(sqlfiles)
        log.info('finished create db ')