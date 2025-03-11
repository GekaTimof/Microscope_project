import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
import pyqtgraph as pg
from PyQt5.QtGui import QIcon
# spectrometer connection class
from SpectrometerOptoskyConnection import SpectrometerConnection, START_INTEGRAL_TIME
# visual_testing function and links for test data
from SpectrometerOptoskyConnection import get_data_from_file
from SpectrometerOptoskyConnection import TEST_DATA_X_PATH, TEST_DATA_Y_PATH
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
        self.mutex = QMutex()
        # start connection to spectrometer
        if not (testing):
            self.connection = SpectrometerConnection()
            self.connection.open_spectrometer()
            self.connection.retrieve_and_set_wavelength_range()


    # function to set new dark spectrum
    def set_dark_spectrum(self):
        self.mutex.lock()
        self.connection.retrieve_and_set_dark_spectrum()
        self.mutex.unlock()


    # function to clear dark spectrum
    def clear_dark_spectrum(self):
        self.mutex.lock()
        self.connection.clear_dark_spectrum()
        self.mutex.unlock()


    # function to set new dark spectrum
    def set_integral_time(self, new_integral_time: int):
        self.mutex.lock()
        self.connection.set_integral_time(new_integral_time)
        self.mutex.unlock()


    # function to update data in thread
    def run(self):
        while self.running:
            self.mutex.lock()
            if self.testing:
                # get test data from file
                x_data = get_data_from_file(TEST_DATA_X_PATH)
                y_data = get_data_from_file(TEST_DATA_Y_PATH)
                y_data += np.random.choice([-200, 200], size=y_data.size)
            else:
                # get real data from spectrometer
                # send command to updating current_spectrum (get ntw values from spectrometer)
                self.connection.retrieve_and_set_current_spectrum()
                # set wavelength_range
                x_data = self.connection.return_wavelength_range()
                print(x_data)
                # set real real_current_spectrum (current_spectrum - dark_spectrum)
                y_data = self.connection.return_real_current_spectrum()
                print(y_data)

            self.new_data.emit(x_data, y_data)
            self.mutex.unlock()
            self.msleep(10)


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
        self.time_label = QLabel("Integral Time (ms):")
        self.time_input = QSpinBox()
        self.time_input.setRange(1, 9999)
        self.time_input.setValue(START_INTEGRAL_TIME)
        self.time_input.setButtonSymbols(QSpinBox.NoButtons)

        # Connect the valueChanged signal to the update_integral_time slot
        self.time_input.valueChanged.connect(self.update_integral_time)

        # button to set dark spectrum
        self.set_dark_spectrum_button = QPushButton("Set Dark Spectrum")
        self.set_dark_spectrum_button.clicked.connect(self.data_thread.set_dark_spectrum)

        # button to clear dark spectrum
        self.clear_dark_spectrum_button = QPushButton("Clear Dark Spectrum")
        self.clear_dark_spectrum_button.clicked.connect(self.data_thread.clear_dark_spectrum)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.time_label)
        control_layout.addWidget(self.time_input)
        control_layout.addWidget(self.set_dark_spectrum_button)
        control_layout.addWidget(self.clear_dark_spectrum_button)
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
    def close_event(self, event):
        self.data_thread.stop()
        event.accept()


    # function to save file with data to selected folder
    def save_data(self):
        # TODO create save_data function
        pass



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # start in normal mode
    window = GraphApp()
    window.show()
    sys.exit(app.exec_())
