#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import logging

# This is the class that will handle the water flow for a single sensor
class WaterFlowMonitor(object):
    def __init__(self, pin, tank, update_interval):
        self.logger = logging.getLogger(
            "project_lob.components.water_flow_monitor")
        self.logger.info("Initializing Water Flow Monitor for tank: "
                         "{}".format(tank))
        # Set the sensor pin and tank
        self.pin = pin
        self.tank = tank
        # The constant is how often we are measuring the water flow
        self.constant = update_interval / 100.00
        # Set the defaults
        self.reset_counters()
        self.samples = []
        self.avg_samples = []
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

    def last_sample(self):
        return self.samples[-1]

    def last_average(self):
        return self.avg_samples[-1]

    def target_offset(self):
        if not self.target_flow:
            return 0
        else:
            return (self.target_flow - self.get_average()) / self.target_flow

    def set_target_flow(self, target):
        self.target_flow = target

    def update_samples(self, sample):
        self.logger.info("Updating samples for tank: {} with "
                         "flow: {}".format(self.tank, sample))
        self.samples.append(sample)
        self.samples = self.samples[-10:]
        self.avg_samples.append(self.get_average())
        self.avg_samples = self.avg_samples[-10:]

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
