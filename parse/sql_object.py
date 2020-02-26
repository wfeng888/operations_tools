from typing import Optional

from parse.constants import FieldType


class SqlObject(object):
    _name:str

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self,pname):
        self._name = pname

class Database(SqlObject):
    # _tables:
    # _routines:
    # _triggers:
    #_operation_list:
    pass

class Column(SqlObject):
    #_table:Table
    _field_type:FieldType
    _identify:str
    pass

class Table(SqlObject):
    _database:Database
    _columns:Optional[list[Column]]




class TableSummary(SqlObject):
    #_database:
    #_reference
    #_referenced:
    #_operation_list:
    pass

class Routine(SqlObject):
    #_operation:
    #_body
    pass

class RoutineSummary(SqlObject):
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

class Index(SqlObject):
    # _database:
    # _table:
    # _definition:
    # _name:
    # _columns:
    #_operation_list:
    pass

class Column(SqlObject):
    # _database:
    # _table:
    # _definition:
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

class Operation(object):

    _verb:str
    _target:SqlObject
    _operation:Optional[Operation]
    _sql_statement:str

    pass

class Alter(Operation):
    _verb='ALTER'
    pass

class Create(Operation):
    _verb='CREATE'
    pass

class Drop(Operation):
    _verb='DROP'
    pass

class Add(Operation):
    _verb='ADD'
    pass

class Modify(Operation):
    _verb='MODIFY'
    pass

class Use(Operation):
    _verb = 'USE'
    pass