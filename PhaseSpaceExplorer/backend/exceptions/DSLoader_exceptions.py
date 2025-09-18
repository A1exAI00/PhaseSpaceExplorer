class NoFileException(Exception):
    """Exception raised when path given does not lead to a file"""

    def __init__(self, path):
        super().__init__(f"{path}: No file with DynamicalSystem")


class CouldNotImportModuleException(Exception):
    """Exception raised when could not import file as module"""

    def __init__(self, path):
        super().__init__(f"{path}: Could not import file as module")


class VariableNamesNotFoundException(Exception):
    """Exception raised when could not import `variable_names` from file"""

    def __init__(self, path):
        super().__init__(f"f{path}: `variable_names` not found in file")


class ParameterNamesNotFoundException(Exception):
    """Exception raised when could not import `parameter_names` from file"""

    def __init__(self, path):
        super().__init__(f"{path}: `parameter_names` not found in file")


class ODEsNotFoundException(Exception):
    """Exception raised when could not import `ODEs` from file"""

    def __init__(self, path):
        super().__init__(f"{path} `ODEs` not found in file")
