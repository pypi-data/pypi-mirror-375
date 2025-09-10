from .util import BaseClass

from typing import Iterable

class InputClass(BaseClass):
    def __format__(self, format_spec: str = "") -> str:
        lines = [f"&{self.__class__.__name__.lower()}"]
        for key, value in self.__dict__.items():
            if value is not None:
                if isinstance(value, Iterable) and not isinstance(value, str):
                    value_str = ", ".join(str(v) for v in value)
                else:
                    value_str = str(value)
                lines.append(f"{key} = {value_str}")
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
    def __init__(self, *inputs: InputClass):
        self.inputs = inputs

    def __format__(self, format_spec: str = "") -> str:
        parts = [format(input, format_spec) for input in self.inputs]
        return "\n\n".join(parts)
    
    def dump(self, filename: str):
        with open(filename, 'w') as f:
            f.write(format(self))
    
    @property
    def setup(self) -> Setup:
        for input in self.inputs:
            if isinstance(input, Setup):
                return input
        raise ValueError("No Setup instance found in inputs")
    