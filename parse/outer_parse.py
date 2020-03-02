from collections import deque

import sqlparse.sql
from parse.parse_delimiter import split_sql
import sys
import parse.sql_object as sql_object
import re
from parse.sql_object import Operation


#输入数据库名称和语句sqlparse.sql.statement对象，解析出来语句对应的数据库名，对象名，语句类型（table/procedure/function/event/trigger）*(create,alter,drop),
# def parse(dbname,statement):

def parse_use(parsed_statement):
    pass

OPERATION_REGEX = {
    (r'\s*use\s+',Operation.USE),
    (r'\s*create\s+',Operation.CREATE),
    (r'\s*alter\s+',Operation.ALTER),
    (r'\s*drop\s+',Operation.DROP),
    (r'\s+add\s+',Operation.ADD),
    (r'\s+modify\s+',Operation.MODIFY),
}

def simple_parse(sqlfile):
    statements = deque()
    with open(sqlfile,encoding='utf-8') as stream:
        content = stream.read()
    for str_stat in split_sql(content):
        statements.append(str_stat)
    return statements

if __name__ == '__main__':
    statements = deque()
    databases = dict()
    tables = dict()
    gdb:str
    if len(sys.argv)>1:
        dbname = sys.argv[1]
        db = sql_object.Database()
        db.name = dbname
        databases[dbname] = db
        gdb = dbname
    # with open('./sqlfile/test.sql',encoding='utf-8') as stream:
    with open('../test/sqlfile/test.sql',encoding='utf-8') as stream:
        content = stream.read()
    for str_stat in split_sql(content):
        statements.append(str_stat)
        ps = sqlparse.parse(str_stat)[0]
        element = ps.token_first(skip_cm=True)
        for pat,obj in OPERATION_REGEX:
            m = re.match(pat,element,re.RegexFlag.IGNORECASE)
            if m:
                sqlobj = obj.parse(ps)
                break
        if isinstance(sqlobj,sql_object.Database):
            gdb = sqlobj.name
            databases




