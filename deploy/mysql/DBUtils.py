import traceback

from mysql.connector import Error
import log





def formatErrorMsg(e):
    try:
        return 'mysql connect error.  errno:{},msg:{},args:{}'.format(str(e.errno),e.msg,e.args)
    except BaseException:
        return traceback.format_exc()



def isDBExists(ds,dbname):
    try:
        conn = ds.get_conn()
    except Error as e:
        log.error(e.errno+':'+e.msg)
    else :
        try:
            if conn:
                conn.database = dbname
                return True
        except Error as e:
            log.error(e.errno+':'+e.msg)
    finally:
        if conn:
            conn.close()
    return False