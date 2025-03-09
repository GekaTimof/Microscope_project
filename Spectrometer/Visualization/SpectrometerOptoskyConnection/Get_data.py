import os.path
import numpy as np
from Constants import Test_wavelength_len

def get_data_from_file(file_name: str):
    data = np.zeros(Test_wavelength_len)
    if os.path.exists(file_name):
        file = open(file_name)
        for i, line in enumerate(file):
            data[i] = line.split()[-1]
            # print(data[i])
    return data

# def get_data_from_massage(massage: str):
#     data = np.zeros(lines_num)
#     i = 0
#     for line in massage:
#         if line:
#             data[i] = line.split()[-1]
#             i += 1
#     return data

