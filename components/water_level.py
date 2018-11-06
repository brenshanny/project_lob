#!/usr/bin/python

import spidev

class WaterLevelManager(object):
    def __init__(self, pins):
        self.monitors = [WaterLevelMonitor(pin) for pin in pins]
        self.averages = {}
        for pin in pins:
            self.averages[pin] = []

    def read_levels(self):
        return [
            {
                "data": monitor.read_level(),
                "pin": monitor.pin,
                "average": monitor.get_average()
            }
            for monitor in self.monitors
        ]

    def print_levels(self):
        for monitor in self.monitors:
            print("Monitor {}, level: {}".format(
                monitor.pin, monitor.read_level()))

class WaterLevelMonitor(object):
    def __init__(self, pin):
        # We'll need the pin, the min/max readings for the desired sensor
        # and a way to differentiate the device for the spi.open command
        self.pin = pin
        self.setup_spi()
        self.samples = []

    def get_average(self):
        return sum(self.samples) / len(self.samples)

    def update_samples(self, sample):
        self.samples.append(sample)
        self.samples = self.samples[-10:]

    def setup_spi(self):
        self.spi = spidev.SpiDev()
        # this is (bus, device), so we'll need to differentiate from
        # other devices here
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1350000

    def read_raw(self):
        r = self.spi.xfer2([1, 8 << self._pin, 0])
        return ((r[1] & 3) << 8) + r[2]

    def read_level(self):
        data = self.read_raw()
        # we'll probably want to incorporate the min/max here to
        # provide a water level between 0 -> 1
        level = round(((data * 3300) / 1024), 0)
        self.update_samples(level)
        return level
