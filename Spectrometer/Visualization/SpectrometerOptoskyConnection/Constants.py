import os

# Path to base directory
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to spectrometer base dir
Spectrometer_directory_name = "Get_data"
Spectrometer_name = "OptoskyDemo"
SPECTROMETER_DIR = os.path.join(CURRENT_DIR, "..", "..", Spectrometer_directory_name)
SPECTROMETER_FILE = os.path.join(SPECTROMETER_DIR, Spectrometer_name)

# Path to files with test data
Test_data_directory_name = "TestData"
Test_data_X_name = "X_data.txt"
Test_data_Y_name = "Y_data.txt" 
TEST_DATA_X_PATH = os.path.join(CURRENT_DIR, "..", Test_data_directory_name, Test_data_X_name)
TEST_DATA_Y_PATH = os.path.join(CURRENT_DIR, "..", Test_data_directory_name, Test_data_Y_name)

# Parameters for spectrometer simulating with test data
Test_wavelength_len = 1024

# Optosky spectrometer commands
Command_open_spectrometer = "open_spectrometer"
Command_get_wavelength_range = "get_wavelength_range"
Command_get_dark_spectrum = "get_dark_spectrum"
Command_get_current_spectrum = "get_current_spectrum"

# dict of all Optosky spectrometer commands
# key - name of command,
# val[0] - command id,
# val[1] - contain array or key phrases to extract values from request
OptoskySpectrometerCommands = {
    Command_open_spectrometer: ("0", ["Open spectrometer success", "Enter :"]),
    Command_get_wavelength_range: ("23", ["Pixel  Wavelength", "=====", "Enter :"]),
    Command_get_dark_spectrum: ("30", ["time(ms) :", "=====", "Enter :"]),
    Command_get_current_spectrum: ("31", ["time(ms) :", "=====", "Enter :"]),
}


# Spectrometer params (will be automated)
Wavelength_range_len = 1024
Spectrum_len = 1024 
Integral_time = 10
