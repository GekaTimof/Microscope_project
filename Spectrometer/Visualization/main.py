# Side imports
import os
import sys
import pwd
import time
import numpy as np
from PyQt5.QtWidgets import QComboBox, QProgressBar, QApplication, QWidget, QFileDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QSpinBox, QLabel, \
    QPushButton, QShortcut, QMessageBox, QGraphicsProxyWidget
from PyQt5.QtCore import QProcess, QThread, pyqtSignal, QMutex
import pyqtgraph as pg
from PyQt5.QtGui import QIcon, QKeySequence, QFont

# Spectrometer connection class
from SpectrometerOptoskyConnection import SpectrometerConnection
# Spectrometer params (constants)
from SpectrometerOptoskyConnection.Constants import MAX_INTEGRAL_TIME, START_INTEGRAL_TIME
# Links to assets
from SpectrometerApplication.Constants import BASE_LANGUAGE, DARK_THEME_STYLE, DARK_THEME, APP_ICON, MIN_GRAPHIC_Y_RANGE, FONT, FONT_SIZE, WARNING_FONT_SIZE, COORDINATES_FONT_SIZE
# Functions to save spectrum data
from SpectrometerApplication.SaveData import generate_spectrum_data_array, generate_spectrum_file_name, save_data_to_folder
# Application text
from SpectrometerApplication import TextConstants as app_text
# Base directory to save spectrum datas
from SpectrometerOptoskyConnection.Constants import BASE_SAVE_SPECTRUM_DIR
# (only for testing mode) Links for test data and visual_testing function
from SpectrometerOptoskyConnection.GetTestData import get_data_from_file
from SpectrometerOptoskyConnection.Constants import TEST_DATA_X_PATH, TEST_DATA_Y_PATH


#------------------------------------------------- Spectrometer thread -------------------------------------------------

# Thread to connect and get data from spectrometer
class DataThread(QThread):
    new_data = pyqtSignal(np.ndarray, np.ndarray)
    # thread initialization
    def __init__(self, testing: bool = False):
        super().__init__()
        self.testing = testing
        self.running = True
        self.mutex = QMutex()
        self.overillumination = False

        # start connection to spectrometer
        if not (self.testing):
            self.connection = SpectrometerConnection()
            self.connection.open_spectrometer()
            self.connection.retrieve_and_set_wavelength_range()


    # method to set new dark spectrum
    def set_dark_spectrum(self):
        self.mutex.lock()
        self.connection.retrieve_and_set_dark_spectrum()
        self.mutex.unlock()


    # method to clear dark spectrum
    def clear_dark_spectrum(self):
        self.mutex.lock()
        self.connection.clear_dark_spectrum()
        self.mutex.unlock()


    # method to set new dark spectrum
    def set_integral_time(self, new_integral_time: int):
        self.mutex.lock()
        self.connection.set_integral_time(new_integral_time)
        self.mutex.unlock()


    # method to save spectrum data (X  Y) to chosen folder
    def save_spectrum_data_to_folder(self, folder):
        self.mutex.lock()
        try:
            # get wavelength_range
            x_data = self.connection.return_wavelength_range()
            # get real real_current_spectrum (current_spectrum - dark_spectrum)
            y_data = self.connection.return_real_current_spectrum()
            # get information about session and spectrometer
            session_info = self.connection.return_session_info()

            # generate array of text lines
            data = session_info + generate_spectrum_data_array(X=x_data, Y=y_data)
            # generate name for file for data
            file_name = generate_spectrum_file_name(prefix=self.connection.return_sub_parameter_text())

            # save data like file to folder (if we have data)
            if data is not None:
                save_data_to_folder(data, file_name, folder)
            # else:
            #     print("Not enough data (X Y) to save it")
            self.mutex.unlock()

            return True
        except:
            self.mutex.unlock()
            return False


    # method to update data in thread
    def run(self):
        # get test y data (in testing mode)
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
                # send command to updating current_spectrum (get new values from spectrometer)
                self.connection.retrieve_and_set_current_spectrum()
                # get wavelength_range
                x_data = self.connection.return_wavelength_range()
                # get real real_current_spectrum (current_spectrum - dark_spectrum)
                y_data = self.connection.return_real_current_spectrum()

                # check overillumination
                self.connection.check_overillumination()
                self.overillumination = self.connection.return_overillumination()

            self.new_data.emit(x_data, y_data)
            self.mutex.unlock()
            self.msleep(1)


    # method to stop thread
    def stop(self):
        self.running = False
        self.quit()
        self.wait()


