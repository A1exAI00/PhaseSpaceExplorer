from copy import deepcopy

import numpy as np
from PySide6 import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox, QLineEdit, QCheckBox

# For VSCode autocomplete, to avoid circular import
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from gui.WorkbenchPhaseSpace import WorkbenchPhaseSpace

from app.controllers.PhaseSpaceController import PhaseSpaceController
from backend.DynamicalSystem import DynamicalSystem
from backend.Trajectory import Trajectory

class RowData():
    def __init__(self, data_default:dict):
        self.type:str = data_default["type"]
        self.trajectory:Trajectory = data_default["trajectory"]
        self.show:str = data_default["show"]
        self.dt:str = data_default["dt"]
        self.t_start:float = data_default["t_start"]
        self.t_end:float = data_default["t_end"]
        self.t_steps:int = data_default["t_steps"]
        return

class InitialStateWidget(QWidget):
    _initial_state_type_options:list[str] = ["Dragpoint", "Tmp"]
    _dt_options:list[str] = ["+", "-"]
    def __init__(self, ds:DynamicalSystem, controller:PhaseSpaceController):
        super().__init__()
        self._ds = ds
        self._controller = controller
        self._N_variables:int = len(self._ds.variable_names)
        self._row_count:int = 0

        # Dragpoint views
        self._headers_dragpoint:list[str] = (["Type",] 
            + self._ds.variable_names 
            + ["Show", "dt", "t start", "t end", "t steps"])
        self._rows_views = []
        # Dragpoint data
        self._variable_value_default:float = 0.0
        default_row_data = {}
        default_row_data["type"] = self._initial_state_type_options[0]
        default_row_data["trajectory"] = Trajectory(self._ds.ODEs, self._variable_value_default*np.ones(self._N_variables))
        default_row_data["show"] = True
        default_row_data["dt"] = self._dt_options[0]
        default_row_data["t_start"] = 0.0
        default_row_data["t_end"] = 10.0
        default_row_data["t_steps"] = 1000
        self._RowData_default = RowData(default_row_data)
        self._rows_data:list[RowData] = []

        # self._headers_SoE =  ["Type",] + self.ds.variable_names + ["Show", "Autocorr.", "Correct", "dt", "eps", "Eig. N", "Eig. dir", "t start", "t end", "t steps"]
        
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
        self.table = QTableWidget()
        self.table.setColumnCount(len(self._headers_dragpoint))
        self.table.setHorizontalHeaderLabels(self._headers_dragpoint)
        # Allow to stretch the last column
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        return
    
    def connect_controller(self):
        self._controller.parameters_sent.connect(self.handle_initial_state_changed_step2)
        self._controller.trajectory_added.connect(self.integrate)
        self._controller.parameters_changed.connect(self.handle_parameters_changed)
        self._controller.labels_changed.connect(self.handle_labels_changed)
        return
    
    def add_row(self):
        # Update the number of rows
        curr_index = self._row_count
        self._row_count += 1 
        self.table.setRowCount(self._row_count)
        new_row_data = deepcopy(self._RowData_default)
        self._rows_data.append(new_row_data)

        # Add field for initial state type
        type_combobox = QComboBox(currentText=new_row_data.type)
        for _type in self._initial_state_type_options:
            type_combobox.addItem(_type)
        type_combobox.currentIndexChanged.connect(self.handle_type_changed)
        self.table.setCellWidget(curr_index, 0, type_combobox)

        # Add field for coordinates of initial state
        this_row_edits = []
        for i in range(len(self._ds.variable_names)):
            edit = QLineEdit(placeholderText=str(new_row_data.trajectory.init_state[i]))
            this_row_edits.append(edit)
            edit.editingFinished.connect(
                lambda item=edit, n=curr_index, i=i:
                self.handle_variable_changed(item.text(), n, i))
            self.table.setCellWidget(curr_index, 1+i, edit)
        self._rows_views.append(this_row_edits)

        # Add field to show/hide initial state and trajectory
        show = QCheckBox() # TODO how to fucking set the state to checked
        show.stateChanged.connect(
            lambda state, index=curr_index: 
            self.handle_show_change(state, index))
        self.table.setCellWidget(curr_index, self._N_variables+1, show)
        
        # Add field for integration direction `dt`
        dt = QComboBox(currentText=new_row_data.dt)
        dt.addItem(self._dt_options[0])
        dt.addItem(self._dt_options[1])
        dt.currentIndexChanged.connect(
            lambda index_combobox, index_traj=curr_index:
            self.handle_dt_changed(index_traj, index_combobox))
        self.table.setCellWidget(curr_index, self._N_variables+2, dt)

        # Add field for t_start
        t_start = QLineEdit(placeholderText=str(new_row_data.t_start))
        t_start.editingFinished.connect(
            lambda item=t_start, index=curr_index:
            self.handle_t_start_changed(item, index))
        self.table.setCellWidget(curr_index, self._N_variables+3, t_start)

        # Add field for t_end
        t_end = QLineEdit(placeholderText=str(new_row_data.t_end))
        t_end.editingFinished.connect(
            lambda item=t_end, index=curr_index:
            self.handle_t_end_changed(item, index))
        self.table.setCellWidget(curr_index, self._N_variables+4, t_end)

        # Add field for (approximate) t_steps
        t_steps = QLineEdit(placeholderText=str(new_row_data.t_steps))
        t_steps.editingFinished.connect(
            lambda item=t_steps, index=curr_index:
            self.handle_t_steps_changed(item, index))
        self.table.setCellWidget(curr_index, self._N_variables+5, t_steps)

        signal_data = {"n":curr_index, "trajectory":new_row_data.trajectory}
        self._controller.trajectory_added.emit(signal_data)
        return
    
    def integrate(self, signal_data):
        self._controller.data_in_InitialStateWidget_changed.emit(signal_data)
        return
    
    def handle_type_changed(self, *args, **kwargs):
        print(args, kwargs)
        return
    
    def handle_variable_changed(self, text, n, i):
        print(text, n, i)
        # Try to interplet input as float
        prev_init_state = self._rows_data[n].trajectory.init_state
        prev_value = prev_init_state[i]
        try:
            new_value = float(text)
        except:
            self._rows_views[n][i].setText(str(prev_value))
            return
        new_initial_state = prev_init_state.copy()
        new_initial_state[i] = new_value
        self._rows_data[n].trajectory.init_state = new_initial_state

        # Send signal to request parameter values
        # ODEsParameterWidget should emit `parameters_sent` signal
        signal_data = {"n":n}
        self._controller.data_in_InitialStateWidget_changed.emit(signal_data)
        return
    
    def handle_initial_state_changed_step2(self, signal_data):
        # NOTE that at this point initial state should be either:
        # - unchanged (in case of parameter change)
        # - updated (in case of initial state change)
        # so initial state should not be changed here
        n = signal_data["n"]
        parameter_values = signal_data["parameter_values"]

        row_data:RowData = self._rows_data[n]
        trajectory:Trajectory = row_data.trajectory
        trajectory.integrate_scipy(parameter_values, 
                                   row_data.t_start,
                                   row_data.t_end,
                                   row_data.t_steps,
                                   periodic_data=self._ds.periodic_data,
                                   periodic_events=self._ds.periodic_events)
        signal_data["trajectory"] = trajectory
        self._controller.trajectory_integrated.emit(signal_data)
        return
    
    def handle_show_change(self, *args, **kwargs):
        state, n = args
        self._rows_data[n].show = (state == 2)
        # TODO emit signal to hide from plot 
        return
    
    def handle_dt_changed(self, *args, **kwargs):
        n = args[0]
        i = args[1]
        self._rows_data[n].dt = self._dt_options[i]
        # TODO emit signal to reintegrate and replot 
        return
    
    def handle_t_start_changed(self, item, n):
        text = item.text()
        # Try to interplet input as float
        prev_value = self._rows_data[n].t_start
        try:
            new_value = float(text)
        except:
            item.setText(str(prev_value))
            return
        self._rows_data[n].t_start = new_value

        signal_data = {"n":n}
        self._controller.data_in_InitialStateWidget_changed.emit(signal_data)
        return
    
    def handle_t_end_changed(self, item, n):
        text = item.text()
        # Try to interplet input as float
        prev_value = self._rows_data[n].t_end
        try:
            new_value = float(text)
        except:
            item.setText(str(prev_value))
            return
        self._rows_data[n].t_end = new_value

        signal_data = {"n":n}
        self._controller.data_in_InitialStateWidget_changed.emit(signal_data)
        return
    
    def handle_t_steps_changed(self, item, n):
        text = item.text()
        # Try to interplet input as float
        prev_value = self._rows_data[n].t_steps
        try:
            new_value = int(text)
        except:
            item.setText(str(prev_value))
            return
        self._rows_data[n].t_steps = new_value

        signal_data = {"n":n}
        self._controller.data_in_InitialStateWidget_changed.emit(signal_data)
        return
    
    def handle_parameters_changed(self, *args, **kwargs):
        print(args, kwargs)
        signal_data = args[0]
        parameter_values = signal_data["parameter_values"]
        for n in range(self._row_count):
            new_signal_data = {"n":n, "parameter_values":parameter_values}
            self.handle_initial_state_changed_step2(new_signal_data)
        return
    
    def handle_labels_changed(self, *args, **kwargs):
        for i in range(self._row_count):
            signal_data = {"n":i, "trajectory":self._rows_data[i].trajectory}
            self._controller.trajectory_integrated.emit(signal_data)
        return