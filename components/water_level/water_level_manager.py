#!/usr/bin/python

import logging

from .water_level_monitor import WaterLevelMonitor

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

