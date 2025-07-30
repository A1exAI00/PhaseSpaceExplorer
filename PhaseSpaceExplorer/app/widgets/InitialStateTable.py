import numpy as np

from PySide6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QComboBox, 
    QHeaderView, QLineEdit, QCheckBox, QPushButton)
# from PySide6.QtCore import Qt

from app.controllers.PhaseSpaceController import PhaseSpaceController

class InitialStateTable(QTableWidget):
    def __init__(
            self,
            variable_names: list[str],
            controller: PhaseSpaceController = None,
            parent=None):
        super().__init__(parent)

        self._controller: PhaseSpaceController = controller
        self._variable_names: list[str] = variable_names
        
        self._available_row_types: list[str] = ["Dragpoint", "SoE"]
        self._rows: list[RowDataDragpoint | RowDataSoE] = []

        self.setColumnCount(len(self._variable_names) + 15)
        
        self._default_headers = ["type",]
        self._default_headers = self.fill_headers(self._default_headers)

        self._headers_dragpoint = ["type",] + self._variable_names
        self._headers_dragpoint.append("Show")
        self._headers_dragpoint.append("dt")
        self._headers_dragpoint.append("t_start")
        self._headers_dragpoint.append("t_end")
        self._headers_dragpoint.append("t_steps")
        self._headers_dragpoint = self.fill_headers(self._headers_dragpoint)
        
        self._headers_SoE = ["type",] + self._variable_names
        self._headers_SoE.append("Show")
        self._headers_SoE.append("Correct")
        self._headers_SoE.append("Autoorrect")
        self._headers_SoE.append("dt")
        self._headers_SoE.append("eps")
        self._headers_SoE.append("Eig. N")
        self._headers_SoE.append("Eig. dir.")
        self._headers_SoE.append("t_start")
        self._headers_SoE.append("t_end")
        self._headers_SoE.append("t_steps")
        self._headers_SoE = self.fill_headers(self._headers_SoE)

        self.setHorizontalHeaderLabels(self._default_headers)
        
        self.connect_controller()
        return

    def get_row_type(self, row):
        return self._rows[row].type
    
    def get_row(self, row):
        return self._rows[row]
    
    def connect_controller(self):
        self.cellChanged.connect(self.on_cell_changed)
        self.currentCellChanged.connect(self.on_cell_focus_changed)
        if self._controller:
            # self._controller....
            pass
        return
    
    def clear_row(self, row):
        for col in range(self.columnCount()):
            # Remove any widget
            if self.cellWidget(row, col):
                self.removeCellWidget(row, col)
            # Remove any item
            if self.item(row, col):
                self.takeItem(row, col)
        return
    
    def add_row(self, row_type):
        self.setRowCount(self.rowCount()+1)

        if row_type == "Dragpoint":
            new_row = RowDataDragpoint(
                len(self._variable_names), 
                self._available_row_types)
            self._rows.append(new_row)
            new_row.add_to_table(self, self.rowCount()-1)

        if row_type == "SoE":
            new_row = RowDataSoE(
                len(self._variable_names), 
                self._available_row_types)
            self._rows.append(new_row)
            new_row.add_to_table(self, self.rowCount()-1)
        return

    def fill_headers(self, headers: list[str]):
        while (len(headers) < self.columnCount()):
            headers.append(f"opt {len(headers)}")
        return headers
    
    def on_type_changed(self, row, new_type):
        # Delete old row
        self.clear_row(row)
        old_row = self._rows[row]
        self._rows[row] = None
        del old_row
        
        if new_type == "Dragpoint":
            new_row = RowDataDragpoint(
                len(self._variable_names), 
                self._available_row_types)
            self._rows[row] = new_row
            new_row.add_to_table(self, row)

        if new_type == "SoE":
            new_row = RowDataSoE(
                len(self._variable_names), 
                self._available_row_types)
            self._rows[row] = new_row
            new_row.add_to_table(self, row)
        
        # If this row is currently focused, update headers
        if self.currentRow() == row:
            self.update_headers_based_on_focus()
        return
    
    def on_cell_focus_changed(self, current_row, current_col, previous_row, previous_col):
        self.update_headers_based_on_focus()
        return
    
    def update_headers_based_on_focus(self):
        current_row = self.currentRow()
        
        if current_row == -1:  # No focus
            self.setHorizontalHeaderLabels(self._default_headers)
        else:
            current_type = self.get_row_type(current_row)
            if current_type == "Dragpoint":
                self.setHorizontalHeaderLabels(self._headers_dragpoint)
            elif current_type == "SoE":
                self.setHorizontalHeaderLabels(self._headers_SoE)
        return
    
    def on_cell_changed(self, row, col):
        """Handle when cell content changes (if needed)"""
        return
    
    def handle_variable_changed(self, n, i):
        field = self._rows[n].variables_fields[i]
        prev_value = self._rows[n].variables[i]

        try:
            new_value = float(field.text())
        except:
            field.setText(str(prev_value))
            return
        self._rows[n].variables[i] = new_value
        field.setText(str(new_value))

        _type = self.get_row_type(n)
        signal_data = {"n":n, "type":_type}
        self._controller.data_changed.emit(signal_data)
        return
    
    def handle_show_change(self, state, n):
        self._rows[n].show = (state==2)

        # TODO emit signal
        return
    
    def handle_dt_changed(self, n, index_combo):
        self._rows[n].dt = ("+", "-")[index_combo]

        _type = self.get_row_type(n)
        signal_data = {"n":n, "type":_type}
        self._controller.data_changed.emit(signal_data)
        return
    
    def handle_t_start_changed(self, n):
        field = self._rows[n].t_start_field
        prev_value = self._rows[n].t_start

        try:
            new_value = float(field.text())
        except:
            field.setText(str(prev_value))
            return
        self._rows[n].t_start = new_value
        field.setText(str(new_value))

        _type = self.get_row_type(n)
        signal_data = {"n":n, "type":_type}
        self._controller.data_changed.emit(signal_data)
        return
    
    def handle_t_end_changed(self, n):
        field = self._rows[n].t_end_field
        prev_value = self._rows[n].t_end

        try:
            new_value = float(field.text())
        except:
            field.setText(str(prev_value))
            return
        self._rows[n].t_end = new_value
        field.setText(str(new_value))

        _type = self.get_row_type(n)
        signal_data = {"n":n, "type":_type}
        self._controller.data_changed.emit(signal_data)
        return
    
    def handle_t_steps_changed(self, n):
        field = self._rows[n].t_steps
        prev_value = self._rows[n].t_steps

        try:
            new_value = int(field.text())
        except:
            field.setText(str(prev_value))
            return
        self._rows[n].t_steps = new_value
        field.setText(str(new_value))

        _type = self.get_row_type(n)
        signal_data = {"n":n, "type":_type}
        self._controller.data_changed.emit(signal_data)
        return
    
    def handle_correct(self, n):
        # TODO
        return
    
    def handle_autocorrect_change(self, state, n):
        self._rows[n].autocorrect = (state==2)

        if (state==2):
            _type = self.get_row_type(n)
            signal_data = {"n":n, "type":_type}
            self._controller.data_changed.emit(signal_data)
        return
    
    def handle_eps_changed(self, n):
        field = self._rows[n].eps_field
        prev_value = self._rows[n].eps

        try:
            new_value = float(field.text())
        except:
            field.setText(f"{prev_value:.5E}")
            return
        self._rows[n].eps = new_value
        field.setText(f"{new_value:.5E}")

        _type = self.get_row_type(n)
        signal_data = {"n":n, "type":_type}
        self._controller.data_changed.emit(signal_data)
        return
    
    def handle_eig_N_changed(self, n):
        field = self._rows[n].eig_N
        prev_value = self._rows[n].eig_N

        try:
            new_value = int(field.text())
        except:
            field.setText(str(prev_value))
            return
        self._rows[n].eig_N = new_value
        field.setText(str(new_value))

        _type = self.get_row_type(n)
        signal_data = {"n":n, "type":_type}
        self._controller.data_changed.emit(signal_data)
        return
    
    def handle_eig_dir_changed(self, n, index_combo):
        self._rows[n].dt = ("+", "-")[index_combo] # TODO refactor ("+", "-")

        _type = self.get_row_type(n)
        signal_data = {"n":n, "type":_type}
        self._controller.data_changed.emit(signal_data)
        return

