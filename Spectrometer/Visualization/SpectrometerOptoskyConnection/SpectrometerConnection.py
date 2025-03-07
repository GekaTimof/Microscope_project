import os
import sys
import pexpect
import numpy as np

from Constants import Spectrometer_directory_path, Spectrometer_name, Accumulation_time, X_len, Y_len
from Constants import OptoskySpectrometerCommands, Command_open_spectrometer, Command_get_wavelength_range, Command_get_dark_spectrum, Command_get_current_spectrum

# class that contain spectrometer connection
class SpectrometerConnection:
    def __init__(self):
        # set dict os spectrometer commands
        # {"key": ("id", [response_1, response_2, ...])}
        self.Commands = OptoskySpectrometerCommands

        # set spectrometer commands
        self.Open_spectrometer = Command_open_spectrometer
        self.Get_wavelength_range = Command_get_wavelength_range
        self.Get_dark_spectrum = Command_get_dark_spectrum
        self.Get_current_spectrum = Command_get_current_spectrum

        # set directories
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
        self.child = pexpect.spawn(f'{self.spectrometer_path}', cwd=self.working_directory, encoding="utf-8", timeout=10)

        # try:
        #     # read output before "Enter :" appears
        #     self.child.expect("Enter :", timeout=5)
        #     print("Connection was success")
        # except:
        #     raise Exception("No answer from spectrometer. (Check spectrometer connection, check spectrometer script access rights")
        #     # TODO add correct Exception

        # set start accumulation time
        self.accumulation_time: int = Accumulation_time
        # set X coordinates length
        self.x_len: int = X_len
        # set Y coordinates length
        self.y_len: int = Y_len



    # function return spectrometer working_directory
    def get_working_directory(self):
        return self.working_directory


    # function return spectrometer accumulation time
    def get_accumulation_time(self):
        return self.accumulation_time


    # function set spectrometer accumulation time
    def set_accumulation_time(self, accumulation_time: int):
        if accumulation_time > 0:
            self.accumulation_time = accumulation_time
        else:
            raise Exception(f"an able to set accumulation_time = {accumulation_time}")
            # TODO add correct Exception


    # # function send one command to spectrometer
    # def send_command(self, command: str, expect_answer: str):
    #     try:
    #         # send command
    #         self.child.sendline("0")
    #         # wait for answer
    #         self.child.expect(f"{expect_answer}", timeout=5)
    #         print(f"{command} command was success")
    #     except:
    #         raise Exception(f"No answer from spectrometer for {command} command")
    #         # TODO add correct Exception


    # # function send one command to spectrometer and return entire text up to expect_answer
    # def send_command_with_response(self, command: str, expect_answer: str):
    #     try:
    #         # send command
    #         self.child.sendline("0")
    #         # wait for answer
    #         self.child.expect(f"{expect_answer}", timeout=5)
    #         data = self.child.before
    #         print(f"{command} command was success")
    #         return data
    #     except:
    #         raise Exception(f"No answer from spectrometer for {command} command")
    #         # TODO add correct Exception


    # function send one command to spectrometer
    def send_command(self, command: str):
        self.child.sendline(command)
        print(f"command - '{command}' has been sent")
        return self


    # function trying to find expect_answer in spectrometer text flow
    def wait_for_response(self,  expect_answer: str, waiting_time: int = 5):
        try:
            # wait for answer
            self.child.expect(f"{expect_answer}", timeout=waiting_time)
            print(f"answer - '{expect_answer}' was received")
        except:
            raise Exception(f"No answer '{expect_answer}' from spectrometer")
            # TODO add correct Exception


    # function trying to find expect_answer in spectrometer text flow and return all test before it
    def read_response_before(self,  expect_answer: str, waiting_time: int = 5):
        # wait for answer
        self.wait_for_response(expect_answer, waiting_time=waiting_time)

        # get response
        data = self.child.before
        return data


    # function to connect to spectrometer
    def open_spectrometer(self):
        # try to connect
        self.send_command(self.Commands[self.Open_spectrometer][0])
        # check connection
        self.wait_for_response(self.Commands[self.Open_spectrometer][1][0])
        # skip Optosky specification
        self.wait_for_response(self.Commands[self.Open_spectrometer][1][1])
        return self




if __name__ == "__main__":
    connection = SpectrometerConnection()
    connection.open_spectrometer()
