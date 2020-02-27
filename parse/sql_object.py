from collections import deque
from typing import Optional, List, Dict

from parse.constants import FieldType
from sqlparse.sql import Identifier
from abc import abstractmethod


def parse_use(tokenlist):
    element =  tokenlist.token_next(idx = 0,skip_ws=True, skip_cm=True, _reverse=True)
    return Database(element.norma)

from enum import Enum, unique
@unique
class Operation(Enum):
    CREATE = 0
    DROP = 1
    ADD = 2
    MODIFY = 3
    ALTER = 4
    USE = 5

    def parse(self):
        pass

def _merge(ori,target):
    for i in set(ori.keys()) & set(target.keys()) :
        target[i].merge(target[i])

    for i in set(target.keys()) - set(ori.keys()):
        ori[i] = target[i]



@property
def database(self):
    return self._database
@database.setter
def database(self,db):
    self._database = db

@property
def table(self):
    return self._table
@database.setter
def table(self,table):
    self._table = table




class AddAttribute(type):
    def __new__(cls, name,bases,dicts):
        if name in ('Index','Table','Column'):
            dicts['database'] = database
        return type.__new__(cls, name,bases,dicts)

class SqlObject(object):
    _name:str

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self,pname):
        self._name = pname

    @abstractmethod
    def equals(self,target):
        pass

class Database(SqlObject):
    # _tablesummarys:
    # _routinesummarys:
    # _triggersummarys:
    #_operation_list:
    def __init__(self,dbname):
        self._name = dbname
        self._tablesummarys:dict[str:TableSummary] = dict()
        self._routinesummarys = dict()
        self._triggersummarys = dict()
        self._operation_list = []

    def equals(self,target):
        if isinstance(target,Database) and self.name == target.name :
            return True
        return False


    def merge(self,targetdatabase):
        _merge(self._tablesummarys,targetdatabase._tablesummarys)
        _merge(self._routinesummarys,targetdatabase._routinesummarys)
        _merge(self._triggersummarys,targetdatabase._triggersummarys)
        self._operation_list.extend(targetdatabase._operation_list)

class Column(SqlObject,metaclass=AddAttribute):
    _dbname:str
    _tablename: str
    _field_type:FieldType
    _identify:str
    pass

class Index(SqlObject):
    _dbname:str
    _tablename: str
    # _identifier:
    # _name:
    # _columns:
    #_ori_statement:str
    def __init__(self,db,table,name,iden,cols):
        pass

class Constraint(SqlObject):
    pass




class Table(SqlObject):
    _dbname:str
    _columns:Optional[List[Column]]
    # _indexs:Optional[List[Index]]
    # _constraints:Optional[List[Constraint]]
    # _identifier:str
    _operation:Operation
    _oristatement:str


class Summary(object):
    @abstractmethod
    def merge(self,target):
        pass

class TableSummary(SqlObject,Summary):
    _dbname:str
    _tablename: str
    _ori_operation_list:List[Table]
    def __init__(self,db,table):
        self._database = db
        self._table = table
        self._ori_operation_list = []

    def addOpe(self,target):
        assert  self._dbname.name == target._dbname and self.table._tablename == target._tablename
        self._ori_operation_list.append(target)

class Routine(SqlObject,Summary):
    #_operation:
    #_body
    pass

class RoutineSummary(SqlObject,Summary):
    #_operation_list:
    pass

class ProcedureSummary(RoutineSummary):
    pass

class FunctionSummary(RoutineSummary):
    pass

class EventSummary(RoutineSummary):
    pass

class TriggerSummary(RoutineSummary):
    # _table:
    #_operation_list:
    pass



class Relation(object):
    pass

class Dependency(Relation):
    pass

class Reference(Dependency):
    # _table:
    # _columns:
    pass

class Referenced(Relation):
    # _table:
    # _columns:
    pass




