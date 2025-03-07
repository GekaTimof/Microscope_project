# Path to files with test data
X_file_path = "../test_data/X_data.txt"
Y_file_path = "../test_data/Y_data.txt"

# Paths to Optosky API script
Spectrometer_directory_path = "Get_data"
Spectrometer_name = "OptoskyDemo"

# Spectrometer params (will be automated)
X_len = 2048
Y_len = 1044
Accumulation_time = 10

# Parameters for spectrometer simulating with test data
Fake_spreading_range = 300
lines_num = 1024

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
    Command_get_dark_spectrum: ("30", [""]),
    Command_get_current_spectrum: ("31", ["time(ms) :", "Enter :"]),
}

