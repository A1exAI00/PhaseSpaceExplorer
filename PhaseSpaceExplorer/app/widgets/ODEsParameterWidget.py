import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit)


from app.controllers.PhaseSpaceController import PhaseSpaceController
from backend.DynamicalSystem import DynamicalSystem

class ODEsParametersWidget(QWidget):

    def __init__(self, dynamical_system:DynamicalSystem, 
                 controller:PhaseSpaceController):
        super().__init__()
        self._ds:DynamicalSystem = dynamical_system
        self._controller:PhaseSpaceController = controller
        self._headers:list[str] = ["Parameter", "Value"]
        self._N_parameters:int = len(self._ds.parameter_names)
        self._parameter_values:np.ndarray = np.zeros(self._N_parameters)
        self.setup_ui()
        self.connect_controller()
        return
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        
        # Setup Initial State table
        self.table = QTableWidget()
        self.table.setRowCount(len(self._ds.parameter_names))
        self.table.setColumnCount(len(self._headers))
        self.table.setHorizontalHeaderLabels(self._headers)
        
        # Allow to stretch the last column
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.values = []
        for (i,parameter_name) in enumerate(self._ds.parameter_names):
            # Items for immutable texts for parameter names
            parameter_name_item = QTableWidgetItem(parameter_name)
            parameter_name_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, parameter_name_item)

            # Items for parameter value input
            parameter_value_item = QLineEdit()
            self.values.append(parameter_value_item)
            parameter_value_item.setPlaceholderText("0.0")
            parameter_value_item.editingFinished.connect(
                lambda item=parameter_value_item, row=i: 
                self.handle_parameter_value_change(item.text(), row))
            self.table.setCellWidget(i, 1, parameter_value_item)
        return
    
    def connect_controller(self):
        self._controller.data_changed.connect(self.handle_parameters_requested)
        return
    
    def handle_parameter_value_change(self, text, changed_parameter_i):
        prev_value = self._parameter_values[changed_parameter_i]
        # Try to interplet text as float
        # Restore prev value if unsuccessful
        try:
            new_value = float(text.replace(" ", ""))
        except:
            self.values[changed_parameter_i].setText(str(prev_value))
            return
        # Store new value
        self._parameter_values[changed_parameter_i] = new_value

        signal_data = {"parameter_values": self._parameter_values}
        self._controller.parameters_changed.emit(signal_data)
        return
    
    def handle_parameters_requested(self, signal_data):
        # Add parameter values to data and pass back
        signal_data["parameter_values"] = self._parameter_values
        self._controller.parameters_to_integrate_sent.emit(signal_data)
        return