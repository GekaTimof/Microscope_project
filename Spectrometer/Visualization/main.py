import sys
import numpy as np
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
import pyqtgraph as pg
from PyQt5.QtGui import QIcon

from SpectrometerOptoskyConnection import SpectrometerConnection

# visual_testing function and links for test data
from SpectrometerOptoskyConnection import get_data_from_file
from SpectrometerOptoskyConnection import X_file_path, Y_file_path


class DataThread(QThread):
    new_data = pyqtSignal(np.ndarray, np.ndarray)

    def __init__(self):
        super().__init__()
        self.testing = False
        self.running = True
        self.connection = SpectrometerConnection()

    # switch testing mode toggle
    def testing_mode(self, testing: bool):
        self.testing = testing


    def run(self):
        while self.running:
            if self.testing:
                # get test data from file
                x_data = get_data_from_file(X_file_path)
                y_data = get_data_from_file(Y_file_path)
                y_data += np.random.choice([-200, 200], size=y_data.size)
            else:
                # get real data from spectrometer
                pass
                # x_data = np.linspace(0, 10, 1024)
                # y_data = np.sin(x_data) + np.random.normal(0, 0.1, 1024)

            self.new_data.emit(x_data, y_data)
            self.sleep(1)

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


class GraphApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.data_thread = DataThread()
        self.data_thread.new_data.connect(self.update_graph)
        self.data_thread.start()


    # in testing mode thread start generating unreal data
    def testing_mode(self, testing: bool):
        self.data_thread.testing_mode(testing)


    def init_ui(self):
        self.setWindowTitle("Real-time Graph")
        self.setGeometry(100, 100, 900, 500)
        self.setWindowIcon(QIcon("icon.png"))

        layout = QHBoxLayout()

        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("w")
        self.graph_widget.setLabel("left", "Y Values")
        self.graph_widget.setLabel("bottom", "X Values")
        self.curve = self.graph_widget.plot(pen="b")

        self.time_label = QLabel("Accumulation Time (s):")
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 300)
        self.time_input.setValue(10)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.time_label)
        control_layout.addWidget(self.time_input)
        control_layout.addStretch()

        layout.addWidget(self.graph_widget)
        layout.addLayout(control_layout)
        self.setLayout(layout)

    def update_graph(self, x_data, y_data):
        self.curve.setData(x_data, y_data)

    def closeEvent(self, event):
        self.data_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GraphApp()
    # set testing mode (use test data)
    window.testing_mode(True)
    window.show()
    sys.exit(app.exec_())
