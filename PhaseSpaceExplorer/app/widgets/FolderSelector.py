from copy import deepcopy

import numpy as np
from PySide6 import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox, QLineEdit, QCheckBox, QFileDialog, QLabel

# For VSCode autocomplete, to avoid circular import
# from typing import TYPE_CHECKING
# if TYPE_CHECKING:
#     from gui.WorkbenchPhaseSpace import WorkbenchPhaseSpace

from app.controllers.MainController import MainController

class FolderSelector(QWidget):
    def __init__(self, controller:MainController, parent=None):
        super().__init__(parent)

        self._controller = controller
        
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        label = QLabel("Choose Dynamical System folder:")
        layout.addWidget(label)
        
        folder_chooser_layout = QHBoxLayout()
        layout.addLayout(folder_chooser_layout)

        self.line_edit = QLineEdit()
        folder_chooser_layout.addWidget(self.line_edit)
        self.browse_button = QPushButton("Browse...")
        folder_chooser_layout.addWidget(self.browse_button)
        
        self.browse_button.clicked.connect(self.browse_folder)
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.line_edit.setText(folder)
            self._controller.ds_folder_selected.emit(self.folder)
        return
    
    @property
    def folder(self):
        return self.line_edit.text()