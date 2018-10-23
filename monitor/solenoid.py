#!/usr/bin/python

class ValveManager(object):
    def __init__(self, pins):
        self.valve_controls = {}
        for pin in pins:
            self.valve_controls[pin] = ValveController(pin)

class ValveController(object):
    def __init__(self, pin):
        self.control_pin = pin
