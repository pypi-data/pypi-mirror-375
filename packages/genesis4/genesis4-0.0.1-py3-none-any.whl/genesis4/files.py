from .input import InputClass
from .lattice import LatticeClass

def inputs_connect(inputs) -> str:
    parts = [input.dump() for input in inputs]
    return "\n\n".join(parts)

def lattice_setting(lattice_dict) -> str:
    lines = [f'{name}: {lattice.dump()}' for name, lattice in lattice_dict.items()]
    return "\n".join(lines)

def lattice_combine(name, lattices) -> str:
    if isinstance(lattices, dict):
        line = '{ ' + ', '.join(f'{num} * {l}' if num > 1 else l for l, num in lattices.items()) + ' }'
    elif isinstance(lattices, (list, tuple)):
        line = '{ ' + ', '.join(lattices) + ' }'
    else:
        raise TypeError("lattices must be a dict, list, or tuple")
    return f'{name}: LINE = {line};'

