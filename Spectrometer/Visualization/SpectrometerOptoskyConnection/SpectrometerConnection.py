import os
import pexpect
import numpy as np

from SpectrometerOptoskyConnection import SPECTROMETER_DIR, SPECTROMETER_FILE, START_INTEGRAL_TIME, WAVELENGTH_RANGE_LEN, SPECTRUM_LEN
from SpectrometerOptoskyConnection import OptoskySpectrometerCommands, Command_open_spectrometer, Command_get_wavelength_range, Command_get_dark_spectrum, Command_get_current_spectrum

# class that contain spectrometer connection
class SpectrometerConnection:
    def __init__(self):
        # set dict os spectrometer commands
        # {"key": ("id", [key_text_1, key_text_2, ...])}
        self.Commands = OptoskySpectrometerCommands

        # set spectrometer commands
        self.Open_spectrometer = Command_open_spectrometer
        self.Get_wavelength_range = Command_get_wavelength_range
        self.Get_dark_spectrum = Command_get_dark_spectrum
        self.Get_current_spectrum = Command_get_current_spectrum

        # set start accumulation time
        self.integral_time: int = START_INTEGRAL_TIME

        # set wavelength len and empty wavelength array
        self.wavelength_range_len: int = WAVELENGTH_RANGE_LEN
        self.wavelength_range = np.zeros(self.wavelength_range_len)

        # set spectrum len and empty spectrum array
        self.spectrum_len: int = SPECTRUM_LEN
        self.dark_spectrum = np.zeros(self.spectrum_len)
        self.current_spectrum = np.zeros(self.spectrum_len)
        self.real_current_spectrum = np.zeros(self.spectrum_len)

        # set sub parameter (True - is we set dark spectrum, False - is we don't set dark spectrum )
        self.sub = False

        # set working directory
        self.working_directory = SPECTROMETER_DIR
        if not os.path.exists(self.working_directory):
            raise FileNotFoundError(f"Spectrometer directory not found: {self.working_directory}")

        # set path to spectrometer script
        self.spectrometer_path = SPECTROMETER_FILE
        if not os.path.isfile(self.spectrometer_path):
            raise FileNotFoundError(f"Spectrometer script not found: {self.spectrometer_path}")

        # set spectrometer connection proses
        self.process = pexpect.spawn(f'{self.spectrometer_path}', cwd=self.working_directory, encoding="utf-8", timeout=10)


    # function return spectrometer working_directory
    def get_working_directory(self):
        return self.working_directory


    # function return spectrometer accumulation time
    def get_integral_time(self):
        return self.integral_time


    # function set spectrometer accumulation time
    def set_integral_time(self, new_integral_time: int):
        if new_integral_time > 0:
            self.integral_time = new_integral_time
        else:
            raise Exception(f"an able to set integral_time = {new_integral_time}")
            # TODO add correct Exception


    # function send one command to spectrometer
    def send_command(self, command: str):
        self.process.sendline(command)
        print(f"command - '{command}' has been sent")
        return self


    # function trying to find expect_answer in spectrometer text flow
    def wait_for_response(self,  expect_answer: str, waiting_time: int = 5):
        try:
            # wait for answer
            self.process.expect(expect_answer, timeout=waiting_time)
            print(f"answer - '{expect_answer}' was received")
        except:
            raise Exception(f"No answer '{expect_answer}' from spectrometer")
            # TODO add correct Exception


    # function trying to find expect_answer in spectrometer text flow and return all test before it
    def read_until_response(self,  expect_answer: str, waiting_time: int = 5):
        # wait for answer
        self.wait_for_response(expect_answer, waiting_time=waiting_time)

        # get response
        response = self.process.before
        return response


    # function to connect to spectrometer
    def open_spectrometer(self):
        # get command parameters
        command_id = self.Commands[self.Open_spectrometer][0]
        expected_answers = self.Commands[self.Open_spectrometer][1]

        # try to connect
        self.send_command(command_id)
        # checking connection
        self.wait_for_response(expected_answers[0])
        # skip before next request
        self.wait_for_response(expected_answers[1])
        return self


    # function to split text data for len lince and convert to np array
    def split_spectrometer_response(self, response: str, data_len: int):
        lines = response.split('\n')
        # List to store extracted data
        data = []

        # try to convert text to float
        for line in lines:
            # Ignore empty lines or lines without tab
            if line.strip() and "\t" in line:
                # Try to extract the second number
                try:
                    # Extract number after tab
                    value = float(line.split("\t")[1].strip())
                    data.append(value)
                except ValueError:
                    pass  # Skip lines that don't have a valid number

        # Convert list to numpy array
        data = np.array(data, dtype=np.float32)


        # check array total len
        if len(data) != data_len:
            return None
        return data


    # function to retrieve and set wavelength range
    def retrieve_and_set_wavelength_range(self):
        # get command parameters
        command_id = self.Commands[self.Get_wavelength_range][0]
        expected_answers = self.Commands[self.Get_wavelength_range][1]

        # send command
        self.send_command(command_id)

        # checking that the wavelength range has been received
        self.wait_for_response(expected_answers[0])
        # get data from response
        response = self.read_until_response(expected_answers[1])
        data = self.split_spectrometer_response(response, self.wavelength_range_len)
        # set wavelength range if we got it
        if data is not None:
            self.wavelength_range = data

        # skip before next request
        self.wait_for_response(expected_answers[2])
        return self


    # function to retrieve and set dark spectrum
    def retrieve_and_set_dark_spectrum(self):
        # get command parameters
        command_id = self.Commands[self.Get_dark_spectrum][0]
        expected_answers = self.Commands[self.Get_dark_spectrum][1]

        # send command
        self.send_command(command_id)

        # wait for integral time request
        self.wait_for_response(expected_answers[0])
        # send integral time
        self.send_command(str(self.integral_time))

        # checking that the integral time has been set and data has been received
        self.wait_for_response(expected_answers[1])
        # get data from response
        response = self.read_until_response(expected_answers[2])
        data = self.split_spectrometer_response(response, self.spectrum_len)
        # set dark spectrum if we got
        if data is not None:
            self.dark_spectrum = data
            self.sub = True
            # set new real current spectrum
            self.real_current_spectrum = self.current_spectrum - self.dark_spectrum

        # skip before next request
        self.wait_for_response(expected_answers[3])
        return self


    # function to retrieve and set current spectrum
    def retrieve_and_set_current_spectrum(self):
        # get command parameters
        command_id = self.Commands[self.Get_current_spectrum][0]
        expected_answers = self.Commands[self.Get_current_spectrum][1]

        # send command
        self.send_command(command_id)

        # wait for integral time request
        self.wait_for_response(expected_answers[0])
        # send integral time
        self.send_command(str(self.integral_time))

        # checking that the integral time has been set and data has been received
        self.wait_for_response(expected_answers[1])
        # get data from response
        response = self.read_until_response(expected_answers[2])
        data = self.split_spectrometer_response(response, self.spectrum_len)
        # set current spectrum if we got
        if data is not None:
            self.current_spectrum = data
            # set new real current spectrum
            self.real_current_spectrum = self.current_spectrum - self.dark_spectrum

        # skip before next request
        self.wait_for_response(expected_answers[3])
        return self


    # function to clear dark spectrum
    def clear_dark_spectrum(self):
        self.dark_spectrum = np.zeros(self.spectrum_len)
        self.sub = False
        self.real_current_spectrum = self.current_spectrum - self.dark_spectrum


    # function return wavelength range
    def return_wavelength_range(self):
        return self.wavelength_range


    # function return dark spectrum
    def return_dark_spectrum(self):
        return self.dark_spectrum


    # function return current spectrum
    def return_current_spectrum(self):
        return self.current_spectrum


    # function return real current spectrum
    def return_real_current_spectrum(self):
        return self.real_current_spectrum


    # function return (wavelength range and real current spectrum)
    def return_wavelength_and_spectrum(self):
        return (self.wavelength_range, self.real_current_spectrum)


    # function return sub parameter
    def return_sub_parameter(self):
        return self.sub


    # function return sub parameter
    def return_sub_parameter_text(self):
        if self.sub:
            return "sub"
        else:
            return "no_sub"



if __name__ == "__main__":
    connection = SpectrometerConnection()
    connection.open_spectrometer()
