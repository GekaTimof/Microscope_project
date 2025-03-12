import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal, QMutex
import pyqtgraph as pg
from PyQt5.QtGui import QIcon
# spectrometer connection class
from SpectrometerOptoskyConnection import SpectrometerConnection
# visual_testing function and links for test data
from SpectrometerOptoskyConnection.GetTestData import get_data_from_file
from SpectrometerOptoskyConnection.Constants import TEST_DATA_X_PATH, TEST_DATA_Y_PATH, MAX_INTEGRAL_TIME, START_INTEGRAL_TIME
# links to assets
from SpectrometerApplication.Constants import APP_ICON, MIN_GRAPHIC_Y_RANGE
# functions to save spectrum data
from SpectrometerApplication.SaveData import generate_spectrum_data_array, generate_spectrum_file_name, save_data_to_folder
# application text
from SpectrometerApplication import TextConstants as app_text



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


    # function to save spectrum data (X  Y) to chosen folder
    def save_spectrum_data_to_folder(self, folder):
        self.mutex.lock()
        # get wavelength_range
        x_data = self.connection.return_wavelength_range()
        # get real real_current_spectrum (current_spectrum - dark_spectrum)
        y_data = self.connection.return_real_current_spectrum()
        # generate array of text lines
        data = generate_spectrum_data_array(X=x_data, Y=y_data)
        # generate name for file for data
        file_name = generate_spectrum_file_name(prefix=self.connection.return_sub_parameter_text())

        # save data like file to folder (if we have data)
        if data is not None:
            save_data_to_folder(data, file_name, folder)
        else:
            print("Not enough data (X Y) to save it")
        self.mutex.unlock()


    # function to update data in thread
    def run(self):
        if self.testing:
            y_data_test = get_data_from_file(TEST_DATA_Y_PATH)
        while self.running:
            self.mutex.lock()
            if self.testing:
                # get test data from file
                x_data = get_data_from_file(TEST_DATA_X_PATH)
                y_data_test += np.random.choice([-10, 10], size=y_data_test.size)
                y_data = y_data_test
            else:
                # get real data from spectrometer
                # send command to updating current_spectrum (get ntw values from spectrometer)
                self.connection.retrieve_and_set_current_spectrum()
                # get wavelength_range
                x_data = self.connection.return_wavelength_range()
                # get real real_current_spectrum (current_spectrum - dark_spectrum)
                y_data = self.connection.return_real_current_spectrum()

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
        self.setWindowTitle(app_text.WINDOW_TITLE)
        self.setGeometry(100, 100, 900, 500)
        self.setWindowIcon(QIcon(APP_ICON))

        layout = QHBoxLayout()

        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("w")
        self.graph_widget.setLabel("left", app_text.LEFT_GRAPHIC_LABEL)
        self.graph_widget.setLabel("bottom", app_text.BOTTOM_GRAPHIC_LABEL)
        self.curve = self.graph_widget.plot(pen="b")
        self.graph_widget.setLimits(minYRange=MIN_GRAPHIC_Y_RANGE)

        # input field to set integral time
        self.time_label = QLabel(app_text.INPUT_INTEGRAL_TIME_LABEL)
        self.time_input = QSpinBox()
        self.time_input.setRange(1, MAX_INTEGRAL_TIME)
        self.time_input.setValue(START_INTEGRAL_TIME)
        self.time_input.setButtonSymbols(QSpinBox.NoButtons)

        # Connect the valueChanged signal to the update_integral_time slot
        self.time_input.valueChanged.connect(self.update_integral_time)

        # button to set dark spectrum
        self.set_dark_spectrum_button = QPushButton(app_text.SET_DARK_SPECTRUM_BUTTON)
        self.set_dark_spectrum_button.clicked.connect(self.data_thread.set_dark_spectrum)

        # button to clear dark spectrum
        self.clear_dark_spectrum_button = QPushButton(app_text.CLEAR_DARK_SPECTRUM_BUTTON)
        self.clear_dark_spectrum_button.clicked.connect(self.data_thread.clear_dark_spectrum)

        # input directory field
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(app_text.INPUT_DIRECTORY_LABEL)
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText(app_text.INPUT_PLACEHOLDER_TEXT)
        self.dir_button = QPushButton(app_text.INPUT_DIRECTORY_BUTTON)
        self.dir_button.clicked.connect(self.select_directory)

        # create directory input layout
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_button)

        # button to save spectrometer data
        self.save_button = QPushButton(app_text.SAVE_SPECTROMETER_DATA_BUTTON)
        self.save_button.clicked.connect(self.save_spectrum_data)

        # Button to reset graph zoom
        self.reset_zoom_button = QPushButton(app_text.RESET_ZOOM_BUTTON)
        self.reset_zoom_button.clicked.connect(self.reset_graph_view)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.time_label)
        control_layout.addWidget(self.time_input)
        control_layout.addWidget(self.set_dark_spectrum_button)
        control_layout.addWidget(self.clear_dark_spectrum_button)
        control_layout.addWidget(self.dir_label)
        control_layout.addLayout(dir_layout)
        control_layout.addWidget(self.save_button)
        control_layout.addWidget(self.reset_zoom_button)
        control_layout.addStretch()

        layout.addWidget(self.graph_widget,5)
        layout.addLayout(control_layout, 1)
        self.setLayout(layout)


    # function to directory selector
    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, app_text.SELECT_DIRECTORY_FILE_DIALOG)
        if directory:
            self.dir_input.setText(directory)


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
    def save_spectrum_data(self):
        directory = self.dir_input.text()
        if not directory:
            print("No directory selected!")
        else:
            self.data_thread.save_spectrum_data_to_folder(folder=directory)


    # function to reset graphic zoom
    def reset_graph_view(self):
        if self.curve is not None:
            data = self.curve.getData()
            if data is not None and len(data[0]) > 0:
                x_values, y_values = data
                min_x, max_x = min(x_values), max(x_values)
                min_y, max_y = min(y_values), max(y_values)

                self.graph_widget.setXRange(min_x, max_x)
                self.graph_widget.setYRange(min_y, max_y)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    # start in normal mode
    window = GraphApp()
    window.show()
    sys.exit(app.exec_())
