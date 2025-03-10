import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal
import pyqtgraph as pg
from PyQt5.QtGui import QIcon
# spectrometer connection class
from SpectrometerOptoskyConnection import SpectrometerConnection
# visual_testing function and links for test data
from SpectrometerOptoskyConnection import get_data_from_file
from SpectrometerOptoskyConnection import X_file_path, Y_file_path
# links to assets
from SpectrometerApplication import APP_ICON

# Thread to connect and get data from spectrometer
class DataThread(QThread):
    new_data = pyqtSignal(np.ndarray, np.ndarray)
    # thread initialization
    def __init__(self, testing: bool = False):
        super().__init__()
        self.testing = testing
        self.running = True
        # start connection to spectrometer
        if not (testing):
            self.connection = SpectrometerConnection()
            self.connection.open_spectrometer()

    #
    # # switch testing mode toggle
    # def testing_mode(self, testing: bool):
    #     self.testing = testing


    # function to set new dark spectrum
    def set_dark_spectrum(self):
        self.connection.retrieve_and_set_dark_spectrum()


    # function to set new dark spectrum
    def set_integral_time(self, new_integral_time: int):

        self.connection.set_integral_time(new_integral_time=new_integral_time)


    # function to update data in thread
    def run(self):
        while self.running:
            if self.testing:
                # get test data from file
                x_data = get_data_from_file(X_file_path)
                y_data = get_data_from_file(Y_file_path)
                y_data += np.random.choice([-200, 200], size=y_data.size)
            else:
                # get real data from spectrometer
                # send command to updating current_spectrum (get ntw values from spectrometer)
                self.connection.get_current_spectrum()
                # set wavelength_range
                x_data = self.connection.return_wavelength_range()
                # set real real_current_spectrum (current_spectrum - dark_spectrum)
                y_data = self.connection.return_real_current_spectrum()

            self.new_data.emit(x_data, y_data)
            self.sleep(1)


    # function to stop thread
    def stop(self):
        self.running = False
        self.quit()
        self.wait()



# Interface for spectrometer application
class GraphApp(QWidget):
    def __init__(self, testing: bool = False):
        super().__init__()
        self.data_thread = DataThread(testing=testing)
        self.init_ui()
        self.data_thread.new_data.connect(self.update_graph)
        self.data_thread.start()

    #
    # # in testing mode thread start generating unreal data
    # def testing_mode(self, testing: bool):
    #     self.data_thread.testing_mode(testing)


    def init_ui(self):
        self.setWindowTitle("Real-time Graph")
        self.setGeometry(100, 100, 900, 500)
        self.setWindowIcon(QIcon(APP_ICON))

        layout = QHBoxLayout()

        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("w")
        self.graph_widget.setLabel("left", "Y Values")
        self.graph_widget.setLabel("bottom", "X Values")
        self.curve = self.graph_widget.plot(pen="b")

        # input field to set integral time
        self.time_label = QLabel("Integral Time (s):")
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 300)
        self.time_input.setValue(10)
        self.time_input.setButtonSymbols(QSpinBox.NoButtons)
        self.time_input.editingFinished.connect(self.update_integral_time)

        # button to set dark spectrum
        self.dark_spectrum_button = QPushButton("Set Dark Spectrum")
        self.dark_spectrum_button.clicked.connect(self.data_thread.set_dark_spectrum)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.time_label)
        control_layout.addWidget(self.time_input)
        control_layout.addWidget(self.dark_spectrum_button)
        control_layout.addStretch()

        layout.addWidget(self.graph_widget)
        layout.addLayout(control_layout)
        self.setLayout(layout)


    # function to update integral time
    def update_integral_time(self, value):
        self.data_thread.set_integral_time(value)


    # function to set X and Y to graph
    def update_graph(self, x_data, y_data):
        self.curve.setData(x_data, y_data)


    # function to stap thread (spectrometer connection)
    def closeEvent(self, event):
        self.data_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # set testing mode (use test data)
    window = GraphApp(testing=True)
    window.show()
    sys.exit(app.exec_())
