from PySide6.QtWidgets import (QApplication, QMainWindow, QMdiArea, QMdiSubWindow)

from app.controllers.PhaseSpaceController import PhaseSpaceController
from app.controllers.MainController import MainController
from app.widgets.ODEsParameterWidget import ODEsParametersWidget
from app.widgets.InitialStateWidget import InitialStateWidget
from app.widgets.PhaseSpacePlotWidget import PhaseSpacePlotWidget
from app.widgets.FolderSelector import FolderSelector

from backend.DynamicalSystem import DynamicalSystem

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._main_controller = MainController()
        self.setup_ui()
        self.connect_controller()
        return

    def setup_ui(self):
        self.setWindowTitle("PhaseSpaceExplorer by Alex Akinin")
        self.setGeometry(50, 50, 1700, 900)

        # Create MDI area
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        self.setup_DsChooser()
        return
    
    def connect_controller(self):
        self._main_controller.ds_folder_selected.connect(self.handle_ds_folder_selected)
        return

    def setup_DsChooser(self):
        ds_chooser = QMdiSubWindow()
        self.ds_chooser = ds_chooser
        ds_chooser.setGeometry(50, 50, 500, 100)
        ds_chooser_widget = FolderSelector(self._main_controller)
        ds_chooser.setWidget(ds_chooser_widget)
        self.mdi.addSubWindow(ds_chooser)
        ds_chooser.show()
        return
    
    def delete_DsChooser(self):
        return
        
    def setup_PhaseSpaceWorkbench(self):
        self.ps_controller = PhaseSpaceController()
        
        # Create and add ODEs Parameter Subwindow
        ops = QMdiSubWindow()
        ops.setGeometry(0, 0, 500, 200)
        ops_widget = ODEsParametersWidget(self.ds, self.ps_controller)
        ops.setWidget(ops_widget)
        ops.setWindowTitle("ODEs Parameters")
        self.mdi.addSubWindow(ops)
        ops.show()

        # Create and add Initial State Subwindow
        iss = QMdiSubWindow()
        iss.setGeometry(500, 0, 1000, 200)
        iss_widget = InitialStateWidget(self.ds, self.ps_controller)
        iss.setWidget(iss_widget)
        iss.setWindowTitle("Initial States")
        self.mdi.addSubWindow(iss)
        iss.show()

        # Create and add Phase Space Plot Subwindow
        psps = QMdiSubWindow()
        psps.setGeometry(0, 200, 500, 500)
        psps_widget = PhaseSpacePlotWidget(self.ds, self.ps_controller)
        psps.setWidget(psps_widget)
        iss.setWindowTitle("Phase Space Plot")
        self.mdi.addSubWindow(psps)
        psps.show()
        return
    
    def handle_ds_folder_selected(self, path:str):
        self.ds = DynamicalSystem()
        self.ds.load_from_py(path)
        print(self.ds)
        self.mdi.removeSubWindow(self.ds_chooser)
        self.setup_PhaseSpaceWorkbench()
        return