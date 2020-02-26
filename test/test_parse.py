import sqlparse
import sqlparse.sql
from parse_delimiter import split_sql

#输入数据库名称和语句sqlparse.sql.statement对象，解析出来语句对应的数据库名，对象名，语句类型（table/procedure/function/event/trigger）*(create,alter,drop),
# def parse(dbname,statement):


if __name__ == '__main__':

    # with open('./sqlfile/test.sql',encoding='utf-8') as stream:
    with open('./sqlfile/test.sql',encoding='utf-8') as stream:
        statements = stream.read()
    for str_stat in split_sql(statements):
        ps = sqlparse.parse(str_stat)
