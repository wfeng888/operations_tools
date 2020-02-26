from collections import deque

import sqlparse.sql
from parse.parse_delimiter import split_sql
import sys


#输入数据库名称和语句sqlparse.sql.statement对象，解析出来语句对应的数据库名，对象名，语句类型（table/procedure/function/event/trigger）*(create,alter,drop),
# def parse(dbname,statement):


if __name__ == '__main__':
    statements = deque()
    if len(sys.argv)>1:
        dbname = sys.argv[1]
    # with open('./sqlfile/test.sql',encoding='utf-8') as stream:
    with open('../test/sqlfile/test.sql',encoding='utf-8') as stream:
        content = stream.read()
    for str_stat in split_sql(content):
        statements.append(str_stat)
        ps = sqlparse.parse(str_stat)

