from .util import BaseClass

class LatticeClass(BaseClass):
    name: str

class SingleLatticeClass(LatticeClass):
    def __init_subclass__(cls, *args, **kwargs) -> None:
        super().__init_subclass__()
        cls.counter = 0

    def __init__(self, name = None, **kwargs) -> None:
        self.__class__.counter += 1
        if name is None:
            name = f"{self.__class__.__name__.upper()[:3]}{self.__class__.counter}"
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __format__(self, format_spec: str = "") -> str:
        name = f'{self.name}: {self.__class__.__name__.upper()}'
        kv = '{ ' + ', '.join(f'{k} = {v}' for k, v in self.__dict__.items() if k != 'name') + ' }'
        return f'{name} = {kv};'
    
    def __add__(self, other): return Line(self, other)
    def __radd__(self, other): return Line(other, self)
    def __mul__(self, num): return Line(*[self] * num)
    def __rmul__(self, num): return Line(*[self] * num)

class Undulator(SingleLatticeClass):
    pass

class Drift(SingleLatticeClass):
    pass

class Quadrupole(SingleLatticeClass):
    pass

class Corrector(SingleLatticeClass):
    pass

class Chicane(SingleLatticeClass):
    pass

class Phaseshifter(SingleLatticeClass):
    pass

class Marker(SingleLatticeClass):
    pass


class MultiLatticeClass(LatticeClass):
    def __init_subclass__(cls, *args, **kwargs) -> None:
        super().__init_subclass__()
        cls.counter = 0

class Line(MultiLatticeClass):
    def __init__(self, *elements):
        self.__class__.counter += 1
        if isinstance(elements[0], str):
            self.name = elements[0]
            self.elements = elements[1:]
        else:
            self.name = f'{self.__class__.__name__.upper()[:3]}{self.__class__.counter}'
            self.elements = elements

    def __format__(self, format_spec: str = "") -> str:
        elems = '{ ' + ', '.join(l.name for l in self.elements) + ' }'
        return f'{self.name}: LINE = {elems};'

    def __add__(self, other):
        if isinstance(other, Line):
            return Line(*(self.elements + other.elements))
        elif isinstance(other, LatticeClass):
            return Line(*(self.elements + (other,)))
        raise TypeError("Can only add Line or LatticeClass instances")
    
    def __radd__(self, other):
        if isinstance(other, Line):
            return Line(*(other.elements + self.elements))
        elif isinstance(other, LatticeClass):
            return Line(*( (other,) + self.elements))
        raise TypeError("Can only add Line or LatticeClass instances")
    
    def __mul__(self, num): return Line(*self.elements * num)

    def __rmul__(self, num): return Line(*self.elements * num)


class LatticeFile:
    def __init__(self, beamline: Line):
        self.beamline = beamline

    def __format__(self, format_spec: str = "") -> str:
        dependencies = set(l for l in self.beamline.elements)
        elems = [f'{l}' for l in dependencies]
        elems.sort()
        return '\n'.join(elems) + f'\n\n{self.beamline}'
    
    def dump(self, filename: str):
        with open(filename, 'w') as f:
            f.write(format(self))

