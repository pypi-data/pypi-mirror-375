import subprocess

from .input import InputFile
from .lattice import LatticeFile

class Genesis4:
    def __init__(self, path: str, silent: bool = True):
        self.name = self.__class__.__name__
        self.path = path
        # subprocess.run(self.path, shell=True, stdout=subprocess.PIPE if silent else None)

    def run(self, input: InputFile, lattice: LatticeFile):
        input_filename = f'{input.setup.rootname}.in' # type: ignore
        input.dump(input_filename)
        lattice.beamline.name = input.setup.beamline # type: ignore
        lattice_filename = input.setup.lattice # type: ignore
        lattice.dump(lattice_filename) # type: ignore
        subprocess.run(f'{self.path} {input_filename}', shell=True)
        # subprocess.run(f'rm {input_filename} {lattice_filename}', shell=True)

