from PySide6.QtCore import QObject, Signal

class MainController(QObject):
    # Dicts for development only!
    # TODO change dicts to concrete data types
    ds_folder_selected = Signal(str)
    
    def __init__(self):
        super().__init__()