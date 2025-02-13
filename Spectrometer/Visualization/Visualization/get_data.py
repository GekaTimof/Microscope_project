import os.path
import numpy as np

from numpy.ma.core import array
from pyqtgraph.examples.GraphItem import lines

file_pass = "../test_data/Y_data.txt"
# количество строк в файле
lines_num = 1024

def get_data_from_file(file_name: str):
    data = np.zeros(lines_num)
    if os.path.exists(file_name):
        file = open(file_name)
        for i, line in enumerate(file):
            data[i] = line.split()[-1]
            # print(data[i])
    return data

# data = get_data_from_file(file_pass)
# print(data)