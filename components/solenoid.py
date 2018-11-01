#!/usr/bin/python

import RPi.GPIO as GPIO

class ValveManager(object):
    def __init__(self, pins):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.valve_controls = {}
        self.toggle_phase = "off"
        for pin in pins:
            self.valve_controls[pin] = ValveController(pin)

    def toggle_valves(self):
        if self.toggle_phase == "off":
            for pin in list(self.valve_controls.keys()):
                valve = self.valve_controls[pin]
                print("Toggling on valve: {}".format(valve.control_pin))
                valve.turn_on()
        else:
            for pin in list(self.valve_controls.keys()):
                valve = self.valve_controls[pin]
                print("Toggling off valve: {}".format(valve.control_pin))
                valve.turn_off()

class ValveController(object):
    def __init__(self, pin):
        self.control_pin = pin
        GPIO.setup(self.control_pin, GPIO.OUT)

    def turn_on(self):
        GPIO.output(self.control_pin, GPIO.HIGH)

    def turn_off(self):
        GPIO.output(self.control_pin, GPIO.LOW)
