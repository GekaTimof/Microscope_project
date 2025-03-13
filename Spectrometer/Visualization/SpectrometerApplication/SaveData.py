import os
import datetime
import getpass
import pwd
import numpy as np


# generate array with X and Y (for saving text data)
def generate_spectrum_data_array(X: np.array, Y: np.array):
    if X.size == Y.size:
        text_array = []
        for i, elem in enumerate(X):
            text_array.append(f"{X[i]}  {Y[i]}\n")
        return text_array
    else:
        return None


# generate name for file with data from spectrometer
def generate_spectrum_file_name(prefix: str = ""):
    name = prefix + str(datetime.datetime.now())
    return name


# save file with data to selected folder (if folder exist)
def save_data_to_folder(data, file_name: str, folder):
    if os.path.isdir(folder):
        path_to_file = os.path.join(folder, file_name)

        # get name of user in whose directory the program is located
        script_dir = os.path.dirname(os.path.realpath(__file__))
        dir_stat = os.stat(script_dir)
        user_info = pwd.getpwuid(dir_stat.st_uid)
        user_name = user_info.pw_name

        try:
            # get info about user
            user_info = pwd.getpwnam(user_name)
            uid, gid = user_info.pw_uid, user_info.pw_gid
            # create file
            with open(path_to_file, "w") as file:
                pass
            # switch file owner fore user
            os.chown(path_to_file, uid, gid)

            # save data
            with open(path_to_file, "w") as file:
                file.writelines(i for i in data)
        except KeyError:
            print(f"⚠ Error: The user could not be found {user_name}")
    else:
        raise Exception(f"{folder} is not a directory")

