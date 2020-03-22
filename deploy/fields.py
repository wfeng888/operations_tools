from functools import  partial


def getx(cname,self):
    return self._attributes.get(cname,None)

def setx(cname,self, value):
    cls = self.__class__.__annotations__[cname]
    if value == None:
        self._attributes[cname] = None
        return
    if isinstance(cls,int) or cls == int:
        self._attributes[cname] = int(value)
    elif isinstance(cls,(list,tuple)) or cls in (list,tuple):
        if not isinstance(value,(list,tuple)):
            self._attributes[cname] = value.split(',')
        else:
            self._attributes[cname] = value
    elif isinstance(cls,dict) or cls == dict:
        if not isinstance(value,dict):
            tmplist = value.split(',')
            self._attributes[cname][tmplist.split(':')[0]] = tmplist.split(':')[1]
        else:
            self._attributes[cname] = value
    elif isinstance(cls,bool) or cls == bool:
        self._attributes[cname] = True if value and str(value).upper() == 'TRUE' else False
    else:
        self._attributes[cname] = value


class FieldMeta(type):
    def __new__(cls,clsname,bases,dicts):
        def _addBaseAnnotations(parents):
            for parent in parents:
                if not parent.__name__ == 'object' and not parent.__name__ == 'type':
                    if hasattr(parent,'__dict__') and parent.__dict__.get('__annotations__',None):
                        for key in  (set(parent.__dict__['__annotations__'].keys()) - set(dicts['__annotations__'].keys())):
                            dicts['__annotations__'][key] = parent.__dict__['__annotations__'][key]
                    if hasattr(parent,'__dict__') and parent.__dict__.get('_attribute_names',None):
                        dicts['_attribute_names'].update(parent.__dict__.get('_attribute_names'))
                    _addBaseAnnotations(parent.__bases__)
        names = []
        dicts['_attributes'] = {}
        dicts['_attribute_names'] = set()
        if not dicts.get('__annotations__',None):
            dicts['__annotations__'] = {}
        for name in dicts['__annotations__'].keys():
            if not name.startswith('__') and not name.startswith('_CONS'):
                names.append(name)
        for name in names:
            getter = partial(getx,'_'+name)
            setter = partial(setx,'_'+name)
            dicts[name] = property(getter,setter)
            dicts['_attribute_names'].add(name)
            dicts['__annotations__']['_'+name] = dicts['__annotations__'][name]
        _addBaseAnnotations(bases)
        return type.__new__(cls,clsname,bases,dicts)