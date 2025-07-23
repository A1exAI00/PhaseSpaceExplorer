from PySide6.QtCore import QObject, Signal

class PhaseSpaceController(QObject):
    # Dicts for development only!
    # TODO change dicts to concrete data types
    data_in_InitialStateWidget_changed = Signal(dict)
    parameters_sent = Signal(dict)
    parameters_changed = Signal(dict)
    trajectory_added = Signal(dict)
    trajectory_integrated = Signal(dict)
    trajectories_requested = Signal(dict)
    labels_changed = Signal(dict)
    
    def __init__(self):
        super().__init__()