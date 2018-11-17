#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys
import logging

class WaterFlowManager(object):
    def __init__(self, config):
        # setup the water monitors for each pin
        # We'll likely want to have some dict to know which montior goes
        # to which tank
        self.logger = logging.getLogger(
            "project_lob.components.water_flow_manager")
        self.logger.info("Initializing Water Flow Manager")
        self.monitors = [
            WaterFlowMonitor(cfg["pin"], cfg["tank"]) for cfg in config
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

# This is the class that will handle the water flow for a single sensor
class WaterFlowMonitor(object):
    def __init__(self, pin, tank):
        self.logger = logging.getLogger(
            "project_lob.components.water_flow_monitor")
        self.logger.info("Initializing Water Flow Monitor for tank: "
                         "{}".format(tank))
        # Set the sensor pin and tank
        self.pin = pin
        self.tank = tank
        # The constant is how often we are measuring the water flow
        # currently it is set to every 10 seconds
        self.constant = 0.10
        # Set the defaults
        self.reset_counters()
        self.samples = []
        self.target_flow = None
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(
                self.pin,
                GPIO.FALLING,
                callback=self.count_pulse
                )

    def get_average(self, log = False):
        avg = sum(self.samples) / len(self.samples)
        if log:
            self.logger.info("Water flow average is {} for pin: {}".format(
                avg, self.pin))
        return avg

    def target_offset(self):
        if not self.target_flow:
            return 0
        else:
            return (self.target_flow - self.get_average()) / self.target_flow

    def set_target_flow(self, target):
        self.target_flow = target

    def update_samples(self, sample):
        self.logger.info("Updating samples for tank: {} with sample "
                         "flow: {}".format(self.tank, sample))
        self.samples.append(sample)
        self.samples = self.samples[-10:]

    def reset_counters(self):
        self.logger.info("Resetting counters for tank {}".format(self.tank))
        self.total_count = 0
        self.rate_count = 0
        self.timer = 0
        self.min_count = 0

    def reset_rate_count(self):
        self.rate_count = 0

    def reset_timer(self, increment = 0):
        self.logger.info("Resetting timer for tank {}".format(self.tank))
        self.timer = time.time() + increment

    def count_pulse(self, channel):
        self.total_count += 1
        self.rate_count += 1

    def calc_flow(self, reset_timer = False):
        self.logger.info("Calculating flow for tank: {}".format(self.tank))
        liters = round(self.rate_count * self.constant, 4)
        total = round(self.total_count * self.constant, 4)
        self.update_samples(liters)
        # logging here
        print('Liters/min -> ', liters)
        print('Total Liters -> ', total)
        if reset_timer:
            self.reset_rate_count()
            self.reset_timer(10)
        return [liters, total]

    def shut_down(self):
        self.logger.info("Shutting down Water Flow Monitor for "
                         "tank: {}".format(self.tank))
        GPIO.cleanup()

    def run(self):
        self.logger.info("Running Water Flow Monitor for "
                         "tank: {}".format(self.tank))
        self.reset_timer(10)
        # We'll want to setup logging here
        while True:
            try:
                if time.time() >= self.timer:
                    self.min_count += 1
                    self.calc_flow(True)
                time.sleep(1)
            # Likely will need a different shut down call
            except KeyboardInterrupt:
                self.shut_down()
