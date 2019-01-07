#!/usr/bin/python

import logging

from .temperature_monitor import TemperatureMonitor

class TemperatureManager(object):
    """
    An object to manage multiple TemperatureMonitors.
    Required arguments:
        config: List containing dicts of temperature probe info
                ex: [ { "device_id": "some_device_id", "tank": 1 } ]
    """
    def __init__(self, config):
        self.logger = logging.getLogger(
            "project_lob.components.temperature_manager")
        self.logger.info("Initializing Temperature Manger")
        self.monitors = [
            TemperatureMonitor(cfg["device_id"], cfg["tank"]) for cfg in config
        ]
        self.averages = {}
        for monitor in self.monitors:
            self.averages[monitor.tank] = []

    def read_monitors(self):
        """
        Construct and return a list of temperature readings from each
        TemperatureMonitor
        """
        self.logger.info("Reading temperatures")
        return [
            {
                "data": monitor.read_temp(),
                "device_id": monitor.device_id,
                "tank": monitor.tank,
                "average": monitor.get_average()
            }
            for monitor in self.monitors
        ]

    def print_temps(self):
        """
        Print out the current temperature for each TemperatureMonitor
        """
        self.logger.info("Printing temperatures")
        for monitor in self.monitors:
            print("Temp monitor: {}".format(monitor.tank))
            [c, f] = monitor.read_temp()
            print("C: {}, F: {}".format(c, f))
