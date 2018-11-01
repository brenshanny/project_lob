#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys

class WaterFlowManager(object):
    def __init__(self, pins):
        # setup the water monitors for each pin
        # We'll likely want to have some dict to know which montior goes
        # to which tank
        self.water_monitors = [WaterFlowMonitor(pin) for pin in pins]

    def read_monitors(self):
        return [
            {readings: monitor.calc_flow(), pin: monitor.flow_sensor_pin}
            for monitor in self.water_monitors
        ]

    def print_flows(self):
        for monitor in self.water_monitors:
            print("Flow Monitor: {}".format(monitor.flow_sensor_pin))
            print(monitor.calc_flow)

    def reset_monitors(self):
        for monitor in self.water_monitors:
            monitor.reset_counters()

# This is the class that will handle the water flow for a single sensor
class WaterFlowMonitor(object):
    def __init__(self, pin):
        # Set the sensor pin
        self.flow_sensor_pin = pin
        # The constant is how often we are measuring the water flow
        # currently it is set to every 10 seconds
        self.constant = 0.10
        # Set the defaults
        self.reset_counters()
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.flow_sensor_pin, GPIO.IN, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(
                self.flow_sensor_pin,
                GPIO.FALLING,
                callback=self.count_pulse
                )

    def reset_counters(self):
        self.total_count = 0
        self.rate_count = 0
        self.timer = 0
        self.min_count = 0

    def reset_rate_count(self):
        self.rate_count = 0

    def reset_timer(self, increment = 0):
        self.timer = time.time() + increment

    def count_pulse(self, channel):
        self.total_count += 1
        self.rate_count += 1

    def calc_flow(self, reset_timer = False):
        liters = round(self.rate_count * self.constant, 4)
        total = round(self.total_count * self.constant, 4)
        # logging here
        print('Liters/min -> ', liters)
        print('Total Liters -> ', total)
        if reset_timer:
            self.reset_rate_count()
            self.reset_timer(10)
        return [liters, total]

    def shut_down(self):
        GPIO.cleanup()

    def run(self):
        self.reset_timer(10)
        # We'll want to setup logging here
        print("Running WaterFlowMonitor")
        while True:
            try:
                if time.time() >= self.timer:
                    self.min_count += 1
                    self.calc_flow(True)
                time.sleep(1)
            # Likely will need a different shut down call
            except KeyboardInterrupt:
                print('Shutting down...')
                self.shut_down()
