
_DEFAULT_BUFFER_SIZE = 4096
class ConnectionBase(object):

    def __init__(self,host,user,password,port=22):
        self._host = host
        self._user = user
        self._password = password
        self._port = port


