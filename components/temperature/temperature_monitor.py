#!/usr/bin/python

# TemperatureMonitor based of code written by Adaftuit
# Modified by Brendan Shanny 2018
# https://learn.adafruit.com/
# adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing/software


import glob
import time
import logging

class TemperatureMonitor(object):
    def __init__(self, device_id, tank):
        self.logger = logging.getLogger(
            "project_lob.components.temperature_monitor")
        self.logger.info("Initializing Temperature Monitor for device: "
                         "{}".format(tank))
        self.device_id = device_id
        self.tank = tank
        # Find the correct folder with the device id
        self.device_folder = glob.glob('/sys/bus/w1/devices/' + '28*')[0]
        self.device_file = self.device_folder + '/w1_slave'
        self.samples= []

    def get_average(self):
        avg = sum(self.samples) / len(self.samples)
        self.logger.info("Average temp is {}, for tank: {}".format(
            avg, self.tank))
        return avg

    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def last_sample(self):
        return self.samples[-1]

    def update_samples(self, sample):
        self.logger.info("Updating Samples with temp: {}".format(sample))
        self.samples.append(sample)
        self.samples = self.samples[-10:]

    def read_temp(self):
        self.logger.info("Reading temp for tank: {}".format(self.tank))
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
