from os.path import join, isfile

from backend.load_from_py import import_module_with_exec

class DynamicalSystem:
    def __init__(self):
        self._ds_filename = "dynamical_system.py"
        self._ds_folder_path = None
        self._ds_file_path = None
        self._variable_names = None
        self._parameter_names = None
        self._ODEs = None
        self._periodic_data = None

        self._loaded = False
        return
    
    @property
    def loaded(self):
        return self._loaded

    def __repr__(self):
        if not self._loaded:
            return "Dunamical System is not loaded"
        strings = [f"Path to folder: {self._ds_folder_path}",
                   f"Filename: {self._ds_filename}",
                   f"Variable names: {self._variable_names}",
                   f"Parameter names: {self._parameter_names}",
                   f"Periodic variable data: {self._periodic_data}",
                   f"ODEs: {self._ODEs}"]
        return "\n".join(strings)
    
    def load_from_py(self, ds_folder_path):
        ds_file_path = join(self._ds_folder_path, self._ds_filename)

        if not isfile(ds_file_path):
            print(f"Dynamical System file at {ds_file_path} not found")
            return False
        
        try: 
            ds_module = import_module_with_exec(ds_file_path)
        except: 
            print(f"Error when loading Dynamical System file at {ds_file_path}")
            return False
        
        try: 
            variable_names = ds_module["variable_names"]
        except:
            print(f"List of strings 'variable_names' is missing at {ds_file_path}")
            return False
        
        try: 
            parameter_names = ds_module["parameter_names"]
        except:
            print(f"List of strings 'parameter_names' is missing at {ds_file_path}")
            return False
        
        try: 
            ODEs = ds_module["ODEs"]
        except:
            print(f"Function 'ODEs' is missing at {ds_file_path}")

        try: 
            periodic_data = ds_module["periodic_data"]
        except:
            periodic_data = {}
        
        self._ds_folder_path = ds_folder_path
        self._ds_file_path = ds_file_path
        self._variable_names = variable_names
        self._parameter_names = parameter_names
        self._ODEs = ODEs
        self._periodic_data = periodic_data
        self._loaded = True
        return True
