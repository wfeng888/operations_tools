from configparser import ConfigParser
from mysql.connector import Error
from deploy.mysql.DataSource import DBUtilPooledDBDataSource,MysqlPooledDataSource

def get_column_names(description):
    if description:
        return [ i[0] for i in description ]
    return []



def bulk_insert_test(ds):
    dbName = 'test'
    tableName =  'test_insert'
    SIZE = 100
    SQL_DROP_TABLE_IF_EXISTS = 'drop table if exists {}.{}  '
    SQL_CREATE_TABLE = (
        "create table {}.{} ("
        "`id` bigint NOT NULL AUTO_INCREMENT,"
        "`name` varchar(20) DEFAULT NULL,"
        "`age` tinyint NOT NULL DEFAULT '0',"
        "`grade` tinyint DEFAULT NULL,"
        "`last_name` varchar(20) DEFAULT NULL,"
        "`desc` blob,"
        "PRIMARY KEY (`id`)"
        ")"
    )
    try:
        connout = ds.get_conn()
        connin = ds.get_conn()
        with connout.cursor() as outCursor:
            outCursor.execute(SQL_DROP_TABLE_IF_EXISTS.format(dbName,tableName))
            outCursor.execute(SQL_CREATE_TABLE.format(dbName,tableName))
            outCursor.execute('select * from test.t3')
            rows = outCursor.rowcount
            column_names = get_column_names(outCursor.description)
            insertSql = "insert into {}.{}(".format(dbName,tableName)+ ",".join([ "`"+item+"`" for item in column_names]) + \
                        ")" + \
                        " values( " + \
                        ",".join([ "%s" for i in column_names]) + \
                        ")"
            connin.begin()
            try:
                with connin.cursor() as inCursor:
                    size = 0
                    # 因为CMySQLCursor实现的bug，fetchmany会结束不了。
                    values = outCursor.fetchmany(SIZE)
                    while not values :
                        size = size + len(values)
                        print(size)
                        inCursor.executemany(insertSql,values)
                        values = outCursor.fetchmany(SIZE)
            except Error:
                connin.rollback()
            else:
                connin.commit()
    finally:
        connout.close()
        connin.close()

def test_execute_multi(ds):
    try:
        conn = ds.get_conn()
        with conn.cursor() as cursor:
            cursor.execute('show tables')
            print(cursor.description)

            results = [i for i in cursor.__iter__()]
            print(cursor.rowcount)
            print(results)
            cursor.execute('use test')
            for result in cursor.execute("select * from t1 limit 1;select * from t2 limit 1;select * from t3 limit 1", multi=True):
                if result.with_rows:
                    print("Rows produced by statement '{}':".format(result.statement))
                    column_names = get_column_names(cursor.description)
                    print(column_names)
                    l = [zip(column_names,i)for i in  result.fetchall()]
                    print(l)
                else:
                    print("Number of rows affected by statement '{}': {}".format(result.statement, result.rowcount))
    finally:
        conn.close()

def test_prepare_cursor(ds):
    try:
        conn = ds.get_conn()
        with conn.cursor(prepared=True) as cursor:
            print(type(cursor))
            conn.database = 'test'
            for param in ['tomas','zhangsan']:
                cursor.execute('select * from t3 where name = ? limit 1 ',(param,))
                print(cursor.fetchone())
    finally:
        conn.close()


def test_call_proc(ds):
    try:
        conn = ds.get_conn()
        with conn.cursor() as cursor:
            print(type(cursor))
            conn.database = 'test'
            result = cursor.callproc('TEST_PROC',(1,2,0))
            print(result)
            for i in cursor.stored_results():
                if i.with_rows:
                    print(i.fetchall())

    finally:
        conn.close()

if __name__ == '__main__':
    mConfigParser = ConfigParser();
    mConfigParser.read(('./config.ini',),'utf-8')
    mConfigParser.get('mysql','database')
    connparams = dict()
    for key,value in mConfigParser.items('mysql'):
        connparams[key] = value
    connparams['port'] = mConfigParser.getint('mysql','port')
    try:
        uds = DBUtilPooledDBDataSource(**connparams)
    except Error as e:
        print("connect error ")
        raise e
    else:
        test_call_proc(uds)
        test_execute_multi(uds)
        bulk_insert_test(uds)
        test_prepare_cursor(uds)
    finally:
        uds.close()
        mds.close()