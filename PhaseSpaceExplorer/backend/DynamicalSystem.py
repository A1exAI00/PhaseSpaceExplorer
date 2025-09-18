from os.path import join, isfile

from backend.DSLoader import DSLoader


class DynamicalSystem:
    def __init__(self):
        self._ds_folderpath = None
        self._ds_filepath = None
        self._variable_names = None
        self._parameter_names = None
        self._ODEs = None
        self._periodic_data = None
        self._periodic_events = None

        self._loaded = False
        return

    @property
    def variable_names(self):
        return self._variable_names

    @property
    def parameter_names(self):
        return self._parameter_names

    @property
    def ODEs(self):
        return self._ODEs

    @property
    def periodic_data(self):
        return self._periodic_data

    @property
    def periodic_events(self):
        return self._periodic_events

    @property
    def loaded(self):
        return self._loaded

    def __repr__(self):
        if not self._loaded:
            return "Dunamical System is not loaded"
        strings = [f"Path to folder: {self._ds_folderpath}",
                   f"Variable names: {self._variable_names}",
                   f"Parameter names: {self._parameter_names}",
                   f"Periodic variable data: {self._periodic_data}",
                   f"Periodic events: {self._periodic_events}",
                   f"ODEs: {self._ODEs}"]
        return "\n".join(strings)

    def load(self, loader: DSLoader):
        self._ds_folderpath = loader.folderpath
        self._ds_filepath = loader.filepath
        self._variable_names = loader.variable_names
        self._parameter_names = loader.parameter_names
        self._ODEs = loader.ODEs
        self._periodic_data = loader.periodic_data
        self._periodic_events = loader.periodic_events
        self._loaded = True
