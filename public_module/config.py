
from configparser import ConfigParser
from os import path
from deploy.fields import FieldMeta
import log

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
        for k,v in mConfigParser.items('mysql'):
            kw[k] = v
    try:
        mysqlconfig.host = kw['host']
        mysqlconfig.port = kw['port']
        mysqlconfig.user = kw['user']
        mysqlconfig.password = kw['password']
        mysqlconfig.database = kw['database']
    except KeyError as e:
        log.error("set mysql config failed!")
    else:
        CONFIG['mysql'] = mysqlconfig


CONFIG = {}
init_mysqlconfig()
