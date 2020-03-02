from abc import ABCMeta
from configparser import ConfigParser
from os import path
from functools import partial
from deploy.fields import FieldMeta

class ConfigBase(object,metaclass=FieldMeta):
    host:str
    port:int
    user:str
    password:str

class MysqlConfig(ConfigBase):
    database:str


def init():
    mConfigParser = ConfigParser();
    mConfigParser.read(path.join(path.split(__file__)[0],'config.ini'),'utf-8')
    mysqlconfig = MysqlConfig()
    mysqlconfig.host = mConfigParser.get('mysql','host')
    mysqlconfig.port = mConfigParser.get('mysql','port')
    mysqlconfig.user = mConfigParser.get('mysql','user')
    mysqlconfig.password = mConfigParser.get('mysql','password')
    mysqlconfig.database = mConfigParser.get('mysql','database')
    return mysqlconfig


CONFIG = init()