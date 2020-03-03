import log
from public_module.config import CONFIG,MYSQL_CATEGORY,MYSQL_CREATEDB_SQL_DIRECTORY_CONFIG
from deploy.until import list_sqlfile
from deploy.mysql import SimpleDeploy
SIMPLE_DEPLOY,PARALLEL_DEPLOY = range(2)

def execute_createDB(mode=SIMPLE_DEPLOY):
    if mode == SIMPLE_DEPLOY:
        log.debug('start looking for sqlfile')
        sqlfiles = list_sqlfile(CONFIG[MYSQL_CATEGORY][MYSQL_CREATEDB_SQL_DIRECTORY_CONFIG])
        log.debug('has get all sorted sqlfile')
        SimpleDeploy.exec(sqlfiles)
        log.debug('finished create db ')