###############################################################################
###############################################################################

class RowDataDragpoint():
    def __init__(self, N_variables, available_types):
        self.N_variables = N_variables
        self.available_types = available_types
        # Data
        self.type = "Dragpoint"
        self.variables = np.zeros(self.N_variables)
        self.show = False
        self.dt = "+"
        self.t_start = 0.0
        self.t_end = 10.0
        self.t_steps = 1000
        
        # Views
        self.type_field = None
        self.variables_fields = None
        self.show_field = None
        self.dt_field = None
        self.t_start_field = None
        self.t_end_field = None
        self.t_steps_field = None
        return
    
    def add_to_table(self, table:InitialStateTable, n:int):
        self.type_field = QComboBox()
        self.type_field.addItems(self.available_types)
        self.type_field.setCurrentIndex(self.available_types.index(self.type))
        self.type_field.currentTextChanged.connect(
            lambda text, n=n:
            table.on_type_changed(n, text))
        table.setCellWidget(n, 0, self.type_field)

        self.variables_fields = [None,]*self.N_variables
        for i in range(self.N_variables):
            field = QLineEdit()
            field.setPlaceholderText(str(self.variables[i]))
            field.editingFinished.connect(
                lambda n=n, i=i:
                table.handle_variable_changed(n, i))
            table.setCellWidget(n, 1+i, field)
            self.variables_fields[i] = field

        self.show_field = QCheckBox() # TODO how to fucking set the state to checked
        self.show_field.stateChanged.connect(
            lambda state, n=n: 
            table.handle_show_change(state, n))
        table.setCellWidget(n, self.N_variables+1, self.show_field)

        self.dt_field = QComboBox()
        self.dt_field.addItems(("+", "-"))
        self.dt_field.setCurrentIndex(0)
        self.dt_field.currentIndexChanged.connect(
            lambda index_combobox, n=n:
            table.handle_dt_changed(n, index_combobox))
        table.setCellWidget(n, self.N_variables+2, self.dt_field)

        self.t_start_field = QLineEdit()
        self.t_start_field.setPlaceholderText(str(self.t_start))
        self.t_start_field.editingFinished.connect(
            lambda n=n:
            table.handle_t_start_changed(n))
        table.setCellWidget(n, self.N_variables+3, self.t_start_field)

        self.t_end_field = QLineEdit()
        self.t_end_field.setPlaceholderText(str(self.t_end))
        self.t_end_field.editingFinished.connect(
            lambda n=n:
            table.handle_t_end_changed(n))
        table.setCellWidget(n, self.N_variables+4, self.t_end_field)

        self.t_steps_field = QLineEdit()
        self.t_steps_field.setPlaceholderText(str(self.t_steps))
        self.t_steps_field.editingFinished.connect(
            lambda n=n:
            table.handle_t_steps_changed(n))
        table.setCellWidget(n, self.N_variables+5, self.t_steps_field)
        return
    
