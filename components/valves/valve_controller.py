#!/usr/bin/python

import RPi.GPIO as GPIO
import logging


class ValveController(object):
    def __init__(self, pin, tank):
        self.logger = logging.getLogger(
            "project_lob.components.valve_controller")
        self.logger.info("Setting up Valve Controller for tank: {}".format(tank))
        self.pin = pin
        self.tank = tank
        GPIO.setup(self.pin, GPIO.OUT)

    def turn_on(self):
        self.logger.info("Turning valve tank: {} ON".format(self.tank))
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_off(self):
        self.logger.info("Turning valve tank: {} OFF".format(self.tank))
        GPIO.output(self.pin, GPIO.LOW)
