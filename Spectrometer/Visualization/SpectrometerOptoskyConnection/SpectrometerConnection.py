import os
import sys
import pexpect
import numpy as np

from Constants import Spectrometer_directory_path, Spectrometer_name


class SpectrometerConnection():
    def __init__(self):
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

        # check first connection
        try:
            # read output before "Enter :" appears
            self.child.expect("Enter :", timeout=5)
            print("Connection was success")
        except:
            raise Exception("No answer from spectrometer. (Check spectrometer connection, check spectrometer script access rights")
            # TODO add correct Exception


    # function return spectrometer working_directory
    def get_working_directory(self):
        return str(self.working_directory)


    # function send one command to spectrometer
    def send_command(self, command: str, expect_answer: str):
        try:
            # send command
            self.child.sendline("0")
            # wait for answer
            self.child.expect(f"{expect_answer}", timeout=5)
            print(f"{command} command was success")
        except:
            raise Exception(f"No answer from spectrometer for {command} command")
            # TODO add correct Exception

    # function send one command to spectrometer and return entire text up to expect_answer
    def send_command_with_response(self, command: str, expect_answer: str):
        try:
            # send command
            self.child.sendline("0")
            # wait for answer
            self.child.expect(f"{expect_answer}", timeout=5)
            data = self.child.before
            print(f"{command} command was success")
            return data
        except:
            raise Exception(f"No answer from spectrometer for {command} command")
            # TODO add correct Exception


if __name__ == "__main__":
    connection = SpectrometerConnection()
    print(connection.get_working_directory())
    connection.send_command("0", "success!")
    connection.send_command("0", "Enter :")
    print(connection.send_command_with_response("23", "Enter :"))