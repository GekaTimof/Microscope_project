import os

#------------------------------------------------------ User Zone ------------------------------------------------------


#---------------------------------------------------- NOT User Zone ----------------------------------------------------

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
    Command_open_spectrometer: ("0", ["Open spectrometer success!", "Enter :"]),
    Command_get_wavelength_range: ("23", ["Wavelength", "=====", "Enter :"]),
    Command_get_dark_spectrum: ("30", ["input", "Count", "=====", "Enter :"]),
    Command_get_current_spectrum: ("31", ["input", "Count", "=====", "Enter :"]),
}

# Spectrometer params
WAVELENGTH_RANGE_LEN = 1024
SPECTRUM_LEN = WAVELENGTH_RANGE_LEN
OVERILLUMINATION_THRESHOLD = 65535
START_INTEGRAL_TIME = 10
MAX_INTEGRAL_TIME = 99999

# Params for request to spectrometer
WAITING_TIME_MULTIPLIER = 2
MINIMUM_WAITING_TIME = 5
