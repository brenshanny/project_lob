#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys
import logging

from .water_flow_monitor import WaterFlowMonitor

class WaterFlowManager(object):
    def __init__(self, config, update_interval):
        # setup the water monitors for each pin
        # We'll likely want to have some dict to know which montior goes
        # to which tank
        self.logger = logging.getLogger(
            "project_lob.components.water_flow_manager")
        self.logger.info("Initializing Water Flow Manager")
        self.monitors = [
            WaterFlowMonitor(cfg["pin"], cfg["tank"], update_interval)
            for cfg in config
        ]
        self.averages = {}
        for monitor in self.monitors:
            self.averages[monitor.tank] = []

    def read_monitors(self):
        self.logger.info("Reading water flow monitors")
        return [
            {
                "data": monitor.calc_flow(),
                "tank": monitor.tank,
                "pin": monitor.pin,
                "average": monitor.get_average()
            }
            for monitor in self.monitors
        ]

    def print_flows(self):
        self.logger.info("Printing water flow readings")
        for monitor in self.monitors:
            print("Flow Monitor: {}".format(monitor.tank))
            print(monitor.calc_flow())

    def reset_monitors(self):
        self.logger.info("Resetting water flow monitors")
        for monitor in self.monitors:
            monitor.reset_counters()
