
_DEFAULT_BUFFER_SIZE = 4096



class  ContextManager(object):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return self.close()

class ConnectionBase(ContextManager):

    def __init__(self,host,user,password,port=22):
        self._host = host
        self._user = user
        self._password = password
        self._port = port


