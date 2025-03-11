import os
import datetime
import numpy as np


# generate array with X and Y (for saving text data)
def generate_spectrum_data_array(X: np.array, Y: np.array):
    if X.size == Y.size:
        pass


# create name for file with data from spectrometer
def create_spectrum_data_name(prefix: str = ""):
    name = prefix + str(datetime.datetime.now())
    return name


# save file with data to selected folder (if folder exist)
def save_data_to_folder(data, file_name: str, folder):
    if os.path.isdir(folder):
        path_to_file = os.path.join(folder, file_name)
        with open(path_to_file, "w") as file:
            file.writelines(i for i in data)
    else:
        raise Exception(f"{folder} is not a directory")

