#!/usr/bin/python

import spidev
import logging

class WaterLevelManager(object):
    def __init__(self, monitor_config, min_threshold, max_threshold):
        self.logger = logging.getLogger(
            "project_lob.components.water_level_manager")
        self.logger.info("Initializing Water Level Manager")
        self.monitors = [
            WaterLevelMonitor(
                cfg["pin"], cfg["tank"], cfg["min"],
                cfg["max"], min_threshold, max_threshold)
            for cfg in monitor_config
        ]
        self.averages = {}
        for monitor in self.monitors:
            self.averages[monitor.tank] = []

    def read_monitors(self):
        self.logger.info("Reading water levels")
        return [
            {
                "data": monitor.read_level(),
                "tank": monitor.tank,
                "pin": monitor.pin,
                "average": monitor.get_average()
            }
            for monitor in self.monitors
        ]

    def print_levels(self):
        self.logger.info("Printing water levels")
        for monitor in self.monitors:
            print("Monitor {}, level: {}".format(
                monitor.tank, monitor.read_level()))

class WaterLevelMonitor(object):
    def __init__(self, pin, tank, min_level, max_level, min_thresh, max_thresh):
        self.logger = logging.getLogger(
            "project_lob.components.water_level_monitor")
        self.logger.info("Initializing Water Level Monitor for "
                         "tank: {}".format(tank))
        # We'll need the pin, the min/max readings for the desired sensor
        # and a way to differentiate the device for the spi.open command
        self.pin = pin
        self.tank = tank
        self.setup_spi()
        self.samples = []
        self.avg_samples = []
        self.min_level = min_level
        self.max_level = max_level
        self.min_thresh = self.min_level * min_thresh
        self.max_thresh = self.max_level * max_thresh
        self.target_level = (
            self.max_level - ((self.max_level - self.min_level) / 2)
        )

    def get_average(self, log = False):
        if not (len(self.samples) > 0):
            self.read_level()
        avg = sum(self.samples) / len(self.samples)
        if log:
            self.logger.info("Water level average is {} for tank {}".format(
                avg, self.tank))
        return avg

    def check_alert(self):
        last_sample = self.last_sample()
        if last_sample <= self.min_thresh:
            return ("Low water warning for tank {}! Level is currently {}, "
                    "minimum level is {}".format(
                        self.tank, last_sample, self.min_level))
        elif last_sample >= self.max_thresh:
            return ("High water warning for tank {}! Level is currently {}, "
                    "max level is {}".format(
                        self.tank, last_sample, self.max_level))
        else:
            return False

    def level_direction(self):
        return self.samples[0] - self.samples[-1]

    def last_sample(self):
        return self.samples[-1]

    def last_average(self):
        return self.avg_samples[-1]

    def raw_offset(self):
        return (self.get_average() - self.target_level)

    def target_offset(self):
        return (self.raw_offset() / (self.target_level - self.min_level))

    def update_samples(self, sample):
        self.logger.info("Updating samples for tank: {} with level "
                         "sample: {}".format(self.tank, sample))
        self.samples.append(sample)
        self.samples = self.samples[-10:]
        self.avg_samples.append(self.get_average())
        self.avg_samples = self.avg_samples[-10:]

    def setup_spi(self):
        self.logger.info("Setting up SPI for tank: {}".format(self.tank))
        self.spi = spidev.SpiDev()
        # this is (bus, device), so we'll need to differentiate from
        # other devices here
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1350000

    def read_raw(self):
        r = self.spi.xfer2([1, 8 << self.pin, 0])
        return ((r[1] & 3) << 8) + r[2]

    def read_level(self):
        self.logger.info("Reading levels for tank: {}".format(self.tank))
        data = self.read_raw()
        # we'll probably want to incorporate the min/max here to
        # provide a water level between 0 -> 1
        level = round(((data * 3300) / 1024), 0)
        self.update_samples(level)
        return level
