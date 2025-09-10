from .util import BaseClass

class LatticeClass(BaseClass):
    def dump(self) -> str:
        clsname = self.__class__.__name__.upper()
        kv = '{ ' + ', '.join(f'{k} = {v}' for k, v in self.__dict__.items()) + ' }'
        return f'{clsname} = {kv};'

class Undulator(LatticeClass):
    pass

class Drift(LatticeClass):
    pass

class Quadrupole(LatticeClass):
    pass

class Corrector(LatticeClass):
    pass

class Chicane(LatticeClass):
    pass

class Phaseshifter(LatticeClass):
    pass

class Marker(LatticeClass):
    pass

class Line(LatticeClass):
    def __init__(self, *elements):
        self.elements = elements

    def __rmul__(self, num):
        return Line(*self.elements * num)
