from .util import BaseClass

from typing import Iterable

class InputClass(BaseClass):
    def dump(self) -> str:
        lines = [f"&{self.__class__.__name__.lower()}"]
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, Iterable):
                    value_str = ", ".join(str(v) for v in value)
                else:
                    value_str = str(value)
                lines.append(f"  {key} = {value_str}")
        lines.append("&end")
        return "\n".join(lines)

class Setup(InputClass):
    pass

class AfterSetup(InputClass):
    pass

class Lattice(InputClass):
    pass

class Time(InputClass):
    pass

class Profiles(InputClass):
    pass

class Beam(InputClass):
    pass

class Field(InputClass):
    pass

class ImportDistribution(InputClass):
    pass

class ImportBeam(InputClass):
    pass

class ImportField(InputClass):
    pass

class EFeild(InputClass):
    pass

class Sponrad(InputClass):
    pass

class Wake(InputClass):
    pass

class Sort(InputClass):
    pass

class Write(InputClass):
    pass

class Track(InputClass):
    pass

class Stop(InputClass):
    pass

class InputFile:
    def __init__(self, filename = None, *inputs):
        self.filename = filename
        self.inputs = inputs

    def dump(self) -> str:
        parts = [input.dump() for input in self.inputs]
        return "\n\n".join(parts)
    
