from copy import deepcopy

import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTableWidget, QHBoxLayout, 
    QComboBox, QLineEdit, QCheckBox)

from app.controllers.PhaseSpaceController import PhaseSpaceController
from app.widgets.InitialStateTable import InitialStateTable, RowDataDragpoint, RowDataSoE
from backend.DynamicalSystem import DynamicalSystem
from backend.Trajectory import Trajectory

class InitialStateWidget(QWidget):
    _initial_state_type_options:list[str] = ["Dragpoint", "Tmp"]
    _dt_options:list[str] = ["+", "-"]
    def __init__(self, ds:DynamicalSystem, 
                 controller:PhaseSpaceController):
        super().__init__()
        self._ds = ds
        self._controller = controller
        self._N_variables:int = len(self._ds.variable_names)

        self._trajectories:list[Trajectory] = []

        self.setup_ui()
        self.connect_controller()
        return
    
    def setup_ui(self):
        # Main layout
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Button group (horizontal)
        button_layout = QHBoxLayout()
        # Add button to add row
        add_row_button = QPushButton("Add Row")
        add_row_button.clicked.connect(self.add_row)
        button_layout.addWidget(add_row_button)
        # Add placeholder button
        other_button = QPushButton("Other Button")
        button_layout.addWidget(other_button)
        layout.addLayout(button_layout)

        # Setup Initial State table
        self.table = InitialStateTable(self._ds._variable_names, self._controller)
        layout.addWidget(self.table)
        return
    
    def add_row(self):
        self.table.add_row("Dragpoint")
        self._trajectories.append(Trajectory(self._ds.ODEs, np.zeros(self._N_variables)))

        signal_data = {"n":self.table.rowCount()-1}
        self._controller.trajectory_added.emit(signal_data)
        return
    
    def connect_controller(self):
        self._controller.parameters_to_integrate_sent.connect(self.handle_initial_state_changed_step2)
        self._controller.trajectory_added.connect(self.integrate)
        self._controller.parameters_changed.connect(self.handle_parameters_changed)
        self._controller.labels_changed.connect(self.handle_labels_changed)
        return
    
    def integrate(self, signal_data):
        self._controller.data_changed.emit(signal_data)
        return
    
    def handle_initial_state_changed_step2(self, signal_data):
        # NOTE that at this point initial state should be either:
        # - unchanged (in case of parameter change)
        # - updated (in case of initial state change)
        # so initial state should not be changed here
        n = signal_data["n"]
        parameter_values = signal_data["parameter_values"]

        row_data = self.table.get_row(n)
        trajectory:Trajectory = self._trajectories[n]
        trajectory.init_state = row_data.variables

        t_start, t_end = row_data.t_start, row_data.t_end
        if row_data.dt == "-":
            t_start, t_end = t_end, t_start

        trajectory.integrate_scipy(parameter_values,
                                   t_start, t_end,
                                   row_data.t_steps,
                                   periodic_data=self._ds.periodic_data,
                                   periodic_events=self._ds.periodic_events)
        signal_data["trajectory"] = trajectory
        self._controller.trajectory_integrated.emit(signal_data)
        return
    
    def handle_parameters_changed(self, *args, **kwargs):
        signal_data = args[0]
        parameter_values = signal_data["parameter_values"]
        for n in range(self.table.rowCount()):
            new_signal_data = {"n":n, "parameter_values":parameter_values}
            self.handle_initial_state_changed_step2(new_signal_data)
        return
    
    def handle_labels_changed(self, *args, **kwargs):
        for i in range(self.table.rowCount()):
            signal_data = {"n":i, "trajectory":self._trajectories[i]}
            self._controller.trajectory_integrated.emit(signal_data)
        return