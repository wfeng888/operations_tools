from functools import  partial


def getx(cname,self):
    return self._attributes[cname]

def setx(cname,self, value):
    cls = self.__class__.__annotations__[cname]
    if isinstance(cls,int) or cls == int:
        self._attributes[cname] = int(value)
    elif isinstance(cls,(list,tuple)) or cls in (list,tuple):
        self._attributes[cname] = value.split(',')
    elif isinstance(cls,dict) or cls == dict:
        tmplist = value.split(',')
        self._attributes[cname][tmplist.split(':')[0]] = tmplist.split(':')[1]
    elif isinstance(cls,bool) or cls == bool:
        self._attributes[cname] = True if value and str(value).upper() == 'TRUE' else False
    else:
        self._attributes[cname] = value


class FieldMeta(type):
    def __new__(cls,clsname,bases,dicts):
        def _addBaseAnnotations(parents):
            for parent in parents:
                if not parent.__name__ == 'object' and not parent.__name__ == 'type' and hasattr(parent,'__dict__'):
                    for key in  (set(parent.__dict__['__annotations__'].keys()) - set(dicts['__annotations__'].keys())):
                        dicts['__annotations__'][key] = parent.__dict__['__annotations__'][key]
                    _addBaseAnnotations(parent.__bases__)
        names = []
        dicts['_attributes'] = {}
        dicts['_properties'] = {}
        for name in dicts['__annotations__'].keys():
            names.append(name)
        for name in names:
            getter = partial(getx,'_'+name)
            setter = partial(setx,'_'+name)
            dicts[name] = property(getter,setter)
            dicts['_properties'][name] = property(getter,setter)
            dicts['__annotations__']['_'+name] = dicts['__annotations__'][name]
        _addBaseAnnotations(bases)
        return type.__new__(cls,clsname,bases,dicts)