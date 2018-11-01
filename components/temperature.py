#!/usr/bin/python

# TemperatureMonitor based of code written by Adaftuit
# Modified by Brendan Shanny 2018
# https://learn.adafruit.com/
# adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software

import os
import glob
import time

class TemperatureManager(object):
    def __init__(self, ids):
        # We need to setup 4 different temperature monitors here
        # each will be coded with a specific folder to access
        # We'll likely want to pass in the folder id's
        self.temp_monitors = [TemperatureMonitor(id) for id in ids]

    def read_monitors(self):
        return [
            {readings: monitor.read_temp(), device_id: monitor.device_id}
            for monitor in self.temp_monitors
        ]

    def print_temps(self):
        for monitor in self.temp_monitors:
            print("Temp monitor: {}".format(monitor.device_id))
            [c, f] = monitor.read_temp()
            print("C: {}, F: {}".format(c, f))

class TemperatureMonitor(object):
    def __init__(self, device_id):
        self.device_id = device_id
        # Find the correct folder with the device id
        self.device_folder = glob.glob('/sys/bus/w1/devices/' + '28*')[0]
        self.device_file = self.device_folder + '/w1_slave'

    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        # is this an efficient way to read the data from multiple sources?
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f
