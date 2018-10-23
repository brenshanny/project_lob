#!/usr/bin/python

import spidev

class WaterLevelManager(object):
    def __init__(self, pins):
        self.water_monitors = [WaterLevelMonitor(pin) for pin in pins]

    def read_levels(self):
        return [
            { level: monitor.read_level(), pin: monitor.sensor_pin }
            for monitor in self.water_monitors
        ]

class WaterLevelMonitor(object):
    def __init__(self, pin):
        # We'll need the pin, the min/max readings for the desired sensor
        # and a way to differentiate the device for the spi.open command
        self.sensor_pin = pin
        self.setup_spi()

    def setup_spi(self):
        self.spi = spidev.SpiDev()
        # this is (bus, device), so we'll need to differentiate from
        # other devices here
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 1350000

    def read_raw(self):
        r = spi.xfer2([1, 8 << self.sensor_pin, 0])
        return ((r[1] & 3) << 8) + r[2]

    def read_level(self):
        data = self.read_raw()
        # we'll probably want to incorporate the min/max here to
        # provide a water level between 0 -> 1
        return round(((data * 3300) / 1024), 0)
