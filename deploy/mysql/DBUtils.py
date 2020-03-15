import traceback

from mysql.connector import Error
import log

SQL_CREATE_DATABASE = r'create database {} if not exists'


def formatErrorMsg(e):
    try:
        return 'errno:{},msg:{},args:{}'.format(str(e.errno),e.msg,e.args)
    except BaseException:
        return traceback.format_exc()


def safe_close(resource,destroy=False):
    try:
        if resource:
            resource.close()
            if destroy:
                del resource
    except BaseException as e:
        log.error(traceback.format_exc())

def exec_stts(conn,statements):
    if not isinstance(statements,(list,tuple)):
        statements = (statements,)
    with conn.cursor() as cursor:
        for stt in statements:
            try:
                log.debug('exec statement:{}'.format(stt))
                cursor.execute(stt)
            except Error as e:
                log.error('error_num:%d,error_msg:%s .when execute statement:%s' %(e.errno,e.msg,stt))
            except BaseException as e:
                log.error(traceback.format_exc())

def query(conn,stat,params=()):
    try:
        with conn.cursor() as cursor:
            cursor.execute(stat,params)
            if cursor.with_rows:
                return cursor.fetchall()
            return ()
    except Error as e:
        log.error(formatErrorMsg(e))

def isDBExists(conn,dbname):
    try:
        if conn:
            conn.database = dbname
            return True
    except Error as e:
        log.error(formatErrorMsg(e))
    return False

def getVariable(variablename,conn=None,ds=None,globalv=False):
    stat = 'select @@{}'.format(variablename)
    try:
        if not ( conn or ds ):
            log.error('both conn and ds cann\'t be None at the same time.')
            return None
        if not conn:
            conn = ds.get_conn()
        return query(conn,stat)[0][0]
    except Error as e:
        log.error(formatErrorMsg(e))
        return None
    finally:
        if ds:
            safe_close(conn)
        pass