###############################################################################
###############################################################################

class RowDataSoE():
    def __init__(self, N_variables, available_types):
        self.N_variables = N_variables
        self.available_types = available_types
        # Data
        self.type = "SoE"
        self.variables = np.zeros(self.N_variables)
        self.show = False
        self.autocorrect = False
        self.dt = "+"
        self.eps = 1e-5
        self.eig_N = 0
        self.eig_dir = "+"
        self.t_start = 0.0
        self.t_end = 10.0
        self.t_steps = 1000

        # Views
        self.type_field = None
        self.variables_fields = None
        self.show_field = None
        self.correct_field = None
        self.autocorrect_field = None
        self.dt_field = None
        self.eps_field = None
        self.eig_N_field = None
        self.eig_dir_field = None
        self.t_start_field = None
        self.t_end_field = None
        self.t_steps_field = None
        return
    
    def add_to_table(self, table, n):
        self.type_field = QComboBox()
        self.type_field.addItems(self.available_types)
        self.type_field.setCurrentIndex(self.available_types.index(self.type))
        self.type_field.currentTextChanged.connect(
            lambda text, n=n: 
            table.on_type_changed(n, text))
        table.setCellWidget(n, 0, self.type_field)

        self.variables_fields = [None,]*self.N_variables
        for i in range(self.N_variables):
            field = QLineEdit()
            field.setPlaceholderText(str(self.variables[i]))
            field.editingFinished.connect(
                lambda n=n, i=i:
                table.handle_variable_changed(n, i))
            table.setCellWidget(n, 1+i, field)
            self.variables_fields[i] = field

        self.show_field = QCheckBox() # TODO how to fucking set the state to checked
        self.show_field.stateChanged.connect(
            lambda state, n=n: 
            table.handle_show_change(state, n))
        table.setCellWidget(n, self.N_variables+1, self.show_field)

        self.correct_field = QPushButton("Correct")
        self.correct_field.clicked.connect(
            lambda n=n:
            table.handle_correct(n))
        table.setCellWidget(n, self.N_variables+2, self.correct_field)

        self.autocorrect_field = QCheckBox()
        self.autocorrect_field.stateChanged.connect(
            lambda state, n=n: 
            table.handle_autocorrect_change(state, n))
        table.setCellWidget(n, self.N_variables+3, self.autocorrect_field)

        self.dt_field = QComboBox()
        self.dt_field.addItems(("+", "-"))
        self.dt_field.setCurrentIndex(0)
        self.dt_field.currentIndexChanged.connect(
            lambda index_combobox, n=n:
            table.handle_dt_changed(n, index_combobox))
        table.setCellWidget(n, self.N_variables+4, self.dt_field)

        self.eps_field = QLineEdit()
        self.eps_field.setPlaceholderText(str(self.eps))
        self.eps_field.editingFinished.connect(
            lambda n=n:
            table.handle_eps_changed(n))
        table.setCellWidget(n, self.N_variables+5, self.eps_field)

        self.eig_N_field = QLineEdit()
        self.eig_N_field.setPlaceholderText(str(self.eig_N))
        self.eig_N_field.editingFinished.connect(
            lambda n=n:
            table.handle_eig_N_changed(n))
        table.setCellWidget(n, self.N_variables+6, self.eig_N_field)

        self.eig_dir_field = QComboBox()
        self.eig_dir_field.addItems(("+", "-"))
        self.eig_dir_field.setCurrentIndex(0)
        self.eig_dir_field.currentIndexChanged.connect(
            lambda index_combobox, n=n:
            table.handle_eig_dir_changed(n, index_combobox))
        table.setCellWidget(n, self.N_variables+7, self.eig_dir_field)

        self.t_start_field = QLineEdit()
        self.t_start_field.setPlaceholderText(str(self.t_start))
        self.t_start_field.editingFinished.connect(
            lambda n=n:
            table.handle_t_start_changed(n))
        table.setCellWidget(n, self.N_variables+8, self.t_start_field)

        self.t_end_field = QLineEdit()
        self.t_end_field.setPlaceholderText(str(self.t_end))
        self.t_end_field.editingFinished.connect(
            lambda n=n:
            table.handle_t_end_changed(n))
        table.setCellWidget(n, self.N_variables+9, self.t_end_field)

        self.t_steps_field = QLineEdit()
        self.t_steps_field.setPlaceholderText(str(self.t_steps))
        self.t_steps_field.editingFinished.connect(
            lambda n=n:
            table.handle_t_steps_changed(n))
        table.setCellWidget(n, self.N_variables+10, self.t_steps_field)
        return