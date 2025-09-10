class BaseClass:
    def __init__(self, name = None, **kwargs):
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'
    