#------------------------------------------------- Application thread --------------------------------------------------

# Interface for spectrometer application
class GraphApp(QWidget):
    def __init__(self, testing: bool = False):
        super().__init__()
        self.data_thread = DataThread(testing=testing)
        self.init_ui()
        self.loaded_spectra = {}
        self.data_thread.new_data.connect(self.update_graph)
        self.data_thread.start()

    # method to set application UI
    def init_ui(self):
        # Application base language
        if BASE_LANGUAGE in app_text.APPLICATION_LANGUAGES:
            self.language = BASE_LANGUAGE
        else:
            self.language = app_text.APPLICATION_LANGUAGES[0]

        # Main Window
        self.setWindowTitle(app_text.WINDOW_TITLE[self.language])
        self.setGeometry(100, 100, 1200, 600)
        self.setWindowIcon(QIcon(APP_ICON))

        layout = QHBoxLayout()

        # Widget with graph
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground("w")
        self.graph_widget.showGrid(x=True, y=True, alpha=0.75)
        self.graph_widget.setLabel("left", app_text.LEFT_GRAPHIC_LABEL[self.language])
        self.graph_widget.setLabel("bottom", app_text.BOTTOM_GRAPHIC_LABEL[self.language])
        self.curve = self.graph_widget.plot(pen="b")
        self.graph_widget.setLimits(minYRange=MIN_GRAPHIC_Y_RANGE)

        # Label for overillumination (will appear over graph)
        self.overillumination_label = pg.TextItem(app_text.OVERILLUMINATION_WARNING_TEXT[self.language], color='r', anchor=(0.5, 0))
        self.overillumination_label.setFont(QFont(FONT, WARNING_FONT_SIZE))
        self.overillumination_label.setZValue(2)
        self.overillumination_label.hide()
        self.graph_widget.addItem(self.overillumination_label)

        # Label for mouse coordinates
        self.coord_label = pg.TextItem("", anchor=(0, 1), color='k')
        self.coord_label.setFont(QFont(FONT, COORDINATES_FONT_SIZE))
        self.graph_widget.addItem(self.coord_label)
        self.coord_label.hide()

        # connect mouse to action (get coordinates)
        self.graph_widget.scene().sigMouseMoved.connect(self.on_mouse_move)

        # Field (input) to set integral time
        self.time_label = QLabel(app_text.INPUT_INTEGRAL_TIME_LABEL[self.language])
        self.time_input = QSpinBox()
        self.time_input.setRange(1, MAX_INTEGRAL_TIME)
        self.time_input.setValue(START_INTEGRAL_TIME)
        self.time_input.setButtonSymbols(QSpinBox.NoButtons)

        # Connect the valueChanged signal to the update_integral_time slot
        self.time_input.valueChanged.connect(self.update_integral_time)

        # Button to set dark spectrum
        self.set_dark_spectrum_button = QPushButton(app_text.SET_DARK_SPECTRUM_BUTTON[self.language])
        self.set_dark_spectrum_button.clicked.connect(self.data_thread.set_dark_spectrum)

        # Button to clear dark spectrum
        self.clear_dark_spectrum_button = QPushButton(app_text.CLEAR_DARK_SPECTRUM_BUTTON[self.language])
        self.clear_dark_spectrum_button.clicked.connect(self.data_thread.clear_dark_spectrum)

        # Field to input directory
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(app_text.INPUT_DIRECTORY_LABEL[self.language])
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText(app_text.INPUT_PLACEHOLDER_TEXT[self.language])
        self.dir_input.setReadOnly(True)
        self.dir_button = QPushButton(app_text.INPUT_DIRECTORY_BUTTON[self.language])
        self.dir_button.clicked.connect(self.select_directory)

        # create directory input layout
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_button)
        # check if user set base dir in constants
        if os.path.isdir(BASE_SAVE_SPECTRUM_DIR):
            self.dir_input.setText(BASE_SAVE_SPECTRUM_DIR)

        # Button to save spectrum data
        self.save_button = QPushButton(app_text.SAVE_SPECTROMETER_DATA_BUTTON[self.language])
        self.save_button.clicked.connect(self.save_spectrum_data)
        # set key combination to save spectrum data
        shortcut_save_spectrum_data = QShortcut(QKeySequence("Ctrl+S"), self)
        shortcut_save_spectrum_data.activated.connect(self.save_spectrum_data)

        # Progress bar for data sawing
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        # Button to reset graph zoom
        self.reset_zoom_button = QPushButton(app_text.RESET_ZOOM_BUTTON[self.language])
        self.reset_zoom_button.clicked.connect(self.reset_graph_view)
        # set key combination to reset graph zoom
        shortcut_reset_zoom = QShortcut(QKeySequence("Ctrl+R"), self)
        shortcut_reset_zoom.activated.connect(self.reset_graph_view)

        # Button to switch theme (Light and Dark)
        self.theme_button = QPushButton(app_text.SWITCH_TO_DARK_THEME_BUTTON[self.language])
        self.theme_button.setCheckable(True)
        self.theme_button.toggled.connect(self.toggle_theme)
        # chek if user set Dark theme like base theme
        if DARK_THEME:
            self.theme_button.toggle()

        # Language selector
        self.language_label = QLabel(app_text.LANGUAGE_SELECTOR[self.language])
        self.language_combo = QComboBox()
        self.language_combo.addItems(app_text.APPLICATION_LANGUAGES)
        self.language_combo.setCurrentText(self.language)
        self.language_combo.currentTextChanged.connect(self.change_language)
        language_layout = QHBoxLayout()
        language_layout.addWidget(self.language_label, 3)
        language_layout.addWidget(self.language_combo, 2)

        # Field for load spectra
        self.loaded_spectrum_button = QPushButton(app_text.SPECTRUM_LOAD_BUTTON[self.language])
        self.load_spectrum_button.clicked.connect(self.load_spectrum_file)

        # Control layout creation (total layout)
        control_layout = QVBoxLayout()
        control_layout.addLayout(language_layout)
        control_layout.addWidget(self.theme_button)
        control_layout.addWidget(self.reset_zoom_button)
        control_layout.addWidget(self.time_label)
        control_layout.addWidget(self.time_input)
        control_layout.addWidget(self.set_dark_spectrum_button)
        control_layout.addWidget(self.clear_dark_spectrum_button)
        control_layout.addWidget(self.dir_label)
        control_layout.addLayout(dir_layout)
        control_layout.addWidget(self.save_button)
        control_layout.addWidget(self.progress_bar)
        control_layout.addWidget(self.load_spectrum_button)
        control_layout.addStretch()

        layout.addWidget(self.graph_widget,4)
        layout.addLayout(control_layout, 1)
        self.setLayout(layout)


    # method to directory selector
    def select_directory(self):
        # get home directory of user in whose directory the program is located
        script_dir = os.path.dirname(os.path.realpath(__file__))
        dir_stat = os.stat(script_dir)
        user_info = pwd.getpwuid(dir_stat.st_uid)
        home_dir = user_info.pw_dir

        options = QFileDialog.Option.DontUseNativeDialog
        options |= QFileDialog.Option.ReadOnly

        # if user already select directory we will set it to selection field, if not select, we will set home directory
        current_directory = self.dir_input.text() if os.path.isdir(self.dir_input.text()) else home_dir

        directory = QFileDialog.getExistingDirectory(self, app_text.INPUT_DIRECTORY_WINDOW_NAME[self.language],
                                                     current_directory, options)
        if directory:
            # check that user try to select folder in home directory
            if not directory.startswith(home_dir):
                QMessageBox.warning(self, app_text.WARNING_SELECT_OUT_OF_HOME[self.language])
                return

            self.dir_input.setText(directory)


    # method to update integral time
    def update_integral_time(self, value):
        self.data_thread.set_integral_time(value)


    # method to set X and Y to graph
    def update_graph(self, x_data, y_data):
        self.curve.setData(x_data, y_data)

        if self.data_thread.overillumination:
            # set warning positon
            x_center = np.mean(x_data)
            y_center = (np.min(y_data) + np.max(y_data)) / 2
            self.overillumination_label.setPos(x_center, y_center)
            # show warning
            self.overillumination_label.show()
        else:
            # hide warning
            self.overillumination_label.hide()


    # method to stap thread (spectrometer connection)
    def close_event(self, event):
        self.data_thread.stop()
        event.accept()


    # method to save file with data to selected folder
    def save_spectrum_data(self):
        try:
            directory = self.dir_input.text()
        except:
            QMessageBox.warning(self, app_text.WARNING_NO_DIRECTORY_SELECTED[self.language])
            return

        # get home directory of user in whose directory the program is located
        script_dir = os.path.dirname(os.path.realpath(__file__))
        dir_stat = os.stat(script_dir)
        user_info = pwd.getpwuid(dir_stat.st_uid)
        home_dir = user_info.pw_dir

        # check that use try to save data to home directory
        if not directory.startswith(home_dir):
            QMessageBox.warning(self, app_text.WARNING_SAWING_OUT_OF_HOME[self.language])
            return

        # Show progress bar and simulate progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        QApplication.processEvents()

        for i in range(1, 6):
            time.sleep(0.1)
            self.progress_bar.setValue(i * 20)
            QApplication.processEvents()

        success = self.data_thread.save_spectrum_data_to_folder(folder=directory)
        self.progress_bar.setVisible(False)

        if not success:
            QMessageBox.critical(self, "Error", app_text.CRITICAL_SAVING_FAILED[self.language])

    # method to reset graphic zoom
    def reset_graph_view(self):
        if self.curve is not None:
            data = self.curve.getData()
            if data is not None and len(data[0]) > 0:
                x_values, y_values = data
                min_x, max_x = min(x_values), max(x_values)
                min_y, max_y = min(y_values), max(y_values)

                self.graph_widget.setXRange(min_x, max_x)
                self.graph_widget.setYRange(min_y, max_y)


    # method to get mouse coordinates when it on the graph
    def on_mouse_move(self, pos):
        vb = self.graph_widget.getViewBox()
        if vb.sceneBoundingRect().contains(pos):
            mouse_point = vb.mapSceneToView(pos)
            x, y = mouse_point.x(), mouse_point.y()

            view_rect = vb.viewRect()
            margin_x = (view_rect.right() - view_rect.left()) * 0.03
            margin_y = (view_rect.bottom() - view_rect.top()) * 0.04

            if (view_rect.left() + margin_x <= x <= view_rect.right() - margin_x and
                view_rect.top() + margin_y <= y <= view_rect.bottom() - margin_y):

                text = f"x={int(x)} y={int(y)}"
                self.coord_label.setText(text)
                self.coord_label.setPos(x, y)
                self.coord_label.show()
            else:
                self.coord_label.hide()
        else:
            self.coord_label.hide()


    # method to switch theme (Light and Dark)
    def toggle_theme(self, checked):
        if checked:
            self.set_dark_theme()
            self.theme_button.setText(app_text.SWITCH_TO_LIGHT_THEME_BUTTON[self.language])
        else:
            self.set_light_theme()
            self.theme_button.setText(app_text.SWITCH_TO_DARK_THEME_BUTTON[self.language])


    # method to set dark application theme
    def set_dark_theme(self):
        dark_style = DARK_THEME_STYLE
        self.coord_label.setColor("w")
        self.setStyleSheet(dark_style)
        self.graph_widget.setBackground('k')
        self.curve.setPen('y')


    # method to set light application theme
    def set_light_theme(self):
        self.coord_label.setColor("black")
        self.setStyleSheet("")
        self.graph_widget.setBackground('w')
        self.curve.setPen('b')


    # method to change application language
    def change_language(self, selected_language):
        if selected_language != self.language:
            self.update_base_language_constant(selected_language)
            self.restart_application()


    # method to change base language constant (BASE_LANGUAGE)
    def update_base_language_constant(self, new_language):
        constants_path = os.path.join(os.path.dirname(__file__), "SpectrometerApplication" ,"Constants.py")
        with open(constants_path, "r") as file:
            lines = file.readlines()

        with open(constants_path, "w") as file:
            for line in lines:
                if line.startswith("BASE_LANGUAGE"):
                    file.write(f'BASE_LANGUAGE = "{new_language}"\n')
                else:
                    file.write(line)


    # method to restart all application
    def restart_application(self):
        QApplication.quit()
        QProcess.startDetached(sys.executable, sys.argv)


    # method to load saved spectrum to diagram
    def load_spectrum_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select spectrum files", "", "Text Files (*.txt *.csv)")
        for file_path in files:
            if file_path not in self.loaded_spectra:
                x_data, y_data = self.read_spectrum_from_file(file_path)
                color = pg.intColor(len(self.loaded_spectra))  # уникальный цвет
                curve = self.graph_widget.plot(x_data, y_data, pen=color, name=os.path.basename(file_path))
                self.loaded_spectra[file_path] = curve


#-------------------------------------------------- Application start --------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # set font settings
    app.setFont(QFont(FONT, FONT_SIZE))
    # start in normal mode
    window = GraphApp(testing=True)
    window.show()
    sys.exit(app.exec_())
