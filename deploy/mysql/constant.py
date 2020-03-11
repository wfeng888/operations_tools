

class MysqlVarType(object):
    VAR_SCOPE = enumerate(('session','global','both'))
    def __init__(self,cmd_line,option_file,system_var,status_var,var_scope,dynamic):
        self._cmd_line = cmd_line
        self._option_file = option_file
        self._system_var = system_var
        self._status_var = status_var
        self._var_scope = var_scope
        self._dynamic = dynamic

MYSQL57_VAR= {}

MYSQL8_VAR = {}