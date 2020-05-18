
import traceback
from mysql.connector import Error
import log
from public_module.utils import record_log

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

def exec_stts(conn,statements,config=None):
    with conn.cursor() as cursor:
        for i in range(len(statements)):
            try:
                # t1 = int(round(time.time() * 1000))
                # print('before get statement %f'%t1)
                stt = statements.popleft()
                # t2 = int(round(time.time() * 1000))
                # print('after get statement %f elapsed time %f'%(t2,t2-t1))
                if config.log_statement:
                    log.info('exec statement:{}'.format(stt))
                cursor.execute(stt)
                # t3 = int(round(time.time() * 1000))
                # print('after execute statement %f,elapsed time %f'%(t3,t3-t2))
            except Error as e:
                log.error('error_num:%d,error_msg:%s .when execute statement:%s' %(e.errno,e.msg,stt))
                return -1
            except BaseException as e:
                log.error(traceback.format_exc())
                return -1
        return 0

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

@record_log
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