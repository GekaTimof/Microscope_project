import os
import sys
import pexpect
import numpy as np

from SpectrometerOptoskyConnection import Spectrometer_directory_path, Spectrometer_name, Integral_time, Wavelength_range_len, Spectrum_len
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
        self.integral_time: int = Integral_time

        # set wavelength len and empty wavelength array
        self.wavelength_range_len: int = Wavelength_range_len
        self.wavelength_range = np.zeros(self.wavelength_range_len)

        # set spectrum len and empty spectrum array
        self.spectrum_len: int = Spectrum_len
        self.dark_spectrum = np.zeros(self.spectrum_len)
        self.current_spectrum = np.zeros(self.spectrum_len)
        self.real_current_spectrum = np.zeros(self.spectrum_len)

        # find directories
        base_dir = os.path.dirname(os.path.abspath(__file__))
        script_dir = os.path.dirname(base_dir)
        project_dir = os.path.dirname(script_dir)

        # set working directory
        self.working_directory = os.path.join(project_dir, Spectrometer_directory_path)
        if not os.path.exists(self.working_directory):
            raise FileNotFoundError(f"Spectrometer directory not found: {self.working_directory}")

        # set path to spectrometer script
        self.spectrometer_path = os.path.join(self.working_directory, Spectrometer_name)
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
            self.process.expect(f"{expect_answer}", timeout=waiting_time)
            print(f"answer - '{expect_answer}' was received")
        except:
            raise Exception(f"No answer '{expect_answer}' from spectrometer")
            # TODO add correct Exception


    # function trying to find expect_answer in spectrometer text flow and return all test before it
    def read_until_response(self,  expect_answer: str, waiting_time: int = 5):
        # wait for answer
        self.wait_for_response(expect_answer, waiting_time=waiting_time)

        # get response
        data = self.process.before
        return data


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


    # function to get and set wavelength range
    def  get_wavelength_range(self):
        # get command parameters
        command_id = self.Commands[self.Get_wavelength_range][0]
        expected_answers = self.Commands[self.Get_wavelength_range][1]

        # send command
        self.send_command(command_id)

        # checking that the wavelength range has been received
        self.wait_for_response(expected_answers[0])
        # get data from response
        data = self.read_until_response(expected_answers[1])
        # TODO set wavelength_range

        # skip before next request
        self.wait_for_response(expected_answers[2])
        return self


    # function to get and set dark spectrum
    def  get_dark_spectrum(self):
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
        data = self.read_until_response(expected_answers[2])
        # TODO set dark_spectrum

        # skip before next request
        self.wait_for_response(expected_answers[3])
        return self


    # function to get and set current spectrum
    def  get_current_spectrum(self):
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
        data = self.read_until_response(expected_answers[2])
        # TODO set current_spectrum
        # TODO set real_current_spectrum (real spectrum - dark spectrum)

        # skip before next request
        self.wait_for_response(expected_answers[3])
        return self


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


if __name__ == "__main__":
    connection = SpectrometerConnection()
    connection.open_spectrometer()
