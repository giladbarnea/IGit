def prettyrepr(cls):
    class PrettyRepr(cls):
        def prepr(self):
            return self.__class__.__qualname__
        
        def __repr__(self) -> str:
            return self.prepr()
    
    return PrettyRepr
