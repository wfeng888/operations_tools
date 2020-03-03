
from configparser import ConfigParser
from os import path
from typing import List

from deploy.fields import FieldMeta
import log

MYSQL_CATEGORY = 'mysql'
MYSQL_CREATEDB_SQL_DIRECTORY_CONFIG = 'sqldirectory'
MYSQL_CREATEDB_CONFIG = ('host','port','user','password','database','sqldirectory')

class ConfigBase(object,metaclass=FieldMeta):
    host:str
    port:int
    user:str
    password:str

class MysqlConfig(ConfigBase):
    database:str


def init_mysqlconfig(**kw):
    global CONFIG
    mysqlconfig = MysqlConfig()
    if not kw:
        mConfigParser = ConfigParser();
        mConfigParser.read(path.join(path.split(__file__)[0],'config.ini'),'utf-8')
        kw = {}
        for k,v in mConfigParser.items(MYSQL_CATEGORY):
            kw[k] = v
    try:
        CONFIG[MYSQL_CATEGORY] = {}
        CONFIG[MYSQL_CATEGORY]['host'] = mysqlconfig.host = kw['host']
        CONFIG[MYSQL_CATEGORY]['port'] = mysqlconfig.port = kw['port']
        CONFIG[MYSQL_CATEGORY]['user'] = mysqlconfig.user = kw['user']
        CONFIG[MYSQL_CATEGORY]['password'] = mysqlconfig.password = kw['password']
        CONFIG[MYSQL_CATEGORY]['database'] = mysqlconfig.database = kw['database']
    except KeyError as e:
        log.error("set mysql config failed!")
        del CONFIG[MYSQL_CATEGORY]

def setSQLFileDirectory(dir):
    global CONFIG
    CONFIG[MYSQL_CATEGORY][MYSQL_CREATEDB_SQL_DIRECTORY_CONFIG] = dir

def checkConfigForMysqlCreateDB():
    global CONFIG
    try:
        for item in MYSQL_CREATEDB_CONFIG:
            if not CONFIG[MYSQL_CATEGORY][item]:
                return False
    except KeyError as e:
        return False
    return True

CONFIG = {}
init_mysqlconfig()
