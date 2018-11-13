#!/usr/bin/python

# TemperatureMonitor based of code written by Adaftuit
# Modified by Brendan Shanny 2018
# https://learn.adafruit.com/
# adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software

import os
import glob
import time
import logging

class TemperatureManager(object):
    def __init__(self, ids):
        self.logger = logging.getLogger(
            "project_lob.components.temperature_manager")
        self.logger.info("Initializing Temperature Manger")
        self.temp_monitors = [TemperatureMonitor(t_id) for t_id in ids]
        self.averages = {}
        for t_id in ids:
            self.averages[t_id] = []

    def read_monitors(self):
        self.logger.info("Reading temperatures")
        return [
            {
                "data": monitor.read_temp(),
                "device_id": monitor.device_id,
                "average": monitor.get_average()
            }
            for monitor in self.temp_monitors
        ]

    def print_temps(self):
        self.logger.info("Printing temperatures")
        for monitor in self.temp_monitors:
            print("Temp monitor: {}".format(monitor.device_id))
            [c, f] = monitor.read_temp()
            print("C: {}, F: {}".format(c, f))

class TemperatureMonitor(object):
    def __init__(self, device_id):
        self.logger = logging.getLogger(
            "project_lob.components.temperature_monitor")
        self.logger.info("Initializing Temperature Monitor for device: "
                         "{}".format(device_id))
        self.device_id = device_id
        # Find the correct folder with the device id
        self.device_folder = glob.glob('/sys/bus/w1/devices/' + '28*')[0]
        self.device_file = self.device_folder + '/w1_slave'
        self.samples= []

    def get_average(self):
        avg = sum(self.samples) / len(self.samples)
        self.logger.info("Average is {}, for device: {}".format(
            avg, self.device_id))
        return avg
    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def update_samples(self, sample):
        self.logger.info("Updating Samples with temp: {}".format(sample))
        self.samples.append(sample)
        self.samples = self.samples[-10:]

    def read_temp(self):
        self.logger.info("Reading temp for device: {}".format(self.device_id))
        lines = self.read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            self.update_samples(temp_c)
            return temp_c, temp_f
