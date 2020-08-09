class LazyProxy(object):
    def __init__(self, cls, *args, **kwargs):
        self.__dict__["_cls"] = cls
        self.__dict__["_args"] = args
        self.__dict__["_kwargs"] = kwargs
        
        self.__dict__["_inst"] = None
    
    def __getattr__(self, name):
        if self.__dict__["_inst"] is None:
            self.__init_inst()
        
        return getattr(self.__dict__["_inst"], name)
    
    def __setattr__(self, name, value):
        if self.__dict__["_inst"] is None:
            self.__init_inst()
        
        setattr(self.__dict__["_inst"], name, value)
    
    def __init_inst(self):
        self.__dict__["_inst"] = object.__new__(self.__dict__["_cls"], *self.__dict__["_args"], **self.__dict__["_kwargs"])
        self.__dict__["_inst"].__init__(*self.__dict__["_args"], **self.__dict__["_kwargs"])


class LazyInit(object):
    def __new__(cls, *args, **kwargs):
        return LazyProxy(cls, *args, **kwargs)


class A(LazyInit):  # classes meant to be lazy loaded are derived from LazyInit
    def __init__(self, x):
        print("Init A")
        self.x = 14 + x
