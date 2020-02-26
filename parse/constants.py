class FieldType(object):
    _type_name:str
    _size:int
    _isNoSize:bool = True

    @property
    def size(self):
        if not self._isNoSize:
            return self._size
        return None

    @size.setter
    def size(self,long_size):
        if not self._isNoSize:
            self._size = long_size

    @property
    def type_name(self):
        return self._type_name

class DECIMAL(FieldType):
    _type_name = 'DECIMAL'



class TINY(FieldType):
    _type_name = 'TINY'

class SHORT(FieldType):
    _type_name = 'SHORT'

class LONG(FieldType):
    _type_name = 'LONG'

class FLOAT(FieldType):
    _type_name = 'FLOAT'

class DOUBLE(FieldType):
    _type_name = 'DOUBLE'

class TIMESTAMP(FieldType):
    _type_name = 'TIMESTAMP'

class LONGLONG(FieldType):
    _type_name = 'LONGLONG'

class INT24(FieldType):
    _type_name = 'INT24'

class DATE(FieldType):
    _type_name = 'DATE'

class TIME(FieldType):
    _type_name = 'TIME'

class DATETIME(FieldType):
    _type_name = 'DATETIME'

class YEAR(FieldType):
    _type_name = 'YEAR'

class NEWDATE(FieldType):
    _type_name = 'NEWDATE'

class VARCHAR(FieldType):
    _type_name = 'VARCHAR'

class BIT(FieldType):
    _type_name = 'BIT'

class JSON(FieldType):
    _type_name = 'JSON'

class NEWDECIMAL(FieldType):
    _type_name = 'NEWDECIMAL'

class NEWDECIMAL(FieldType):
    _type_name = 'NEWDECIMAL'

class ENUM(FieldType):
    _type_name = 'ENUM'

class SET(FieldType):
    _type_name = 'SET'

class TINY_BLOB(FieldType):
    _type_name = 'TINY_BLOB'

class MEDIUM_BLOB(FieldType):
    _type_name = 'MEDIUM_BLOB'

class LONG_BLOB(FieldType):
    _type_name = 'LONG_BLOB'

class BLOB(FieldType):
    _type_name = 'BLOB'

class VAR_STRING(FieldType):
    _type_name = 'VAR_STRING'

class STRING(FieldType):
    _type_name = 'STRING'

class GEOMETRY(FieldType):
    _type_name = 'GEOMETRY'
