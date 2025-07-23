from typing import List

from PySide6.QtWidgets import QVBoxLayout, QWidget, QComboBox, QHBoxLayout, QPushButton
from PySide6.QtCore import QTimer

from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
# import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from app.controllers.PhaseSpaceController import PhaseSpaceController
from backend.DynamicalSystem import DynamicalSystem

class PhaseSpacePlotWidget(QWidget):
    def __init__(self, ds:DynamicalSystem, controller:PhaseSpaceController):
        super().__init__()
        self._ds:DynamicalSystem = ds
        self._controller = controller

        self._available_labels = self._ds.variable_names + ["t",]

        self._canvas = MyCanvas(
            self._available_labels,
            width=5, height=4, dpi=100)

        self._mylines:List[MyLine] = [] # TODO move this list into canvas class

        self.setup_ui()
        self.connect_controller()

        # Setup a timer to trigger the redraw by calling wake_canvas
        # self.timer = QTimer()
        # self.timer.setInterval(1000)
        # self.timer.timeout.connect(self.wake_canvas)
        # self.timer.start()
        return
    
    def setup_ui(self):
        # Setup layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        labels_layout = QHBoxLayout()
        layout.addLayout(labels_layout)

        x_axis_label_combobox = QComboBox()
        y_axis_label_combobox = QComboBox()
        for label in self._available_labels:
            x_axis_label_combobox.addItem(label)
            y_axis_label_combobox.addItem(label)
        x_axis_label_combobox.setCurrentIndex(self._canvas.x_label_index)
        y_axis_label_combobox.setCurrentIndex(self._canvas.y_label_index)
        x_axis_label_combobox.currentIndexChanged.connect(
            lambda label, axis="x":
            self.handle_axis_label_changed(label, axis))
        y_axis_label_combobox.currentIndexChanged.connect(
            lambda label, axis="y":
            self.handle_axis_label_changed(label, axis))
        labels_layout.addWidget(x_axis_label_combobox)
        labels_layout.addWidget(y_axis_label_combobox)

        fit_btn = QPushButton("Fit to plot")
        fit_btn.clicked.connect(self._canvas.autoscale)
        layout.addWidget(fit_btn)

        toolbar = NavigationToolbar(self._canvas, self)
        layout.addWidget(toolbar)

        layout.addWidget(self._canvas)
        return
    
    def connect_controller(self):
        self._controller.trajectory_integrated.connect(self.handle_trajectory_integrated)
        return
    
    def wake_canvas(self):
        self._canvas.draw()
        return
    
    def handle_trajectory_integrated(self, signal_data):
        n = signal_data["n"]
        trajectory = signal_data["trajectory"]

        x_label_index = self._canvas.x_label_index
        y_label_index = self._canvas.y_label_index

        if x_label_index != len(self._available_labels)-1:
            to_plot_xs = [trajectory.y_sols[i][x_label_index,:] for i in range(len(trajectory.y_sols))]
        else:
            to_plot_xs = trajectory.t_sols

        if y_label_index != len(self._available_labels)-1:
            to_plot_ys = [trajectory.y_sols[i][y_label_index,:] for i in range(len(trajectory.y_sols))]
        else:
            to_plot_ys = trajectory.t_sols

        # Check if new MyLine is needed
        if n > len(self._mylines)-1:
            self._mylines.append(MyLine(self._canvas))

        self._mylines[n].update(to_plot_xs, to_plot_ys)
        self.wake_canvas()
        return
    
    def handle_axis_label_changed(self, label, axis):
        if axis == "x":
            self._canvas.x_label_index = label
        if axis == "y":
            self._canvas.y_label_index = label

        self._controller.labels_changed.emit({})
        return


class MyCanvas(FigureCanvas):
    def __init__(self, available_labels, x_label_index=0, y_label_index=1, 
                 parent=None, width=5, height=4, dpi=100):
        # Scroll wheel zoom 
        self._base_scale = 1.2

        self._available_labels = available_labels
        self._x_label_index = x_label_index
        self._y_label_index = y_label_index

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.margins(0.05, 0.05)
        super().__init__(self.fig)
        self.fig.canvas.mpl_connect('scroll_event', self.zoom_fun)

        self.axes.set_xlabel(self._available_labels[self._x_label_index])
        self.axes.set_ylabel(self._available_labels[self._y_label_index])
        return
    
    @property
    def x_label_index(self):
        return self._x_label_index
    @x_label_index.setter
    def x_label_index(self, index):
        self._x_label_index = index
        self.axes.set_xlabel(self._available_labels[self._x_label_index])
        return
    
    @property
    def y_label_index(self):
        return self._y_label_index
    @y_label_index.setter
    def y_label_index(self, index):
        self._y_label_index = index
        self.axes.set_ylabel(self._available_labels[self._y_label_index])
        return
    
    @property
    def x_label(self):
        return self._available_labels[self._x_label_index]
    
    @property
    def y_label(self):
        return self._available_labels[self._y_label_index]
    
    def autoscale(self):
        self.axes.autoscale()
        return
    
    def wake(self):
        self.draw()
    
    def zoom_fun(self, event):
        # get the current x and y limits
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()
        cur_xrange = (cur_xlim[1] - cur_xlim[0])*.5
        cur_yrange = (cur_ylim[1] - cur_ylim[0])*.5
        xdata = event.xdata # get event x location
        ydata = event.ydata # get event y location
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1/self._base_scale
        elif event.button == 'down':
            # deal with zoom out
            scale_factor = self._base_scale
        else:
            # deal with something that should never happen
            scale_factor = 1
            print(event.button)
        # set new limits
        self.axes.set_xlim([xdata - cur_xrange*scale_factor,
                     xdata + cur_xrange*scale_factor])
        self.axes.set_ylim([ydata - cur_yrange*scale_factor,
                     ydata + cur_yrange*scale_factor])
        self.draw() # force re-draw


class MyLine():
    def __init__(self, canvas:MyCanvas):
        self._canvas = canvas
        self._refs:List[Line2D] = []
        return
    
    def update(self, x_datas, y_datas):
        assert len(x_datas) == len(y_datas)

        # Remove excess references if we have more than needed
        while len(self._refs) > len(x_datas):
            removed_ref = self._refs.pop()
            removed_ref.remove()
        
        # Add new references if we need more
        while len(self._refs) < len(x_datas):
            new_ref, = self._canvas.axes.plot([], [])  # Create empty line
            self._refs.append(new_ref)

        # Update all references with new data
        for (x_data, y_data, ref) in zip(x_datas, y_datas, self._refs):
            ref.set_data(x_data, y_data)
        return