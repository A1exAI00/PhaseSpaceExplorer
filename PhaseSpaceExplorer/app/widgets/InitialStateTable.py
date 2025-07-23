from PySide6.QtWidgets import (
    QApplication, QTableWidget, QTableWidgetItem, QComboBox, 
    QHeaderView, QLineEdit, QCheckBox, QPushButton)
# from PySide6.QtCore import Qt

class DynamicHeaderTable(QTableWidget):
    def __init__(
            self,
            variable_names,
            parent=None):
        super().__init__(parent)

        self._variable_names = variable_names

        self.setColumnCount(len(self._variable_names) + 10)
        # self.setRowCount()
        
        self._row_types = ["Dragpoint", "SoE"]
        
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
        self.setHorizontalHeaderLabels(self._default_headers)
        
        # Populate the table with combo boxes and data
        self.populate_table()
        
        # Connect signals
        self.cellChanged.connect(self.on_cell_changed)
        self.currentCellChanged.connect(self.on_cell_focus_changed)
        return
    
    def clear_row(self, row):
        for col in range(self.columnCount()):
            # Remove any widget
            if self.cellWidget(row, col):
                self.removeCellWidget(row, col)
            
            # Remove any item
            if self.item(row, col):
                self.takeItem(row, col)
    
    def populate_row_dragpoint(self, row):
        combo = QComboBox()
        combo.addItems(self._row_types)
        combo.setCurrentIndex(0)
        combo.currentTextChanged.connect(
            lambda text, row=row: 
            self.on_type_changed(row, text))
        self.setCellWidget(row, 0, combo)

        for i in range(len(self._variable_names)):
            field = QLineEdit(placeholderText="0.0") # TODO 
            field.editingFinished.connect(
                lambda item=field, row=row, i=i:
                self.handle_variable_changed(item.text(), row, i))
            self.setCellWidget(row, 1+i, field)

        show = QCheckBox() # TODO how to fucking set the state to checked
        show.stateChanged.connect(
            lambda state, row=row: 
            self.handle_show_change(state, row))
        self.setCellWidget(row, len(self._variable_names)+1, show)

        dt = QComboBox(currentText="+") # TODO
        dt.addItem("+")
        dt.addItem("-")
        dt.currentIndexChanged.connect(
            lambda index_combobox, row=row:
            self.handle_dt_changed(row, index_combobox))
        self.setCellWidget(row, len(self._variable_names)+2, dt)

        t_start = QLineEdit(placeholderText="0.0") # TODO
        t_start.editingFinished.connect(
            lambda item=t_start, row=row:
            self.handle_t_start_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+3, t_start)

        t_end = QLineEdit(placeholderText="10.0") # TODO
        t_end.editingFinished.connect(
            lambda item=t_end, row=row:
            self.handle_t_end_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+4, t_end)

        t_steps = QLineEdit(placeholderText="1000") # TODO
        t_steps.editingFinished.connect(
            lambda item=t_steps, row=row:
            self.handle_t_steps_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+5, t_steps)
        return
    
    def populate_row_SoE(self, row):
        combo = QComboBox()
        combo.addItems(self._row_types)
        combo.setCurrentIndex(0)
        combo.currentTextChanged.connect(
            lambda text, row=row: 
            self.on_type_changed(row, text))
        self.setCellWidget(row, 0, combo)

        for i in range(len(self._variable_names)):
            field = QLineEdit(placeholderText="0.0") # TODO 
            field.editingFinished.connect(
                lambda item=field, row=row, i=i:
                self.handle_variable_changed(item.text(), row, i))
            self.setCellWidget(row, 1+i, field)

        show = QCheckBox() # TODO how to fucking set the state to checked
        show.stateChanged.connect(
            lambda state, row=row: 
            self.handle_show_change(state, row))
        self.setCellWidget(row, len(self._variable_names)+1, show)

        correct = QPushButton("Correct")
        correct.click.connect(
            lambda row=row:
            self.handle_correct(row))
        self.setCellWidget(row, len(self._variable_names)+2, show)

        autocorrect = QCheckBox()
        autocorrect.stateChanged.connect(
            lambda state, row=row: 
            self.handle_autocorrect_change(state, row))
        self.setCellWidget(row, len(self._variable_names)+3, autocorrect)

        dt = QComboBox(currentText="+") # TODO
        dt.addItem("+")
        dt.addItem("-")
        dt.currentIndexChanged.connect(
            lambda index_combobox, row=row:
            self.handle_dt_changed(row, index_combobox))
        self.setCellWidget(row, len(self._variable_names)+4, dt)

        eps = QLineEdit(placeholderText="1e-5") # TODO 
        eps.editingFinished.connect(
            lambda item=eps, row=row, i=i:
            self.handle_eps_changed(item.text(), row, i))
        self.setCellWidget(row, len(self._variable_names)+5, eps)

        eig_N = QLineEdit(placeholderText="0") # TODO 
        eig_N.editingFinished.connect(
            lambda item=eig_N, row=row, i=i:
            self.handle_eig_N_changed(item.text(), row, i))
        self.setCellWidget(row, len(self._variable_names)+5, eig_N)

        eig_dir = QComboBox(currentText="+") # TODO
        eig_dir.addItem("+") # TODO
        eig_dir.addItem("-") # TODO
        eig_dir.currentIndexChanged.connect(
            lambda index_combobox, row=row:
            self.handle_eig_dir_changed(row, index_combobox))
        self.setCellWidget(row, len(self._variable_names)+6, eig_dir)

        t_start = QLineEdit(placeholderText="0.0") # TODO
        t_start.editingFinished.connect(
            lambda item=t_start, row=row:
            self.handle_t_start_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+7, t_start)

        t_end = QLineEdit(placeholderText="10.0") # TODO
        t_end.editingFinished.connect(
            lambda item=t_end, row=row:
            self.handle_t_end_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+8, t_end)

        t_steps = QLineEdit(placeholderText="1000") # TODO
        t_steps.editingFinished.connect(
            lambda item=t_steps, row=row:
            self.handle_t_steps_changed(item, row))
        self.setCellWidget(row, len(self._variable_names)+9, t_steps)
        return
    
    def add_row(self):
        self.setRowCount(self.rowCount()+1)
        self.populate_row_dragpoint(self.rowCount()-1)
        return

    def fill_headers(self, headers):
        while (len(headers) < self.columnCount()):
            headers.append(f"opt {len(headers)}")
        return
    
    def populate_table(self):
        self.add_row()
        self.populate_row_dragpoint(0)
    
    def on_type_changed(self, row, new_type):
        """Handle when the type combo box changes for a row"""
        self._row_types[row] = new_type
        # Update the data in other columns to match new type
        for col in range(1, self.columnCount()):
            self.item(row, col).setText(f"{new_type}_data{col}")
        
        # If this row is currently focused, update headers
        if self.currentRow() == row:
            self.update_headers_based_on_focus()
    
    def on_cell_focus_changed(self, current_row, current_col, previous_row, previous_col):
        """Handle when focus changes between cells"""
        self.update_headers_based_on_focus()
    
    def update_headers_based_on_focus(self):
        """Update headers based on which cell (if any) has focus"""
        current_row = self.currentRow()
        
        if current_row == -1:  # No focus
            self.setHorizontalHeaderLabels(self._default_headers)
        else:
            current_type = self._row_types[current_row]
            if current_type == "ff":
                self.setHorizontalHeaderLabels(self._headers_dragpoint)
            elif current_type == "SoE":
                self.setHorizontalHeaderLabels(self._headers_SoE)
    
    def on_cell_changed(self, row, col):
        """Handle when cell content changes (if needed)"""
        pass  # Add any additional handling if needed


# Example usage
if __name__ == "__main__":
    app = QApplication([])
    
    table = DynamicHeaderTable(["x", "y", "z"])
    table.resize(600, 300)
    table.show()
    
    app.exec()