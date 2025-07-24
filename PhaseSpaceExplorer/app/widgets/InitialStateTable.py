import numpy as np

from PySide6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QComboBox, 
    QHeaderView, QLineEdit, QCheckBox, QPushButton)
# from PySide6.QtCore import Qt

from app.controllers.PhaseSpaceController import PhaseSpaceController

class RowDataDragpoint():
    def __init__(self, N_variables):
        self.type = "Dragpoint"
        self.variables = np.zeros(N_variables)
        self.show = False
        self.dt = "+"
        self.t_start = 0.0
        self.t_end = 10.0
        self.t_steps = 1000
        return
    
class RowDataSoE():
    def __init__(self, N_variables):
        self.type = "SoE"
        self.variables = np.zeros(N_variables)
        self.show = False
        self.autocorrect = False
        self.dt = "+"
        self.eps = 1e-5
        self.eig_N = 0
        self.eig_dir = "+"
        self.t_start = 0.0
        self.t_end = 10.0
        self.t_steps = 1000
        return

class InitialStateTable(QTableWidget):
    def __init__(
            self,
            variable_names,
            controller:PhaseSpaceController=None,
            parent=None):
        super().__init__(parent)

        self._controller = controller
        self._variable_names = variable_names

        
        self._available_row_types = ["Dragpoint", "SoE"]
        self._row_types = []
        self._row_datas = []
        
        self._default_headers = ["type",]
        self.fill_headers(self._default_headers)

        self._headers_dragpoint = ["type",] + self._variable_names
        self._headers_dragpoint.append("Show")
        self._headers_dragpoint.append("dt")
        self._headers_dragpoint.append("t_start")
        self._headers_dragpoint.append("t_end")
        self._headers_dragpoint.append("t_steps")
        self.fill_headers(self._headers_dragpoint)
        
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
        self.fill_headers(self._headers_SoE)
        
        # Set initial headers
        self.setColumnCount(len(self._variable_names) + 15)
        self.setHorizontalHeaderLabels(self._default_headers)
        
        # Populate the table with combo boxes and data
        self.populate_table()
        
        # Connect signals
        
        self.connect_controller()
        return
    
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
    
    def populate_row_dragpoint(self, row):
        self._row_types[row] = "Dragpoint"
        data_obj = self._row_datas[row]
        
        combo = QComboBox()
        combo.addItems(self._available_row_types)
        combo.setCurrentIndex(self._available_row_types.index(data_obj.type))
        combo.currentTextChanged.connect(
            lambda text, row=row: 
            self.on_type_changed(row, text))
        self.setCellWidget(row, 0, combo)

        for i in range(len(self._variable_names)):
            field = QLineEdit(placeholderText="0.0") # TODO 
            field.editingFinished.connect(
                lambda item=field, row=row, i=i:
                self.handle_variable_changed(item, row, i))
            self.setCellWidget(row, 1+i, field)

        show = QCheckBox() # TODO how to fucking set the state to checked
        show.stateChanged.connect(
            lambda state, row=row: 
            self.handle_show_change(state, row))
        self.setCellWidget(row, len(self._variable_names)+1, show)

        dt = QComboBox(currentText=data_obj.dt)
        dt.addItem("+")
        dt.addItem("-")
        dt.currentIndexChanged.connect(
            lambda index_combobox, row=row:
            self.handle_dt_changed(row, index_combobox))
        self.setCellWidget(row, len(self._variable_names)+2, dt)

        t_start = QLineEdit(placeholderText=str(data_obj.t_start))
        t_start.editingFinished.connect(
            lambda item=t_start, row=row:
            self.handle_t_start_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+3, t_start)

        t_end = QLineEdit(placeholderText=str(data_obj.t_end))
        t_end.editingFinished.connect(
            lambda item=t_end, row=row:
            self.handle_t_end_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+4, t_end)

        t_steps = QLineEdit(placeholderText=str(data_obj.t_steps))
        t_steps.editingFinished.connect(
            lambda item=t_steps, row=row:
            self.handle_t_steps_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+5, t_steps)
        return
    
    def populate_row_SoE(self, row):
        self._row_types[row] = "SoE"
        data_obj = self._row_datas[row]

        combo = QComboBox()
        combo.addItems(self._available_row_types)
        combo.setCurrentIndex(1)
        combo.currentTextChanged.connect(
            lambda text, row=row: 
            self.on_type_changed(row, text))
        self.setCellWidget(row, 0, combo)

        for i in range(len(self._variable_names)):
            field = QLineEdit(placeholderText="0.0") # TODO 
            field.editingFinished.connect(
                lambda item=field, row=row, i=i:
                self.handle_variable_changed(item, row, i))
            self.setCellWidget(row, 1+i, field)

        show = QCheckBox() # TODO how to fucking set the state to checked
        show.stateChanged.connect(
            lambda state, row=row: 
            self.handle_show_change(state, row))
        self.setCellWidget(row, len(self._variable_names)+1, show)

        correct = QPushButton("Correct")
        correct.clicked.connect(
            lambda row=row:
            self.handle_correct(row))
        self.setCellWidget(row, len(self._variable_names)+2, correct)

        autocorrect = QCheckBox()
        autocorrect.stateChanged.connect(
            lambda state, row=row: 
            self.handle_autocorrect_change(state, row))
        self.setCellWidget(row, len(self._variable_names)+3, autocorrect)

        dt = QComboBox(currentText=data_obj.dt)
        dt.addItem("+")
        dt.addItem("-")
        dt.currentIndexChanged.connect(
            lambda index_combobox, row=row:
            self.handle_dt_changed(row, index_combobox))
        self.setCellWidget(row, len(self._variable_names)+4, dt)

        eps = QLineEdit(placeholderText=str(data_obj.eps))
        eps.editingFinished.connect(
            lambda item=eps, row=row:
            self.handle_eps_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+5, eps)

        eig_N = QLineEdit(placeholderText=str(data_obj.eig_N))
        eig_N.editingFinished.connect(
            lambda item=eig_N, row=row:
            self.handle_eig_N_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+6, eig_N)

        eig_dir = QComboBox(currentText=data_obj.eig_dir)
        eig_dir.addItem("+")
        eig_dir.addItem("-")
        eig_dir.currentIndexChanged.connect(
            lambda index_combobox, row=row:
            self.handle_eig_dir_changed(row, index_combobox))
        self.setCellWidget(row, len(self._variable_names)+7, eig_dir)

        t_start = QLineEdit(placeholderText=str(data_obj.t_start))
        t_start.editingFinished.connect(
            lambda item=t_start, row=row:
            self.handle_t_start_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+8, t_start)

        t_end = QLineEdit(placeholderText=str(data_obj.t_end))
        t_end.editingFinished.connect(
            lambda item=t_end, row=row:
            self.handle_t_end_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+9, t_end)

        t_steps = QLineEdit(placeholderText=str(data_obj.t_steps))
        t_steps.editingFinished.connect(
            lambda item=t_steps, row=row:
            self.handle_t_steps_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+10, t_steps)
        return
    
    def add_row(self, row_type):
        self.setRowCount(self.rowCount()+1)

        if row_type == "Dragpoint":
            self._row_types.append("Dragpoint")
            self._row_datas.append(RowDataDragpoint(len(self._variable_names)))
            self.populate_row_dragpoint(self.rowCount()-1)
        if row_type == "SoE":
            self._row_types.append("SoE")
            self._row_datas.append(RowDataSoE(len(self._variable_names)))
            self.populate_row_SoE(self.rowCount()-1)
        return

    def fill_headers(self, headers):
        while (len(headers) < self.columnCount()):
            headers.append(f"opt {len(headers)}")
        return
    
    def populate_table(self):
        self.add_row("Dragpoint")
        self.add_row("SoE")
        return
    
    def on_type_changed(self, row, new_type):
        """Handle when the type combo box changes for a row"""
        self._row_types[row] = new_type
        # Update the data in other columns to match new type
        self.clear_row(row)

        if new_type == "Dragpoint":
            self._row_datas[row] = RowDataDragpoint(len(self._variable_names))
            self.populate_row_dragpoint(row)
        if new_type == "SoE":
            self._row_datas[row] = RowDataSoE(len(self._variable_names))
            self.populate_row_SoE(row)
        
        # If this row is currently focused, update headers
        if self.currentRow() == row:
            self.update_headers_based_on_focus()
        return
    
    def on_cell_focus_changed(self, current_row, current_col, previous_row, previous_col):
        """Handle when focus changes between cells"""
        self.update_headers_based_on_focus()
        return
    
    def update_headers_based_on_focus(self):
        """Update headers based on which cell (if any) has focus"""
        current_row = self.currentRow()
        
        if current_row == -1:  # No focus
            self.setHorizontalHeaderLabels(self._default_headers)
        else:
            current_type = self._row_types[current_row]
            if current_type == "Dragpoint":
                self.setHorizontalHeaderLabels(self._headers_dragpoint)
            elif current_type == "SoE":
                self.setHorizontalHeaderLabels(self._headers_SoE)
        return
    
    def on_cell_changed(self, row, col):
        """Handle when cell content changes (if needed)"""
        return
    
    def handle_variable_changed(self, item, n, i):
        prev_value = self._row_datas[n].variables[i]

        try:
            new_value = float(item.text())
        except:
            item.setText(str(prev_value))
            return
        self._row_datas[n].variables[i] = new_value
        item.setText(str(new_value))

        # TODO emit signal
        return
    
    def handle_show_change(self, state, n):
        self._row_datas[n].show = (state==2)

        # TODO emit signal
        return
    
    def handle_dt_changed(self, n, index_combo):
        self._row_datas[n].dt = ("+", "-")[index_combo] # TODO refactor ("+", "-")

        # TODO emit signal
        return
    
    def handle_t_start_changed(self, item, n):
        prev_value = self._row_datas[n].t_start

        try:
            new_value = float(item.text())
        except:
            item.setText(str(prev_value))
            return
        self._row_datas[n].t_start = new_value
        item.setText(str(new_value))

        # TODO emit signal
        return
    
    def handle_t_end_changed(self, item, n):
        prev_value = self._row_datas[n].t_end

        try:
            new_value = float(item.text())
        except:
            item.setText(str(prev_value))
            return
        self._row_datas[n].t_end = new_value
        item.setText(str(new_value))

        # TODO emit signal
        return
    
    def handle_t_steps_changed(self, item, n):
        prev_value = self._row_datas[n].t_steps

        try:
            new_value = int(item.text())
        except:
            item.setText(str(prev_value))
            return
        self._row_datas[n].t_steps = new_value
        item.setText(str(new_value))

        # TODO emit signal
        return
    
    def handle_correct(self, n):
        # TODO
        return
    
    def handle_autocorrect_change(self, state, n):
        self._row_datas[n].autocorrect = (state==2)

        # TODO emit signal
        return
    
    def handle_eps_changed(self, item, n):
        prev_value = self._row_datas[n].eps

        try:
            new_value = float(item.text())
        except:
            item.setText(f"{prev_value:.5E}")
            return
        self._row_datas[n].eps = new_value
        item.setText(f"{new_value:.5E}")

        # TODO emit signal
        return
    
    def handle_eig_N_changed(self, item, n):
        prev_value = self._row_datas[n].eig_N

        try:
            new_value = int(item.text())
        except:
            item.setText(str(prev_value))
            return
        self._row_datas[n].eig_N = new_value
        item.setText(str(new_value))

        # TODO emit signal
        return
    
    def handle_eig_dir_changed(self, n, index_combo):
        self._row_datas[n].dt = ("+", "-")[index_combo] # TODO refactor ("+", "-")

        # TODO emit signal
        return


# Example usage
if __name__ == "__main__":
    app = QApplication([])
    
    table = InitialStateTable(["x", "y", "z"])
    table.resize(600, 300)
    table.show()
    
    app.exec()