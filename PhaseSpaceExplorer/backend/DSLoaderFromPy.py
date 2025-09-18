from typing import List, Callable, Tuple, Dict

from os.path import isfile, join

from backend.exceptions.DSLoader_exceptions import *


class DSLoaderFromPy():
    def __init__(self, folderpath):
        self.filename = "dynamical_system.py"
        self.folderpath = folderpath
        self.filepath = join(self.folderpath, self.filename)
        self.module = None
        return

    def load_DS(self):

        if not isfile(self.filepath):
            raise NoFileException(self.filepath)

        try:
            with open(self.filepath, 'r') as f:
                code = compile(f.read(), self.filepath, 'exec')
                module = {}
                exec(code, module)
        except:
            raise CouldNotImportModuleException(self.filepath)

        self.module = module

    @property
    def variable_names(self) -> List[str]:
        try:
            to_return = self.module["variable_names"]
        except:
            raise VariableNamesNotFoundException(self.filepath)
        return to_return

    @property
    def parameter_names(self) -> List[str]:
        try:
            to_return = self.module["parameter_names"]
        except:
            raise ParameterNamesNotFoundException(self.filepath)
        return to_return

    @property
    def ODEs(self) -> Callable:
        try:
            to_return = self.module["ODEs"]
        except:
            raise ODEsNotFoundException(self.filepath)
        return to_return

    @property
    def periodic_data(self) -> Dict[int, Tuple[float, float]]:
        try:
            to_return = self.module["periodic_data"]
        except:
            to_return = {}
        return to_return

    @property
    def periodic_events(self) -> List[Callable]:
        try:
            to_return = self.module["periodic_events"]
        except:
            to_return = []
        return to_return
